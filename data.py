import pickle
from dataclasses import dataclass
from typing import TypeVar


@dataclass(frozen=True)
class Platform:
    name: str

    def community(self, community_id: str, name: str, *, personal: bool):
        return PlatformCommunity(platform=self, id=community_id, name=name, personal=personal)

    def contact(self):
        return PlatformContact(self)


@dataclass(frozen=True, kw_only=True)
class PlatformCommunity:
    platform: Platform
    id: str
    name: str
    personal: bool = False


T = TypeVar('T')


@dataclass()
class PlatformContact:
    _EMPTY_SET = frozenset()
    _CACHE = dict()

    platform: Platform
    names: frozenset[str] = _EMPTY_SET
    phones: frozenset[str] = _EMPTY_SET
    communities: frozenset[PlatformCommunity] = _EMPTY_SET
    personal: bool = False

    def __init__(self, platform: Platform):
        self.platform = platform

    @classmethod
    def _get_cached(cls, s: frozenset[T] | T) -> frozenset[T]:
        if s in cls._CACHE:
            return cls._CACHE[s]
        v: frozenset[str] = s if isinstance(s, frozenset) else frozenset({s})
        cls._CACHE[s] = v
        return v

    def add_name(self, name: str):
        if len(self.names) == 0:
            self.names = PlatformContact._get_cached(name)
        else:
            self.names = PlatformContact._get_cached(self.names | {name})

    def add_phone(self, phone: str):
        if len(self.phones) == 0:
            self.phones = PlatformContact._get_cached(phone)
        else:
            self.phones = PlatformContact._get_cached(self.phones | {phone})

    def add_community(self, community: PlatformCommunity):
        if len(self.communities) == 0:
            self.communities = PlatformContact._get_cached(community)
        else:
            self.communities = PlatformContact._get_cached(self.communities | {community})


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
