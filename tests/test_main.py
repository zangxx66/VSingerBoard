import unittest
from unittest.mock import patch
import main as main_module


class TestMain(unittest.TestCase):

    @patch('main.main')
    @patch('os._exit')
    @patch('main.async_worker')
    def test_run_app_normal_exit(
        self, mock_async_worker, mock_os_exit, mock_main_func
    ):
        """
        测试 run_app 在正常退出时调用 async_worker.stop 和 os._exit
        """
        main_module.run_app()

        mock_main_func.assert_called_once()
        mock_async_worker.stop.assert_called_once()
        mock_os_exit.assert_called_once_with(0)

    @patch('main.main', side_effect=Exception("Test Exception"))
    @patch('os._exit')
    @patch('main.async_worker')
    @patch('main.logger')
    def test_run_app_exception_exit(
        self, mock_logger, mock_async_worker, mock_os_exit, mock_main_func
    ):
        """
        测试 run_app 在 main 函数抛出异常时调用清理函数
        """
        main_module.run_app()

        mock_main_func.assert_called_once()
        mock_logger.exception.assert_called_once()
        mock_async_worker.stop.assert_called_once()
        mock_os_exit.assert_called_once_with(0)


if __name__ == '__main__':
    unittest.main()
