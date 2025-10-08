from typing import Optional
from src.utils.ipc import IPCManager

# 这个模块变量将在服务器启动时被 app.py 赋值
ipc_manager: Optional[IPCManager] = None
