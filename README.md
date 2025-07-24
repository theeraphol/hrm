# HRM

ระบบงานการเจ้าหน้าที่ตัวอย่าง พัฒนาโดยใช้ Python Flask

เวอร์ชัน: 0.16.0

## การเริ่มต้นใช้งาน

1. ติดตั้งแพ็กเกจที่จำเป็น (เช่นบน Windows ใช้คำสั่ง `py -m pip`)::

    py -m pip install -r requirements.txt

2. รันเซิร์ฟเวอร์พัฒนา::

    python app.py

เมื่อรันแล้วให้เปิด `http://localhost:4997/hrm/`

สร้างไฟล์ `.env` จาก `.env.example` และกำหนดค่าตัวแปรต่าง ๆ ก่อนรันแอป
แอปจะอ่านค่าการตั้งค่าจากไฟล์ `config.py` ซึ่งดึงข้อมูลจากตัวแปรสภาพแวดล้อม

แอปพลิเคชันมีหน้าใช้งานดังนี้

- `/hrm/` – หน้าหลักหลังเข้าสู่ระบบ
- `/hrm/attendance` – หน้าบันทึกเวลาเข้างาน/ออกงาน
- `/hrm/staff` – หน้าข้อมูลบุคลากร
- `/hrm/history` – หน้าประวัติพนักงาน
- `/hrm/projects` – หน้าโครงการ
- `/hrm/backup` – หน้าสำรองข้อมูล
- `/hrm/about` – หน้าเกี่ยวกับระบบ/คู่มือการใช้งาน


หากยังไม่ได้กำหนดค่า SSO สามารถทดสอบล็อกอินโดยระบุชื่อลงในพารามิเตอร์ `user` ของลิงก์ เช่น

```
http://localhost:4997/hrm/login?user=staff1
```

ระบบจะบันทึกชื่อที่ระบุไว้ในเซสชันและเปลี่ยนไปยังหน้าเจ้าหน้าที่ทันที
## การตั้งค่า SSO

ในตัวอย่างใหม่นี้ใช้กระบวนการ Single Sign-On (SSO) ผ่านมาตรฐาน OpenID
Connect โดยใช้ไลบรารี **Authlib**. ต้องกำหนดตัวแปรสภาพแวดล้อมดังนี้

- `SSO_CLIENT_ID`
- `SSO_CLIENT_SECRET`
- `SSO_AUTHORIZE_URL`
- `SSO_TOKEN_URL`
- `SSO_USERINFO_URL`
- `SSO_SECRET_KEY`

หลังจากกำหนดแล้วให้รัน `python app.py` ตามปกติ

## การตั้งค่าฐานข้อมูล MariaDB

โค้ดตัวอย่างเชื่อมต่อฐานข้อมูล MariaDB ผ่านไลบรารี **PyMySQL**
และใช้สคริปต์ `schema.sql` เพื่อสร้างตารางที่จำเป็น
ให้ตั้งค่าตัวแปรสภาพแวดล้อมดังนี้ (ไฟล์ `config.py` จะอ่านค่าต่าง ๆ จากตัวแปรเหล่านี้)

- `MYSQL_HOST` – ชื่อโฮสต์ของฐานข้อมูล (เช่น `localhost`)
- `MYSQL_PORT` – พอร์ตของ MariaDB (ค่าเริ่มต้น `3306`)
- `MYSQL_USER` – ชื่อผู้ใช้ฐานข้อมูล
- `MYSQL_PASSWORD` – รหัสผ่านของฐานข้อมูล (รองรับตัวแปรเดิม `MYSQL_PW`)
- `MYSQL_DB` – ชื่อฐานข้อมูล (ตรงกับที่สร้างไว้ใน `schema.sql` เช่น `hrm`)
- `MYSQLDUMP_PATH` – เส้นทางคำสั่ง `mysqldump` (ถ้าต้องการใช้บริการสำรองข้อมูล)
- `SECRET_KEY` – คีย์ลับสำหรับ Flask ใช้เซ็นคุกกี้ หากไม่ตั้งค่าจะมีค่าเริ่มต้นในโค้ด
- `PORT` – พอร์ตที่เซิร์ฟเวอร์ Flask จะรัน (ค่าเริ่มต้น `4997`)

รันคำสั่งใน `schema.sql` บนเซิร์ฟเวอร์ MariaDB ก่อนเริ่มใช้งาน

### การแก้ไขปัญหา Authentication plugin `auth_gssapi_client`

หากเชื่อมต่อฐานข้อมูลแล้วเกิดข้อผิดพลาดลักษณะ
`(2059, "Authentication plugin 'b'auth_gssapi_client'' not configured")`
ให้ปรับผู้ใช้ใน MariaDB ให้ใช้ปลั๊กอิน `mysql_native_password` ตัวอย่างเช่น:

```sql
ALTER USER 'youruser'@'localhost'
    IDENTIFIED VIA mysql_native_password USING PASSWORD('yourpassword');
```

เมื่อใช้งานปลั๊กอินดังกล่าวจะสามารถเชื่อมต่อผ่าน PyMySQL ได้ตามปกติ

## License

Released under the MIT License.
