import pickle
from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:
    name: str

    def community(self, community_id: str, name: str):
        return PlatformCommunity(platform=self, id=community_id, name=name)

    def contact(self):
        return PlatformContact(self)


@dataclass(frozen=True, kw_only=True)
class PlatformCommunity:
    platform: Platform
    id: str
    name: str


@dataclass()
class PlatformContact:
    _EMPTY_SET = frozenset()

    platform: Platform
    names: set[str] = _EMPTY_SET
    phones: set[str] = _EMPTY_SET
    communities: set[PlatformCommunity] = _EMPTY_SET
    personal: bool = False

    def __init__(self, platform: Platform):
        self.platform = platform

    def add_name(self, name: str):
        if len(self.names) == 0:
            self.names = {name}
        else:
            self.names.add(name)

    def add_phone(self, phone: str):
        if len(self.phones) == 0:
            self.phones = {phone}
        else:
            self.phones.add(phone)

    def add_community(self, community: PlatformCommunity):
        if len(self.communities) == 0:
            self.communities = {community}
        else:
            self.communities.add(community)


class Contact:
    platforms: dict[Platform, PlatformContact]
    names: set[str]
    communities: set[PlatformCommunity]
    personal: bool = False

    def __init__(self):
        self.platforms = {}
        self.names = set()
        self.communities = set()


def save_pickled(obj: object, file: str):
    with open(file, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_pickled(file: str):
    with open(file, 'rb') as f:
        return pickle.load(f)
