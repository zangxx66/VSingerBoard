import gzip
import re
import sys
import urllib.parse
import requests
import asyncio
from .ac_signature import get__ac_signature
from .signature import execute_js, generateSignature, generateMsToken
from .lib import (
    WebcastImPushFrame,
    WebcastImResponse,
    WebcastImChatMessage,
)
from src.utils import Decorator, logger, WebSocketClient


class DouyinLiveWebFetcher(Decorator, WebSocketClient):
    def __init__(self, live_id: int, max_retries: int = 5, retry_delay: int = 5, abogus_file='a_bogus.js'):
        # For macOS packaged app
        ssl_verify = sys.platform != "darwin"
        super().__init__(ssl=ssl_verify)

        self.abogus_file = abogus_file
        self.__ttwid = None
        self.__room_id = None
        self.heartheat_task = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.http_session = requests.Session()
        self.live_id = str(live_id)
        self.host = "https://www.douyin.com/"
        self.live_url = "https://live.douyin.com/"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
        self.headers = {
            'User-Agent': self.user_agent
        }

    @property
    def ws_connect_status(self):
        """
        获取详细的WebSocket连接状态码。

        :return: int, 0:未连接, 1:已连接, 2:已断开, 3:连接失败
        """
        return self.status_code

    @property
    def ttwid(self):
        """
        产生请求头部cookie中的ttwid字段，访问抖音网页版直播间首页可以获取到响应cookie中的ttwid

        :return: ttwid
        """
        if self.__ttwid:
            return self.__ttwid
        headers = {
            "User-Agent": self.user_agent,
        }
        try:
            response = self.http_session.get(self.live_url, headers=headers)
            response.raise_for_status()
        except Exception as err:
            logger.error("【X】Request the live url error: ", err)
        else:
            self.__ttwid = response.cookies.get('ttwid')
            return self.__ttwid

    @property
    def room_id(self):
        """
        根据直播间的地址获取到真正的直播间roomId，有时会有错误，可以重试请求解决

        :return:room_id
        """
        if self.__room_id:
            return self.__room_id
        url = self.live_url + self.live_id
        headers = {
            "User-Agent": self.user_agent,
            "cookie": f"ttwid={self.ttwid}&msToken={generateMsToken()}; __ac_nonce=0123407cc00a9e438deb4",
        }
        try:
            response = self.http_session.get(url, headers=headers)
            response.raise_for_status()
        except Exception as err:
            logger.error("【X】Request the live room url error: ", err)
        else:
            match = re.search(r'roomId\\":\\"(\d+)\\"', response.text)
            if match is None or len(match.groups()) < 1:
                logger.warning("【X】No match found for roomId")

            self.__room_id = match.group(1)

            return self.__room_id

    @property
    def _wss_url(self):
        wss = ("wss://webcast100-ws-web-lq.douyin.com/webcast/im/push/v2/?app_name=douyin_web"
               "&version_code=180800&webcast_sdk_version=1.0.14-beta.0"
               "&update_version_code=1.0.14-beta.0&compress=gzip&device_platform=web&cookie_enabled=true"
               "&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32"
               "&browser_name=Mozilla"
               "&browser_version=5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,"
               "%20like%20Gecko)%20Chrome/126.0.0.0%20Safari/537.36"
               "&browser_online=true&tz_name=Asia/Shanghai"
               "&cursor=d-1_u-1_fh-7392091211001140287_t-1721106114633_r-1"
               f"&internal_ext=internal_src:dim|wss_push_room_id:{self.room_id}|wss_push_did:7319483754668557238"
               f"|first_req_ms:1721106114541|fetch_time:1721106114633|seq:1|wss_info:0-1721106114633-0-0|"
               f"wrds_v:7392094459690748497"
               f"&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&endpoint=live_pc&support_wrds=1"
               f"&user_unique_id=7319483754668557238&im_path=/webcast/im/fetch/&identity=audience"
               f"&need_persist_msg_count=15&insert_task_id=&live_reason=&room_id={self.room_id}&heartbeatDuration=0")

        signature = generateSignature(wss)
        wss += f"&signature={signature}"

        return wss

    async def connect_async(self):
        self.url = self._wss_url

        self.headers = {
            "cookie": f"ttwid={self.ttwid}",
            'user-agent': self.user_agent,
        }
        await self.start()
        self.heartheat_task = asyncio.create_task(self._sendHeartbeat())

    async def _reconnect(self):
        # 不确定抖子这边掉线频繁是否跟签名有关，先试试效果
        self.url = self._wss_url
        if self.heartheat_task:
            self.heartheat_task.cancel()
        await super()._reconnect()
        self.heartheat_task = asyncio.create_task(self._sendHeartbeat())

    async def disconnect_async(self):
        if self.heartheat_task and not self.heartheat_task.done():
            self.heartheat_task.cancel()
        await self.close()

    def get_ac_nonce(self):
        """
        获取 __ac_nonce
        """
        resp_cookies = self.http_session.get(self.host, headers=self.headers).cookies
        return resp_cookies.get("__ac_nonce")

    def get_ac_signature(self, __ac_nonce: str = None) -> str:
        """
        获取 __ac_signature
        """
        __ac_signature = get__ac_signature(self.host[8:], __ac_nonce, self.user_agent)
        self.http_session.cookies.set("__ac_signature", __ac_signature)
        return __ac_signature

    def get_a_bogus(self, url_params: dict):
        """
        获取 a_bogus
        """
        url = urllib.parse.urlencode(url_params)
        _a_bogus = execute_js(url, self.user_agent, js_file=self.abogus_file, func_name="get_ab")
        return _a_bogus

    async def _sendHeartbeat(self):
        """
        发送心跳包
        """
        while self._is_running:
            try:
                if self.status_code != 1:
                    logger.warning("ws_clinet 连接状态错误")
                    break

                heartbeat = WebcastImPushFrame(payload_type='hb').SerializeToString()
                await self.ws.ping(heartbeat)
                # print("【√】发送心跳包")
            except Exception as e:
                logger.error("【X】心跳包检测错误: ", e)
                break
            else:
                await asyncio.sleep(5)

    async def on_message(self, message):
        # 根据proto结构体解析对象
        package = WebcastImPushFrame().parse(message)
        response = WebcastImResponse().parse(gzip.decompress(package.payload))

        # 返回直播间服务器链接存活确认消息，便于持续获取数据
        if response.need_ack:
            ack = WebcastImPushFrame(log_id=package.log_id, payload_type='ack', payload=response.internal_ext.encode('utf-8')).SerializeToString()
            await self.send(ack)

        for msg in response.messages:
            method = msg.method
            try:
                {
                    'WebcastChatMessage': self._parseChatMsg,  # 聊天消息
                }.get(method)(msg.payload)
            except Exception:
                pass

    def _parseChatMsg(self, payload):
        """聊天消息"""
        message = WebcastImChatMessage().parse(payload)
        user_name = message.user.nickname
        user_id = message.user.id
        content = message.content
        logger.debug(f"【聊天msg】[{user_id}]{user_name}: {content}")
        self.dispatch("danmu", {"user_name": user_name, "user_id": user_id, "content": content, "fans_club_data": message.user.fans_club.data})
