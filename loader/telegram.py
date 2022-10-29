import asyncio
import pickle
from dataclasses import dataclass
from typing import Optional, Union, Dict
from telethon import TelegramClient
from telethon.tl.types import User, Channel
from telethon.errors import ChatAdminRequiredError
from configparser import ConfigParser
from os import path
from getpass import getpass

from data import PlatformContact, Platform, save_pickled

_DEFAULT_CONFIG_FILE = path.join(__package__, 'telegram.ini')
PLATFORM = Platform("Telegram")


@dataclass(kw_only=True)
class Credentials:
    api_id: int
    api_hash: str
    phone: Optional[str] = None
    password: Optional[str] = None


class TelegramLoader:
    _credentials: Optional[Credentials] = None
    _client: Optional[TelegramClient] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        if self._client is None:
            return
        await self._client.disconnect()

    def load_credentials(self, ini_path: str = _DEFAULT_CONFIG_FILE):
        config = ConfigParser()
        config.read(ini_path)
        telegram = config['Telegram']
        creds = Credentials(
            api_id=int(telegram['api_id']),
            api_hash=telegram['api_hash'])
        if 'phone' in telegram:
            creds.phone = telegram['phone']
        if 'password' in telegram:
            creds.password = telegram['password']
        self._credentials = creds

    async def connect(self):
        if self._client is not None:
            return
        if self._credentials is None:
            raise Exception('Missing config')
        client = TelegramClient(
            'Friends Graph Scraper',
            self._credentials.api_id,
            self._credentials.api_hash,
            device_model='Scraper',
            app_version='1.0',
            receive_updates=False
        )

        def get_phone():
            if self._credentials.phone is None:
                self._credentials.phone = input('Please enter your phone (or bot token): ')
            return self._credentials.phone

        def get_password():
            passwd = self._credentials.password or getpass('Please enter your password: ')
            self._credentials.password = None
            return passwd

        await client.start(phone=get_phone, password=get_password)

        self._client = client

    async def get_contacts(self) -> list[PlatformContact]:
        if self._client is None:
            raise Exception('Not connected')

        users: Dict[int, PlatformContact] = dict()

        def add_user(user: User) -> PlatformContact:
            if user.id not in users:
                contact = PLATFORM.contact()
                if user.first_name is not None and not user.first_name.isspace():
                    contact.add_name(user.first_name)
                    if user.last_name is not None and not user.last_name.isspace():
                        contact.add_name(f"{user.first_name} {user.last_name}")
                if user.phone is not None:
                    contact.add_phone(user.phone)
                users[user.id] = contact
                return contact
            else:
                return users[user.id]

        async for dialog in self._client.iter_dialogs():
            entity: Union[User, Channel] = dialog.entity
            if isinstance(entity, User):
                add_user(entity).personal = True

            elif isinstance(entity, Channel):
                channel: Channel = entity
                community = PLATFORM.community(str(channel.id), channel.title)
                try:
                    async for user in self._client.iter_participants(channel):
                        add_user(user).add_community(community)
                except ChatAdminRequiredError:
                    pass
        return [users[uid] for uid in users]


async def _main():
    if not path.isfile(_DEFAULT_CONFIG_FILE):
        print('No config found at', _DEFAULT_CONFIG_FILE)
        exit(1)

    async with TelegramLoader() as loader:
        loader.load_credentials()
        await loader.connect()
        contacts = await loader.get_contacts()

    save_pickled(contacts, 'telegram.pickle')
    print('saved data to ./telegram.pickle')

if __name__ == '__main__':
    asyncio.run(_main())
