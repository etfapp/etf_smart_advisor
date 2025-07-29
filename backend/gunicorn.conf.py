"""
Gunicorn配置文件
"""

import os

# 綁定地址和端口
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"

# 工作進程數
workers = 1

# 工作進程類型
worker_class = "sync"

# 超時設置
timeout = 120
keepalive = 2

# 日誌設置
loglevel = "info"
accesslog = "-"
errorlog = "-"

# 預載應用
preload_app = True

# 最大請求數
max_requests = 1000
max_requests_jitter = 100

