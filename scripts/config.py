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
        tokenGroup: str = 'vk1.a.9PjuLuAj1EjKm7DuORO97apb8I2SurvSuGMTIf8oLZGERTWrKgP3A-oycjs-PPDWcDqmQojjZNSPBj9Sl0YSqtAI2CqRg0pPjvMFro4ihFiU0J4vDM5EauLcSmhyul9qRiG_i5KVeEC8BTB-SUXS_6hSbpTO5hlyO4Kg1fDkx0TSoDShXO5-jl0-JsgycVs5EFu_H-Lu0elTs41KcZD_gw'
        tokenUser: str = ''  # https://oauth.vk.com/authorize?client_id=8049194&scope=board,wall,offline&redirect_uri=https://oauth.vk.com/blank.html&display=page&v=5.131&response_type=token
        id: int = 200655850
        name: Optional[str] = None
        title: Optional[str] = None

        class Topics:
            class Feedbacks:
                id: int = 0
                name: Optional[str] = None

            class Suggestions:
                id: int = 0
                name: Optional[str] = None

            class BugReports:
                id: int = 0
                name: Optional[str] = None

    class Public:
        ...


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


class Constants:
    ...


logs: list[str] = []
group: Type[Group.Test | Group.Public] = Group.Test if TEST_VERSION else Group.Public
