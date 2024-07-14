import asyncio
import datetime
import logging
import os
import random
import sys
import time

import requests
import yaml
from telegram import Bot

from get_bearer_token import get_bearer_token
from get_info import (
    get_date,
    get_seat_info,
    get_segment,
    get_build_id,
    encrypt,
    get_member_seat,
)

import json
import base64
import hmac
import hashlib
import urllib.parse


# 配置日志
logger = logging.getLogger("httpx")
logger.setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL_GET_SEAT = "http://libyy.qfnu.edu.cn/api/Seat/confirm"
URL_CHECK_OUT = "http://libyy.qfnu.edu.cn/api/Space/checkout"
URL_CANCEL_SEAT = "http://libyy.qfnu.edu.cn/api/Space/cancel"

# 配置文件
CHANNEL_ID = ""
TELEGRAM_BOT_TOKEN = ""
MODE = ""
CLASSROOMS_NAME = ""
SEAT_ID = ""
DATE = ""
USERNAME = ""
PASSWORD = ""
GITHUB = ""
BARK_URL = ""
BARK_EXTRA = ""
ANPUSH_TOKEN = ""
ANPUSH_CHANNEL = ""
DD_BOT_SECRET = ""
DD_BOT_TOKEN = ""
PUSH_METHOD = ""


# 读取YAML配置文件并设置全局变量
def read_config_from_yaml():
    global CHANNEL_ID, TELEGRAM_BOT_TOKEN, CLASSROOMS_NAME, MODE, SEAT_ID, DATE, USERNAME, PASSWORD, GITHUB, BARK_EXTRA, BARK_URL, ANPUSH_TOKEN, ANPUSH_CHANNEL, PUSH_METHOD, DD_BOT_TOKEN, DD_BOT_SECRET
    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )  # 获取当前文件所在的目录的绝对路径
    config_file_path = os.path.join(
        current_dir, "config.yml"
    )  # 将文件名与目录路径拼接起来
    with open(
        config_file_path, "r", encoding="utf-8"
    ) as yaml_file:  # 指定为UTF-8格式打开文件
        config = yaml.safe_load(yaml_file)
        CHANNEL_ID = config.get("CHANNEL_ID", "")
        TELEGRAM_BOT_TOKEN = config.get("TELEGRAM_BOT_TOKEN", "")
        CLASSROOMS_NAME = config.get(
            "CLASSROOMS_NAME", []
        )  # 将 CLASSROOMS_NAME 读取为列表
        MODE = config.get("MODE", "")
        SEAT_ID = config.get("SEAT_ID", [])  # 将 SEAT_ID 读取为列表
        DATE = config.get("DATE", "")
        USERNAME = config.get("USERNAME", "")
        PASSWORD = config.get("PASSWORD", "")
        GITHUB = config.get("GITHUB", "")
        BARK_URL = config.get("BARK_URL", "")
        BARK_EXTRA = config.get("BARK_EXTRA", "")
        ANPUSH_TOKEN = config.get("ANPUSH_TOKEN", "")
        ANPUSH_CHANNEL = config.get("ANPUSH_CHANNEL", "")
        DD_BOT_TOKEN = config.get("DD_BOT_TOKEN", "")
        DD_BOT_SECRET = config.get("DD_BOT_SECRET", "")
        PUSH_METHOD = config.get("PUSH_METHOD", "")


# 在代码的顶部定义全局变量
FLAG = False
SEAT_RESULT = {}
USED_SEAT = []
MESSAGE = ""
AUTH_TOKEN = ""
NEW_DATE = ""
TOKEN_TIMESTAMP = None
TOKEN_EXPIRY_DELTA = datetime.timedelta(hours=1, minutes=30)

# 配置常量
EXCLUDE_ID = {
    "7115",
    "7120",
    "7125",
    "7130",
    "7135",
    "7140",
    "7145",
    "7150",
    "7155",
    "7160",
    "7165",
    "7170",
    "7175",
    "7180",
    "7185",
    "7190",
    "7241",
    "7244",
    "7247",
    "7250",
    "7253",
    "7256",
    "7259",
    "7262",
    "7291",
    "7296",
    "7301",
    "7306",
    "7311",
    "7316",
    "7321",
    "7326",
    "7331",
    "7336",
    "7341",
    "7346",
    "7351",
    "7356",
    "7361",
    "7366",
    "7369",
    "7372",
    "7375",
    "7378",
    "7381",
    "7384",
    "7387",
    "7390",
    "7417",
    "7420",
    "7423",
    "7426",
    "7429",
    "7432",
    "7435",
    "7438",
    "7443",
    "7448",
    "7453",
    "7458",
    "7463",
    "7468",
    "7473",
    "7478",
    "7483",
    "7488",
    "7493",
    "7498",
    "7503",
    "7508",
    "7513",
    "7518",
    "7569",
    "7572",
    "7575",
    "7578",
    "7581",
    "7584",
    "7587",
    "7590",
    "7761",
    "7764",
    "7767",
    "7770",
    "7773",
    "7776",
    "7779",
    "7782",
    "7785",
    "7788",
    "7791",
    "7794",
    "7797",
    "7800",
    "7803",
    "7806",
}


# 打印变量
# 好像是师哥测试数据的函数，暂时保留
def print_variables():
    variables = {
        "CHANNEL_ID": CHANNEL_ID,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "MODE": MODE,
        "CLASSROOMS_NAME": CLASSROOMS_NAME,
        "SEAT_ID": SEAT_ID,
        "USERNAME": USERNAME,
        "PASSWORD": PASSWORD,
        "GITHUB": GITHUB,
        "BARK_URL": BARK_URL,
        "BARK_EXTRA": BARK_EXTRA,
        "ANPUSH_TOKEN": ANPUSH_TOKEN,
        "ANPUSH_CHANNEL": ANPUSH_CHANNEL,
        "DD_BOT_TOKEN": DD_BOT_TOKEN,
        "DD_BOT_SECRET": DD_BOT_SECRET,
        "PUSH_METHOD": PUSH_METHOD,
    }
    for var_name, var_value in variables.items():
        logger.info(f"{var_name}: {var_value} - {type(var_value)}")


# post 请求
def send_post_request_and_save_response(url, data, headers):
    global MESSAGE
    retries = 0
    while retries < 20:
        try:
            response = requests.post(url, json=data, headers=headers, timeout=120)
            response.raise_for_status()
            response_data = response.json()
            return response_data
        except requests.exceptions.Timeout:
            logger.error("请求超时，正在重试...")
            retries += 1
        except Exception as e:
            logger.error(f"request请求异常: {str(e)}")
            retries += 1
    logger.error("超过最大重试次数,请求失败。")
    MESSAGE += "\n超过最大重试次数,请求失败。"
    send_message()
    sys.exit()


def send_message():
    if PUSH_METHOD == "TG":
        asyncio.run(send_message_telegram())
    if PUSH_METHOD == "ANPUSH":
        send_message_anpush()
    if PUSH_METHOD == "BARK":
        send_message_bark()
    if PUSH_METHOD == "DD":
        dingtalk("脚本执行通知", MESSAGE, DD_BOT_TOKEN, DD_BOT_SECRET)


# 推送到钉钉
def dingtalk(text, desp, DD_BOT_TOKEN, DD_BOT_SECRET=None):
    url = f"https://oapi.dingtalk.com/robot/send?access_token={DD_BOT_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {"msgtype": "text", "text": {"content": f"{text}\n{desp}"}}

    if DD_BOT_TOKEN and DD_BOT_SECRET:
        timestamp = str(round(time.time() * 1000))
        secret_enc = DD_BOT_SECRET.encode("utf-8")
        string_to_sign = f"{timestamp}\n{DD_BOT_SECRET}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(
            base64.b64encode(hmac_code).decode("utf-8").strip()
        )
        url = f"{url}&timestamp={timestamp}&sign={sign}"

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    try:
        data = response.json()
        if response.status_code == 200 and data.get("errcode") == 0:
            logger.info("钉钉发送通知消息成功🎉")
        else:
            logger.error(f"钉钉发送通知消息失败😞\n{data.get('errmsg')}")
    except Exception as e:
        logger.error(f"钉钉发送通知消息失败😞\n{e}")

    return response.json()


# 推送到 Bark
def send_message_bark():
    try:
        response = requests.get(BARK_URL + MESSAGE + BARK_EXTRA)
        # 检查响应状态码是否为200
        if response.status_code == 200:
            logger.info("成功推送消息到 Bark")
            # 返回响应内容
            return response.text
        else:
            logger.error(f"推送到 Bark 的 GET请求失败，状态码：{response.status_code}")
            return None
    except requests.exceptions.RequestException:
        logger.info("GET请求异常, 你的 BARK 链接不正确")
        return None


def send_message_anpush():
    url = "https://api.anpush.com/push/" + ANPUSH_TOKEN
    payload = {"title": "预约通知", "content": MESSAGE, "channel": ANPUSH_CHANNEL}

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    requests.post(url, headers=headers, data=payload)
    # logger.info(response.text)


async def send_message_telegram():
    try:
        # 使用 API 令牌初始化您的机器人
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        # logger.info(f"要发送的消息为： {MESSAGE}\n")
        await bot.send_message(chat_id=CHANNEL_ID, text=MESSAGE)
        logger.info("成功推送消息到 Telegram")
    except Exception as e:
        logger.info(
            f"发送消息到 Telegram 失败, 可能是没有设置此通知方式，也可能是没有连接到 Telegram"
        )
        return e


def get_auth_token():
    global TOKEN_TIMESTAMP, AUTH_TOKEN, MESSAGE
    try:
        # 如果未从配置文件中读取到用户名或密码，则抛出异常
        if not USERNAME or not PASSWORD:
            raise ValueError("未找到用户名或密码")

        # 检查 Token 是否过期
        if (
            TOKEN_TIMESTAMP is None
            or (datetime.datetime.now() - TOKEN_TIMESTAMP) > TOKEN_EXPIRY_DELTA
        ):
            # Token 过期或尚未获取，重新获取
            name, token = get_bearer_token(USERNAME, PASSWORD)
            if token is None:
                logging.error("获取 token 失败，账号密码错误或者网络错误。")
                MESSAGE += "\n获取 token 失败，账号密码错误或者网络错误。"
                send_message()
                sys.exit()
            else:
                logger.info(f"成功获取授权码")
                AUTH_TOKEN = "bearer" + str(token)
                # 更新 Token 的时间戳
                TOKEN_TIMESTAMP = datetime.datetime.now()
        else:
            logger.info("使用现有授权码")
    except Exception as e:
        logger.error(f"获取授权码时发生异常: {str(e)}")
        sys.exit()


# 检查是否存在已经预约的座位
def check_book_seat():
    global MESSAGE, FLAG
    try:
        res = get_member_seat(AUTH_TOKEN)
        if res is not None and "msg" in res and res["msg"] == "您尚未登录":
            get_auth_token()
        if res is not None and "data" in res:
            for entry in res["data"]["data"]:
                if entry["statusName"] == "预约成功":
                    seat_id = entry["name"]
                    name = entry["nameMerge"]
                    logger.info(f"预约成功：你当前的座位是 {name} {seat_id}")
                    FLAG = True
                    MESSAGE += f"预约成功：你当前的座位是 {name} {seat_id}\n"
                    send_message()
                    break
                elif entry["statusName"] == "使用中" and DATE == "today":
                    logger.info("存在正在使用的座位")
                    FLAG = True
                    break
                else:
                    continue
            # 测试规则不匹配的情况
            # logger.info(res)
        # todo 错误不明 需要提供日志
    except KeyError:
        logger.error("获取个人座位出现错误")


# 状态检测函数，用来检查响应结果
def check_reservation_status():
    global FLAG, MESSAGE
    # 状态信息检测
    if isinstance(SEAT_RESULT, dict) and "msg" in SEAT_RESULT:
        status = SEAT_RESULT["msg"]
        # logger.info("预约状态：" + str(status))
        if status is not None:
            if status == "当前用户在该时段已存在座位预约，不可重复预约":
                logger.info("重复预约, 请检查选择的时间段或是否已经成功预约")
                check_book_seat()
                FLAG = True
            elif status == "预约成功":
                logger.info("成功预约")
                check_book_seat()
                FLAG = True
            elif status == "开放预约时间19:20":
                logger.info("未到预约时间")
                time.sleep(1)
            elif status == "您尚未登录":
                logger.info("没有登录，将重新尝试获取 token")
                get_auth_token()
            elif status == "该空间当前状态不可预约":
                logger.info("此位置已被预约，重新获取座位")
            elif status == "取消成功":
                logger.info("取消成功")
                sys.exit()
            else:
                FLAG = True
                logger.info(f"未知状态信息: {status}")
        else:
            logger.info(SEAT_RESULT)
    else:
        logger.error(
            "未能获取有效的座位预约状态，token已失效，请不要在脚本执行过程中手动登录"
        )
        MESSAGE += (
            "\n未能获取有效的座位预约状态，token已失效，请不要在脚本执行过程中手动登录"
        )
        send_message()
        sys.exit()


def generate_unique_random():
    global USED_SEAT
    start = int(SEAT_ID[0])
    end = int(SEAT_ID[1])

    # 首先检查是否所有的座位ID都已经被使用
    if len(USED_SEAT) == (end - start + 1):
        return False  # 如果所有座位都用过了，返回False

    # 顺序遍历座位ID, 找到第一个未被使用的座位,此设置与下面随机函数只能取一个
    # for i in range(start, end + 1):
    #     if i in USED_SEAT:
    #         continue
    #     else:
    #         return i

    # 生成范围内的随机整数，直到生成一个未出现过的数
    while True:
        random_num = random.randint(start, end)
        if random_num not in USED_SEAT:
            USED_SEAT.append(random_num)
            return random_num


# 预约函数
def post_to_get_seat(select_id, segment):
    global SEAT_RESULT
    # 原始数据
    origin_data = '{{"seat_id":"{}","segment":"{}"}}'.format(select_id, segment)
    # logger.info(origin_data)

    # 加密数据
    aes_data = encrypt(str(origin_data))
    # aes_data = "test"
    # logger.info(aes_data)

    # 测试解密数据
    # aes = decrypt(aes_data)
    # logger.info(aes)

    # 原始的 post_data
    post_data = {
        "aesjson": aes_data,
    }
    request_headers = {
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "lang": "zh",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, "
        "like Gecko)"
        "Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "Origin": "http://libyy.qfnu.edu.cn",
        "Referer": "http://libyy.qfnu.edu.cn/h5/index.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,pl;q=0.5",
        "Authorization": AUTH_TOKEN,
    }
    # 发送POST请求并获取响应
    SEAT_RESULT = send_post_request_and_save_response(
        URL_GET_SEAT, post_data, request_headers
    )
    check_reservation_status()


# 随机获取座位
def random_get_seat(data):
    global MESSAGE
    # 随机选择一个字典
    random_dict = random.choice(data)
    # 获取该字典中 'id' 键对应的值
    select_id = random_dict["id"]
    # seat_no = random_dict['no']
    # logger.info(f"随机选择的座位为: {select_id} 真实位置: {seat_no}")
    return select_id


# 选座主要逻辑
def select_seat(build_id, segment, nowday):
    global MESSAGE, FLAG
    retries = 0  # 添加重试计数器

    while not FLAG and retries < 2000:
        logger.info(f"*" * 50)
        logger.info(f"开始第 {retries+1} 次尝试获取座位")
        retries += 1

        data = get_seat_info(build_id, segment, nowday) if MODE in ["1", "3"] else None

        seat_id = generate_unique_random()
        logger.info(f"随机选择的座位为: {seat_id}")
        if seat_id == False:
            logger.info("指定模式无可用座位, 程序将自动退出")
            MESSAGE += "\n指定模式无可用座位, 程序将自动退出"
            send_message()
            sys.exit()
        else:
            post_to_get_seat(seat_id, segment)
        continue

    # 如果超过最大重试次数仍然没有获取到座位,则退出程序
    if retries >= 2000:
        logger.error("超过最大重试次数,无法获取座位")
        MESSAGE += "\n超过最大重试次数,无法获取座位"
        send_message()
        sys.exit()


def check_time():
    global MESSAGE
    # 获取当前时间
    current_time = datetime.datetime.now()
    # 如果是 Github Action 环境
    if GITHUB:
        current_time += datetime.timedelta(hours=8)
    # 设置预约时间为19:20
    reservation_time = current_time.replace(hour=19, minute=20, second=0, microsecond=0)
    # 计算距离预约时间的秒数
    time_difference = (reservation_time - current_time).total_seconds()
    # time_difference = 0
    # 如果距离时间过长，自动停止程序
    if time_difference > 1200:  # 1200秒=20分钟
        get_info_and_select_seat()
        # logger.info("距离预约时间过长，程序将自动停止。")
        # MESSAGE += "\n距离预约时间过长，程序将自动停止"
        # send_message()
        # sys.exit()
    # 如果距离时间在合适的范围内, 将设置等待时间
    elif time_difference > 30:
        logger.info(f"程序等待{time_difference}秒后启动")
        time.sleep(time_difference - 10)
        get_info_and_select_seat()
    else:
        get_info_and_select_seat()


# 主函数
def get_info_and_select_seat():
    global AUTH_TOKEN, NEW_DATE, MESSAGE
    try:
        # logger.info(CLASSROOMS_NAME)
        NEW_DATE = get_date(DATE)
        get_auth_token()
        for i in CLASSROOMS_NAME:
            build_id = get_build_id(i)
            segment = get_segment(build_id, NEW_DATE)
            select_seat(build_id, segment, NEW_DATE)

    except KeyboardInterrupt:
        logger.info("主动退出程序，程序将退出。")


if __name__ == "__main__":
    try:
        read_config_from_yaml()
        check_time()
    except KeyboardInterrupt:
        logger.info("主动退出程序，程序将退出。")
