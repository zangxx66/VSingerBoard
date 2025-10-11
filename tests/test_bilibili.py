
import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from types import SimpleNamespace

from src.live.bilibili import Bili


class TestBilibili(unittest.IsolatedAsyncioTestCase):

    @patch('src.live.bilibili.Db')
    @patch('src.live.bilibili.live')
    @patch('src.live.bilibili.async_worker')
    @patch('src.live.bilibili.asyncio.wrap_future')
    async def test_start_and_stop(self, mock_wrap_future, mock_async_worker, mock_bili_live, mock_db):
        """
        测试 Bili 类的 start 和 stop 方法是否能正确启动和停止服务。
        """
        # --- Mocks Setup ---

        # 模拟 async_worker.submit，让它返回一个真正的 asyncio.Task
        task = None

        def submit_side_effect(coro):
            nonlocal task
            task = asyncio.create_task(coro)
            return task
        mock_async_worker.submit.side_effect = submit_side_effect

        # 当 bili.stop() 尝试包装 future 时，我们直接返回 task，因为 task 已经是 awaitable 的
        mock_wrap_future.side_effect = lambda f: f

        # Mock a LiveDanmaku instance
        mock_live_danmaku = AsyncMock()
        # .on() and .remove_event_listener() are called directly, not awaited.
        # Replace the default AsyncMocks for these methods with regular MagicMocks.
        mock_live_danmaku.on = MagicMock(return_value=MagicMock())
        mock_live_danmaku.remove_event_listener = MagicMock()
        mock_bili_live.LiveDanmaku.return_value = mock_live_danmaku

        # Mock database calls
        mock_config = SimpleNamespace(room_id=123, sing_prefix="!sing")
        mock_db.get_bconfig = AsyncMock(return_value=mock_config)
        mock_db.get_bcredential = AsyncMock(return_value=None)

        # --- Test Execution ---

        bili = Bili()
        bili.start()

        # 给一点时间让后台任务启动
        await asyncio.sleep(0.01)

        # 验证 start 逻辑
        mock_async_worker.submit.assert_called_once()
        mock_bili_live.LiveDanmaku.assert_called_once()
        mock_live_danmaku.connect.assert_awaited_once()
        self.assertIsNotNone(bili.live)

        # 调用 stop
        await bili.stop()

        # --- Assertions ---

        # 验证 stop 逻辑
        mock_live_danmaku.disconnect.assert_awaited_once()
        self.assertEqual(mock_live_danmaku.remove_event_listener.call_count, 2)
        self.assertIsNone(bili.live)
        self.assertIsNone(bili._run_future)


if __name__ == '__main__':
    unittest.main()
