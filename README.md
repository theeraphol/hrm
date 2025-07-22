# service_queue

ตัวอย่างระบบจองบัตรคิวด้วย Python Flask

## การเริ่มต้นใช้งาน

1. ติดตั้งแพ็กเกจที่จำเป็น::

    pip install -r requirements.txt

2. รันเซิร์ฟเวอร์พัฒนา::

    python app.py

แอปพลิเคชันมีหน้าใช้งานดังนี้

- `/` – หน้าสำหรับประชาชนกดรับบัตรคิว (กรอกหมายเลขบัตรประชาชน)
- `/staff` – หน้าสำหรับเจ้าหน้าที่ดูรายการคิว (ต้องล็อกอินผ่าน `/login`)
- `/staff/call` – หน้าสำหรับเจ้าหน้าที่กดเรียกคิวถัดไป

## การตั้งค่า SSO

ในตัวอย่างใหม่นี้ใช้กระบวนการ Single Sign-On (SSO) ผ่านมาตรฐาน OpenID
Connect โดยใช้ไลบรารี **Authlib**. ต้องกำหนดตัวแปรสภาพแวดล้อมดังนี้

- `SSO_CLIENT_ID`
- `SSO_CLIENT_SECRET`
- `SSO_AUTHORIZE_URL`
- `SSO_TOKEN_URL`
- `SSO_USERINFO_URL`

หลังจากกำหนดแล้วให้รัน `python app.py` ตามปกติ
