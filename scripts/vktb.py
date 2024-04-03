from ctypes import windll
from tendo.singleton import SingleInstance, SingleInstanceException

from .config import *
from .classes import *
from .functions import *
from libs.vk_api_fast import VkApi
from libs.vk_api_fast.bot_longpoll import VkBotEvent, VkBotEventType, VkBotLongPoll
from libs.vk_api_fast.exceptions import ApiError, VkApiError


botPrefs: BotPrefs


def main():

    vk = VkApi(token=group.tokenGroup, api_version=botPrefs.apiVersion)
    vkApi = vk.get_api()
    if None in {group.title, group.name}:
        groupInfo = vkApi.groups.getById(group_id=group.id)[0]
        if group.title is None:
            group.title = groupInfo['name']
        if group.name is None:
            group.name = groupInfo['screen_name']


def preMain() -> None:
    try:
        me = SingleInstance()
    except SingleInstanceException:
        windll.user32.MessageBoxW(0, 'Another instance of the bot is already running!', 'Error!', 0, 0x00001000)
        exit()
    if not isConnected():
        windll.user32.MessageBoxW(0, 'No Internet connection!', 'Error!', 0, 0x00001000)
        exit()
    while True:
        try:
            main()
        except Exception as exception:
            log('error', exception)
            log('info', 'Critical error occurred, restarting bot...')


if __name__ == '__main__':
    preMain()
