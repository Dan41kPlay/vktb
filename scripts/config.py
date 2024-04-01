from pathlib import Path
from threading import Thread
from typing import Callable, Final, Optional, Type


from libs.vk_api_fast.bot_longpoll import VkBotEventType


__all__ = ['Group', 'Constants', 'Database', 'logs', 'group', 'VKC', 'decideAsync',
           'TEST_VERSION', 'WORKING', 'LOG_MODE', 'VKC_ENABLED', 'UPDATE_DATABASE_ON_START', 'UPDATE_DATABASE_ON_LISTEN_ERROR',
           'ASYNC_DATABASE_UPDATE', 'ADD_USERS_FROM_ALL_CONVERSATIONS', 'SKIP_UPDATES', 'POST_UPDATE_MESSAGE', 'RPI_GPIO_ENABLED']

TEST_VERSION: Final[bool] = True
WORKING: bool = True
LOG_MODE: int = 1
VKC_ENABLED: Final[bool] = False
UPDATE_DATABASE_ON_START: Final[bool] = True
UPDATE_DATABASE_ON_LISTEN_ERROR: bool = True
ASYNC_DATABASE_UPDATE: bool = True
ADD_USERS_FROM_ALL_CONVERSATIONS: Final[bool] = True
SKIP_UPDATES: Final[bool] = False
POST_UPDATE_MESSAGE: Final[bool] = True
RPI_GPIO_ENABLED: bool = False


def decideAsync(condition: bool, target: Callable, thread_name_if_async: str) -> None:
    if condition:
        Thread(target=target, name=thread_name_if_async).start()
    else:
        target()


class Group:
    class Test:
        tokenGroup: str = ''
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
