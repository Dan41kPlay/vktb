from pathlib import Path
from threading import Thread
from typing import Callable, Final, Optional, Type

from libs.vk_api_fast.bot_longpoll import VkBotEventType


__all__ = ['Group', 'Constants', 'Database', 'logs', 'group', 'decideAsync',
           'TEST_VERSION', 'WORKING', 'LOG_MODE',  'UPDATE_DATABASE_ON_START', 'UPDATE_DATABASE_ON_LISTEN_ERROR',
           'ASYNC_DATABASE_UPDATE', 'ADD_USERS_FROM_ALL_CONVERSATIONS', 'SKIP_UPDATES', 'POST_UPDATE_MESSAGE']

TEST_VERSION: Final[bool] = True
WORKING: bool = True
LOG_MODE: int = 1
UPDATE_DATABASE_ON_START: Final[bool] = True
UPDATE_DATABASE_ON_LISTEN_ERROR: bool = True
ASYNC_DATABASE_UPDATE: bool = True
ADD_USERS_FROM_ALL_CONVERSATIONS: Final[bool] = True
SKIP_UPDATES: Final[bool] = False
POST_UPDATE_MESSAGE: Final[bool] = True


def decideAsync(condition: bool, target: Callable, thread_name_if_async: str) -> None:
    if condition:
        Thread(target=target, name=thread_name_if_async).start()
    else:
        target()


class Group:
    class Test:
        tokenGroup: str = 'vk1.a.p0irUN0ak6ezYBlgMiE6MXlOkwuGEAnfqTc_lDRkjgYm4PEVs92z-mo88vWm0nx_0j-mmC1IzUKlLOEC58pwcqFl9gGHtyNDNjrm9_hlh5uF8Hjc0Wv7ZFrwDDwP9UoPTTIKzOk734O9CqAXWDUUmZUXOB2tjSAK_s1jKj7DemqgXwMhhlh_yxclqi0PeqAAtGenWvxrfU71_UA9Vb7viA'
        tokenUser: str = ''  # https://oauth.vk.com/authorize?client_id=8049194&scope=board,wall,offline&redirect_uri=https://oauth.vk.com/blank.html&display=page&v=5.199&response_type=token
        id: int = 225362684
        name: Optional[str] = None
        title: Optional[str] = None

    class Public:
        ...


class Constants:
    class DateTimeForms:
        forLog: str = '%Y.%m.%d %H:%M:%S.%f'
        full: str = '%Y.%m.%d %H:%M:%S'
        fullReversed: str = '%d.%m.%Y %H:%M:%S'
        forBan: str = '%d.%m.%Y %H:%M'
        dateOnly: str = '%Y.%m.%d'
        forVersion: str = '%Y%m%d'
        forReserveCopy: str = '%Y%m%d_%H%M%S'

    devId = 483021086
    specialChar: str = '⍼'
    vkIP: str = '87.240.132.78'
    commands: str = ''

    inlineKeyboards: set[str] = set()
    keyboardsWithToMenuButton: set[str] = set()


class Database:
    folderName: str = 'database'
    reserveCopyDeleteTimeDays: int = 3
    reserveCopyFolderName: str = 'reserve_copy'
    reserveCopyFolderPath: Path = Path(folderName, reserveCopyFolderName)
    usersFileName: str = 'users.json'
    usersFilePath: Path = Path(folderName, usersFileName)
    botPrefsFileName: str = 'botPrefs.json'
    botPrefsFilePath: Path = Path(folderName, botPrefsFileName)
    todoFileName: str = 'todo.json'
    todoFilePath: Path = Path(folderName, todoFileName)


logs: list[str] = []
group: Type[Group.Test | Group.Public] = Group.Test if TEST_VERSION else Group.Public
