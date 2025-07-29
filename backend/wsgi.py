"""
WSGI入口文件 - 用於Gunicorn部署
"""

from app import app

if __name__ == "__main__":
    app.run()

