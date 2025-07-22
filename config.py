import os

class Config:
    """การตั้งค่าสำหรับแอปพลิเคชัน"""

    VERSION = "0.6.8"
    SECRET_KEY = os.environ.get("SECRET_KEY", "BST-bangsithong-app-SECRET_KEY-024467684")

    # Database
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_NAME = os.environ.get("DB_NAME")

    # SSO Settings
    SSO_CLIENT_ID = os.environ.get("SSO_CLIENT_ID")
    SSO_CLIENT_SECRET = os.environ.get("SSO_CLIENT_SECRET")
    SSO_AUTHORIZE_URL = os.environ.get("SSO_AUTHORIZE_URL")
    SSO_TOKEN_URL = os.environ.get("SSO_TOKEN_URL")
    SSO_USERINFO_URL = os.environ.get("SSO_USERINFO_URL")
    SSO_SECRET_KEY = os.environ.get("SSO_SECRET_KEY")
