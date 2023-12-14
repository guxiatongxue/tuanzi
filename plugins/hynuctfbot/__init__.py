# python39
# -*- coding: utf-8 -*-
# @Time    : 2023-4-2-12:25:15
# @Author  : nH0pe
# @Email   : jzhtz@vip.qq.com
# @File    : __init__.py
# @Software: PyCharm
import pytz
import requests
import json
from nonebot import require
from datetime import datetime
from nonebot import get_bot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

status = False
# 比赛配置
before_notice_id = 0
group_id = 000000 # 群号
game_id = 1

start_notice = on_command('开启解题播报', priority=1, block=True, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@start_notice.handle()
async def start_notice():
    global status
    status = True
    bot: Bot = get_bot()
    await bot.send_msg(message_type="group", group_id=group_id, message='解题播报已开启')


stop_notice = on_command('关闭解题播报', priority=1, block=True, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@stop_notice.handle()
async def stop_notice():
    global status
    status = False
    bot: Bot = get_bot()
    await bot.send_msg(message_type="group", group_id=group_id, message='解题播报已关闭')


async def get_info() -> str:
    global before_notice_id
    cookie = {
        'GZCTF_Token': ''
    }
    url = f"https://xxx.xxx.xxx/api/game/{game_id}/notices"
    response = requests.get(url, cookies=cookie)

    if response.status_code != 200:
        return ""

    data = json.loads(response.text)
    if len(data) == 0:
        return ""

        # 获取最新的一条公告信息
    latest_notice = data[0]
    latest_notice_id = latest_notice.get("id", "")
    notice_title = latest_notice.get("type", "")
    notice_content = latest_notice.get("content", "")
    notice_time = latest_notice.get("time", "")
    utc_time = datetime.strptime(notice_time, '%Y-%m-%dT%H:%M:%S.%f%z')
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = utc_time.astimezone(beijing_tz)
    beijing_time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    if notice_title == "" or notice_content == "" or notice_time == "" or latest_notice_id == before_notice_id:
        return ""

    # 组装消息
    before_notice_id = latest_notice_id
    message = f"类型：{notice_title}\n{notice_content}\n时间：{beijing_time_str}"
    return message


@scheduler.scheduled_job('interval', seconds=1)
async def auto_get_info():
    if not status:
        return
    message = await get_info()
    if message == "":
        return
    bot: Bot = get_bot()
    await bot.send_msg(message_type="group", group_id=group_id, message=message)
