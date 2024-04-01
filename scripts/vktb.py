from config import *
from libs.vk_api_fast import VkApi
from libs.vk_api_fast.bot_longpoll import VkBotEvent, VkBotEventType, VkBotLongPoll
from libs.vk_api_fast.exceptions import ApiError, VkApiError


def main():

    vk = VkApi(token=group.tokenGroup, api_version=botPrefs.apiVersion)
    vkApi = vk.get_api()
    if None in {group.title, group.name}:
        groupInfo = vkApi.groups.getById(group_id=group.id)[0]
        if group.title is None:
            group.title = groupInfo['name']
        if group.name is None:
            group.name = groupInfo['screen_name']
