import gzip
import re
import urllib.parse
import requests
import asyncio
from .ac_signature import get__ac_signature
from .signature import execute_js, generateSignature, generateMsToken
from .protobuf import PushFrame, Response, ChatMessage, GiftMessage, LikeMessage, MemberMessage, SocialMessage, RoomUserSeqMessage, FansclubMessage, EmojiChatMessage, RoomMessage, RoomStatsMessage, RoomRankMessage, ControlMessage, RoomStreamAdaptationMessage
from src.utils import Decorator, logger, WebSocketClient


class DouyinLiveWebFetcher(Decorator, WebSocketClient):
    def __init__(self, live_id: int, max_retries: int = 5, retry_delay: int = 5, abogus_file='a_bogus.js'):
        self.abogus_file = abogus_file
        self.__ttwid = None
        self.__room_id = None
        self.heartheat_task = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._is_running = False
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
        return self._is_running

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

    async def connect_async(self):
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
        self.url = wss

        self.headers = {
            "cookie": f"ttwid={self.ttwid}",
            'user-agent': self.user_agent,
        }
        await self.start()
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
        ctx = execute_js(self.abogus_file)
        _a_bogus = ctx.call("get_ab", url, self.user_agent)
        return _a_bogus

    async def _sendHeartbeat(self):
        """
        发送心跳包
        """
        while self._is_running:
            try:
                heartbeat = PushFrame(payload_type='hb').SerializeToString()
                # self.send(heartbeat, websocket.ABNF.OPCODE_PING)
                await self.ws.ping(heartbeat)
                # print("【√】发送心跳包")
            except Exception as e:
                logger.error("【X】心跳包检测错误: ", e)
                break
            else:
                await asyncio.sleep(5)

    async def on_message(self, message):
        # 根据proto结构体解析对象
        package = PushFrame().parse(message)
        response = Response().parse(gzip.decompress(package.payload))

        # 返回直播间服务器链接存活确认消息，便于持续获取数据
        if response.need_ack:
            ack = PushFrame(log_id=package.log_id,
                            payload_type='ack',
                            payload=response.internal_ext.encode('utf-8')
                            ).SerializeToString()
            await self.send(ack)

        for msg in response.messages_list:
            method = msg.method
            try:
                {
                    'WebcastChatMessage': self._parseChatMsg,  # 聊天消息
                    'WebcastGiftMessage': self._parseGiftMsg,  # 礼物消息
                    'WebcastLikeMessage': self._parseLikeMsg,  # 点赞消息
                    'WebcastMemberMessage': self._parseMemberMsg,  # 进入直播间消息
                    'WebcastSocialMessage': self._parseSocialMsg,  # 关注消息
                    'WebcastRoomUserSeqMessage': self._parseRoomUserSeqMsg,  # 直播间统计
                    'WebcastFansclubMessage': self._parseFansclubMsg,  # 粉丝团消息
                    'WebcastControlMessage': self._parseControlMsg,  # 直播间状态消息
                    'WebcastEmojiChatMessage': self._parseEmojiChatMsg,  # 聊天表情包消息
                    'WebcastRoomStatsMessage': self._parseRoomStatsMsg,  # 直播间统计信息
                    'WebcastRoomMessage': self._parseRoomMsg,  # 直播间信息
                    'WebcastRoomRankMessage': self._parseRankMsg,  # 直播间排行榜信息
                    'WebcastRoomStreamAdaptationMessage': self._parseRoomStreamAdaptationMsg,  # 直播间流配置
                }.get(method)(msg.payload)
            except Exception:
                pass

    def _parseChatMsg(self, payload):
        """聊天消息"""
        message = ChatMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        content = message.content
        logger.debug(f"【聊天msg】[{user_id}]{user_name}: {content}")
        self.dispatch("danmu", {"user_name": user_name, "user_id": user_id, "content": content, "level": message.user.level, "fans_club_data": message.user.fans_club.data})

    def _parseGiftMsg(self, payload):
        """礼物消息"""
        message = GiftMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        gift_name = message.gift.name
        gift_cnt = message.combo_count
        logger.debug(f"【礼物msg】{user_name} 送出了 {gift_name}x{gift_cnt}")
        self.dispatch("gift", {"user_name": user_name, "user_id": user_id, "gift_name": gift_name, "gift_cnt": gift_cnt})

    def _parseLikeMsg(self, payload):
        '''点赞消息'''
        message = LikeMessage().parse(payload)
        user_name = message.user.nick_name
        count = message.count
        # print(f"【点赞msg】{user_name} 点了{count}个赞")
        self.dispatch("like", {"user_name": user_name, "user_id": message.user.id, "count": count})

    def _parseMemberMsg(self, payload):
        '''进入直播间消息'''
        message = MemberMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        # gender = ["女", "男"][message.user.gender]
        # print(f"【进场msg】[{user_id}][{gender}]{user_name} 进入了直播间")
        self.dispatch("enter", {"user_name": user_name, "user_id": user_id})

    def _parseSocialMsg(self, payload):
        '''关注消息'''
        message = SocialMessage().parse(payload)
        user_name = message.user.nick_name
        # user_id = message.user.id
        # print(f"【关注msg】[{user_id}]{user_name} 关注了主播")
        self.dispatch("follow", {"user_name": user_name, "user_id": message.user.id})

    def _parseRoomUserSeqMsg(self, payload):
        '''直播间统计'''
        message = RoomUserSeqMessage().parse(payload)
        current = message.total
        total = message.total_pv_for_anchor
        # print(f"【统计msg】当前观看人数: {current}, 累计观看人数: {total}")
        self.dispatch("stats", {"current": current, "total": total})

    def _parseFansclubMsg(self, payload):
        '''粉丝团消息'''
        message = FansclubMessage().parse(payload)
        content = message.content
        logger.debug(f"【粉丝团msg】 {content}")

    def _parseEmojiChatMsg(self, payload):
        '''聊天表情包消息'''
        message = EmojiChatMessage().parse(payload)
        emoji_id = message.emoji_id
        user = message.user
        logger.debug(f"【聊天表情包id】{user.nick_name}：{emoji_id}")

    def _parseRoomMsg(self, payload):
        message = RoomMessage().parse(payload)
        common = message.common
        room_id = common.room_id
        logger.debug(f"【直播间msg】直播间id:{room_id}")

    def _parseRoomStatsMsg(self, payload):
        message = RoomStatsMessage().parse(payload)
        display_long = message.display_long
        logger.debug(f"【直播间统计msg】{display_long}")

    def _parseRankMsg(self, payload):
        message = RoomRankMessage().parse(payload)
        ranks_list = message.ranks_list
        result = [item.user.nick_name for item in ranks_list]
        logger.debug(f"【直播间排行榜msg】{result}")

    def _parseControlMsg(self, payload):
        '''直播间状态消息'''
        message = ControlMessage().parse(payload)

        if message.status == 3:
            logger.info("【直播间状态消息】直播已结束")
        else:
            logger.info(f"【直播间状态消息】未处理的直播间状态：{message.status}，method: {message.common.method}")

    def _parseRoomStreamAdaptationMsg(self, payload):
        message = RoomStreamAdaptationMessage().parse(payload)
        adaptationType = message.adaptation_type
        logger.debug(f'直播间adaptation: {adaptationType}')
