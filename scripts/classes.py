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
from typing import Any, Literal, override, Self, Type

from dacite import from_dict
from ujson import dumps, loads, JSONDecodeError

from .config import *
from .functions import *
from libs.vk_api_fast.keyboard import VkKeyboard


__all__ = ['botPrefs', 'DictLikeClass', 'BotPrefs', 'VersionInfo', 'Users', 'BaseUser']


@dataclass
class VersionInfo:
    full: str = f'1.42.1.17r (420117.3-0000.{datetime.now():{Constants.DateTimeForms.forVersion}})'
    name: str = 'The Subscription Update'
    changelog: str = (
        '\n\n❕1.42.1r'
        '\n➕Добавлено больше вариантов кастомизации количества сообщений, выводящихся в консоль'
        '\n♻️Python обновлён до версии 3.12.1'
        '\n\n❕1.42r'
        '\n➕Добавлена система подписок'
        '\n♻️Изменён принцип работы с настройками бота'
        '\n♻️️Изменён принцип работы с профилями игроков'
        '\n♻️Сделано множество мелких исправлений'
        '\n\n❕1.41.5r'
        '\n➕Добавлена поддержка ввода сообщений из консоли и TCP сервера'
        '\n♻️Изменён принцип работы с историями'
        '\n\n❕1.41.4r'
        '\n➕Функция смены языка возвращена'
        '\n\n❕1.41.3r'
        '\n♻️Python обновлён до версии 3.12.0'
        '\n♻️Рефакторинг кода бота'
        '\n\n❕1.41.2r'
        '\n♻️Переработана система шансов и коэффициентов в играх'
        '\n♻️Исправлены ошибки'
        '\n\n❕1.41.1r'
        '\n♻️Предотвращены возможные откаты профилей при перезапуске бота'
        '\n\n❕1.41r'
        '\n➕Добавлена игра "📈Экспонента📉"'
        '\n➕Добавлено больше динамической покраски кнопок'
        '\n♻️Улучшена система создания резервных копий'
        '\n♻️Исправлена история по промокодам'
        '\n\n❕1.40.5r'
        '\n♻️Работа бота оптимизирована'
        '\n♻️Исправлено несколько ошибок, связанных с достижениями и выводом'
        '\n\n❕1.40.4r'
        '\n♻️Исправлены незначительныые недочёты и внесены улучшения'
        '\n\n❕1.40.3r'
        '\n➕Добавлены вывод и пополнение через ₽'
        '\n♻️Python обновлён до версии 3.11.4'
        '\n\n❕1.40.2r'
        '\n❕Добавлен топ по количеству репостов'
        '\n❕Добавлено достижение на количество репостов'
        '\n♻️Переработана система бонусов за репосты'
        '\n♻️В истории бонусов теперь есть ссылка на репостнутую запись'
        '\n\n❕1.40.1r'
        '\n➕Осуществлён переход на собственную валюту'
        '\n\n❕1.40r'
        '\n➕Добавлено 12 историй по новым категориям'
        '\n➕Добавлены 4 новых достижения'
        '\n➕Добавлен топ по промокодам'
        '\n➕Теперь в промокодах будет список уже активированных промокодов, а также количество активированных промокодов в профиле и статистике'
        '\n➕Теперь в историях время может отображаться в неделях, месяцах и годах'
        '\n➖Смена языка отключена из-за неработающего API Microsoft Bing'
        '\n♻️Теперь рассылка в боте происходит намного быстрее'
        '\n♻️Пополнение теперь на главном экране'
        '\n♻️Бот значительно переписан с использованием ООП'
        '\n♻️Исправлено появление двух кнопок "🔚В меню" в "💣Минном поле💣"'
        '\n♻️Исправлены ошибки'
        '\n♻️Исправлены очепятки'
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
