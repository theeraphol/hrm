# ทดสอบการเชื่อมต่อฐานข้อมูลด้วย PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:SECRET_KEY    = [guid]::NewGuid().ToString('N')
$env:MYSQL_HOST    = 'localhost'
$env:MYSQL_USER    = 'root'
$env:MYSQL_PASSWORD = 'change_me'
$env:MYSQL_DB      = 'municipality_queue_db'

python -c "from app import get_connection; conn = get_connection(); cur = conn.cursor(); cur.execute('SELECT VERSION()'); print('เชื่อมต่อสำเร็จ:', cur.fetchone()); conn.close()"
