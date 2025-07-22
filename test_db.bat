# 1. สร้างและเปิดใช้ virtualenv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. ติดตั้งไลบรารี
pip install -r requirements.txt

# 3. กำหนดตัวแปรสภาพแวดล้อมสำหรับการเชื่อมต่อ MySQL/MariaDB
$env:SECRET_KEY    = [guid]::NewGuid().ToString("N")
$env:MYSQL_HOST    = "localhost"
$env:MYSQL_USER    = "root"
$env:MYSQL_PASSWORD = "987654321"
$env:MYSQL_DB      = "municipality_queue_db"

# 4. ทดสอบการเชื่อมต่อ
python -c "
from app import get_connection
conn = get_connection()
cur = conn.cursor()
cur.execute('SELECT VERSION()')
print('เชื่อมต่อสำเร็จ:', cur.fetchone())
conn.close()
"