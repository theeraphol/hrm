import os

class Config:
    """การตั้งค่าสำหรับแอปพลิเคชัน"""

    VERSION = "0.8.0"
    SECRET_KEY = os.environ.get("SECRET_KEY", "BST-bangsithong-app-SECRET_KEY-024467684")

    # Database
    DB_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    DB_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    DB_USER = os.environ.get('MYSQL_USER', 'root')
    DB_PASSWORD = os.environ.get('MYSQL_PASSWORD', '987654321')
    # ค่าดีฟอลต์ตรงกับฐานข้อมูลที่สร้างจาก schema.sql
    DB_NAME = os.environ.get('MYSQL_DB', 'municipality_queue_db')
    # Optional path to mysqldump for backup service
    DBDUMP_PATH = os.environ.get('MYSQLDUMP_PATH')


    # SSO Settings
    SSO_CLIENT_ID = os.environ.get("SSO_CLIENT_ID")
    SSO_CLIENT_SECRET = os.environ.get("SSO_CLIENT_SECRET")
    SSO_AUTHORIZE_URL = os.environ.get("SSO_AUTHORIZE_URL")
    SSO_TOKEN_URL = os.environ.get("SSO_TOKEN_URL")
    SSO_USERINFO_URL = os.environ.get("SSO_USERINFO_URL")
    SSO_SECRET_KEY = os.environ.get("SSO_SECRET_KEY")
