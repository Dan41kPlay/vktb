from collections.abc import Collection, Iterable, Sequence
from dataclasses import dataclass, field, fields, asdict, astuple
from datetime import datetime
from math import inf
from os import makedirs
from os.path import exists
from pathlib import Path
from random import shuffle
from secrets import choice
from string import ascii_letters, digits
from typing import Any, Literal, Self, Type

from dacite import from_dict
from ujson import dumps, loads, JSONDecodeError

from .config import *
from .functions import *
from libs.vk_api_fast.keyboard import VkKeyboard


__all__ = ['botPrefs', 'DictLikeClass', 'BotPrefs', 'VersionInfo', 'Users', 'BaseUser']


@dataclass
class VersionInfo:
    full: str = f'1.0.0indev03.00 (000000.0-0300.{datetime.now():{Constants.DateTimeForms.forVersion}})'
    name: str = 'Release'
    changelog: str = (
        '\n\n❕1.0.0r'
        '➕Initial release'
    )

    def __post_init__(self):
        self.main = '.'.join(self.full.split('.')[:2])


@dataclass(slots=True)
class DictLikeClass(Collection):
    def get(self, field_: str):
        return getattr(self, field_)

    def set(self, field_: str, value: Any) -> None:
        setattr(self, field_, value)

    def inc(self, field_: str) -> None:
        setattr(self, field_, self.get(field_) + 1)

    @property
    def fields(self) -> list[str]:
        return [field_.name for field_ in fields(self)]

    @property
    def values(self) -> list[Any]:
        return [getattr(self, field_.name) for field_ in fields(self)]

    @property
    def toDict(self) -> dict[str, Any]:
        return asdict(self)

    def toFile(self, file_path: Path | str) -> None:
        with open(file_path, 'w') as file:
            file.write(dumps(self.toDict, indent=4, escape_forward_slashes=False))

    @classmethod
    def fromDict(cls, dictionary: dict[str, Any]) -> Self:
        return from_dict(cls, dictionary)

    @classmethod
    def fromFile(cls, file_path: Path | str) -> Self:
        if not exists(file_path):
            return cls()
        try:
            with open(file_path) as f:
                return cls.fromDict(loads(f.read()))
        except JSONDecodeError:
            return cls()

    def __contains__(self, item: Any):
        return item in {field_ for field_, _ in self}

    def __len__(self):
        return len(fields(self))

    def __iter__(self):
        yield from ((field_.name, getattr(self, field_.name)) for field_ in fields(self))


@dataclass(slots=True)
class Exercise(DictLikeClass):
    ...


@dataclass(slots=True)
class BotPrefs(DictLikeClass):
    ...


botPrefs = BotPrefs.fromFile(Database.botPrefsFilePath)
_botPrefs = BotPrefs()


@dataclass(slots=True)
class BaseUser(DictLikeClass):
    id: int = 0
    firstName: str = ''
    lastName: str = ''
    gender: int = 0


class Users(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def toDict(self) -> dict[str, Any]:
        return {userIdStr_: userClass.toDict for userIdStr_, userClass in self.items()}

    def toFile(self, file_path: Path | str = Database.usersFilePath) -> None:
        with open(file_path, 'w') as file:
            file.write(dumps(self.toDict, indent=4, escape_forward_slashes=False))

    @classmethod
    def fromDict(cls, dictionary: dict[str, Any], user_class: Type[BaseUser] = BaseUser) -> Self:
        return cls({userIdStr_: user_class.fromDict(userDict) for userIdStr_, userDict in dictionary.items()})

    @classmethod
    def fromFile(cls, file_path: Path | str = Database.usersFilePath, user_class: Type[BaseUser] = BaseUser) -> Self:
        if not exists(Database.reserveCopyFolderPath):
            makedirs(Database.reserveCopyFolderPath)
        if not exists(file_path):
            with open(file_path, 'w') as file:
                file.write('{}')
        try:
            with open(file_path) as file:
                return cls.fromDict(loads(file.read()), user_class)
        except JSONDecodeError:
            return cls()
