import os

class Config:
    """การตั้งค่าสำหรับแอปพลิเคชัน"""

    VERSION = "0.16.0"

    # คีย์ลับสำหรับ Flask ต้องกำหนดผ่านตัวแปรสภาพแวดล้อมเท่านั้น
    SECRET_KEY = os.environ.get("BST-bangsithong-app-SECRET_KEY-024467684")

    # Database
    DB_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    DB_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    DB_USER = os.environ.get('MYSQL_USER', 'root')
    # กำหนดรหัสผ่านฐานข้อมูลผ่านตัวแปรสภาพแวดล้อม
    # รองรับตัวแปรเดิมที่อาจยังใช้งานอยู่ด้วย
    DB_PASSWORD = os.environ.get('MYSQL_PASSWORD','987654321') or os.environ.get('MYSQL_PW')
    # ค่าดีฟอลต์ตรงกับฐานข้อมูลที่สร้างจาก schema.sql
    DB_NAME = os.environ.get('MYSQL_DB', 'hrm')
    # Optional path to mysqldump for backup service
    DBDUMP_PATH = os.environ.get('MYSQLDUMP_PATH')

    # Server
    SERVER_PORT = int(os.environ.get('PORT', 4997))


    # SSO Settings
    SSO_CLIENT_ID = os.environ.get("SSO_CLIENT_ID")
    SSO_CLIENT_SECRET = os.environ.get("SSO_CLIENT_SECRET")
    SSO_AUTHORIZE_URL = os.environ.get("SSO_AUTHORIZE_URL")
    SSO_TOKEN_URL = os.environ.get("SSO_TOKEN_URL")
    SSO_USERINFO_URL = os.environ.get("SSO_USERINFO_URL")
    SSO_SECRET_KEY = os.environ.get("SSO_SECRET_KEY")
