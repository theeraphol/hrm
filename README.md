# service_queue

ตัวอย่างระบบจองบัตรคิวด้วย Python Flask

เวอร์ชัน: 0.5.0

## การเริ่มต้นใช้งาน

1. ติดตั้งแพ็กเกจที่จำเป็น (เช่นบน Windows ใช้คำสั่ง `py -m pip`)::

    py -m pip install -r requirements.txt

2. รันเซิร์ฟเวอร์พัฒนา::

    python app.py

เมื่อรันแล้วให้เปิด `http://localhost:5000/service_queue/`

แอปพลิเคชันมีหน้าใช้งานดังนี้

- `/service_queue/` – หน้าสำหรับประชาชนกดรับบัตรคิว (กรอกหมายเลขบัตรประชาชน)
- `/service_queue/staff` – หน้าสำหรับเจ้าหน้าที่ดูรายการคิว (ต้องล็อกอินผ่าน `/service_queue/login`)
- `/service_queue/staff/call` – หน้าสำหรับเจ้าหน้าที่กดเรียกคิวถัดไป

## การตั้งค่า SSO

ในตัวอย่างใหม่นี้ใช้กระบวนการ Single Sign-On (SSO) ผ่านมาตรฐาน OpenID
Connect โดยใช้ไลบรารี **Authlib**. ต้องกำหนดตัวแปรสภาพแวดล้อมดังนี้

- `SSO_CLIENT_ID`
- `SSO_CLIENT_SECRET`
- `SSO_AUTHORIZE_URL`
- `SSO_TOKEN_URL`
- `SSO_USERINFO_URL`

หลังจากกำหนดแล้วให้รัน `python app.py` ตามปกติ

## การตั้งค่าฐานข้อมูล MariaDB

โค้ดตัวอย่างเชื่อมต่อฐานข้อมูล MariaDB ผ่านไลบรารี **PyMySQL**
และใช้สคริปต์ `schema.sql` เพื่อสร้างตารางที่จำเป็น
ให้ตั้งค่าตัวแปรสภาพแวดล้อมดังนี้

- `DB_HOST` – ชื่อโฮสต์ของฐานข้อมูล (เช่น `localhost`)
- `DB_PORT` – พอร์ตของ MariaDB (ค่าเริ่มต้น `3306`)
- `DB_USER` – ชื่อผู้ใช้ฐานข้อมูล
- `DB_PASSWORD` – รหัสผ่านของฐานข้อมูล
- `DB_NAME` – ชื่อฐานข้อมูล (ต้องตรงกับที่สร้างไว้ใน `schema.sql`)

รันคำสั่งใน `schema.sql` บนเซิร์ฟเวอร์ MariaDB ก่อนเริ่มใช้งาน
