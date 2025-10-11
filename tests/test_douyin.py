
import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from types import SimpleNamespace

from src.live.douyin import Douyin


class TestDouyin(unittest.IsolatedAsyncioTestCase):

    @patch('src.live.douyin.Db')
    @patch('src.live.douyin.DouyinLiveWebFetcher')
    @patch('src.live.douyin.async_worker')
    @patch('src.live.douyin.asyncio.wrap_future')
    async def test_douyin_start_and_stop(self, mock_wrap_future, mock_async_worker, mock_douyin_fetcher, mock_db):
        """
        测试 Douyin 类的 start 和 stop 方法是否能正确启动和停止服务。
        """
        # --- Mocks Setup ---

        # 模拟 async_worker.submit
        task = None

        def submit_side_effect(coro):
            nonlocal task
            task = asyncio.create_task(coro)
            return task
        mock_async_worker.submit.side_effect = submit_side_effect

        # 模拟 asyncio.wrap_future
        mock_wrap_future.side_effect = lambda f: f

        # 模拟 DouyinLiveWebFetcher 实例
        mock_fetcher_instance = AsyncMock()
        # .on() 和 .remove_listener() 是直接调用，非 await，所以用 MagicMock 替换
        mock_fetcher_instance.on = MagicMock(return_value=MagicMock())
        mock_fetcher_instance.remove_listener = MagicMock()
        mock_douyin_fetcher.return_value = mock_fetcher_instance

        # 模拟数据库调用
        mock_config = SimpleNamespace(room_id=456, sing_prefix="#sing")
        mock_db.get_dy_config = AsyncMock(return_value=mock_config)

        # --- Test Execution ---

        douyin = Douyin()
        douyin.start()

        await asyncio.sleep(0.01)

        # 验证 start 逻辑
        mock_async_worker.submit.assert_called_once()
        mock_douyin_fetcher.assert_called_with(live_id=456, max_retries=99)
        mock_fetcher_instance.connect_async.assert_awaited_once()
        self.assertIsNotNone(douyin.live)

        # 调用 stop
        await douyin.stop()

        # --- Assertions ---

        # 验证 stop 逻辑
        mock_fetcher_instance.disconnect_async.assert_awaited_once()
        mock_fetcher_instance.remove_listener.assert_called_once_with("danmu", douyin.add_dydanmu)
        self.assertIsNone(douyin.live)
        self.assertIsNone(douyin._run_future)


if __name__ == '__main__':
    unittest.main()
