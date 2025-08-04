-- HRM database schema
CREATE DATABASE IF NOT EXISTS hrm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hrm;

-- หน่วยงาน
CREATE TABLE IF NOT EXISTS departments (
    dept_code VARCHAR(20) PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO departments (dept_code, dept_name) VALUES
    ('1','สำนักปลัด'),
    ('2','กองคลัง'),
    ('3','กองช่าง'),
    ('4','กองสาธารณสุขและสิ่งแวดล้อม'),
    ('5','กองการศึกษา'),
    ('6','กองสวัสดิการสังคม');

-- ข้อมูลบุคลากร
CREATE TABLE IF NOT EXISTS staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_id CHAR(13) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    position VARCHAR(100),
    department VARCHAR(100),
    division VARCHAR(100),
    start_date DATE,
    note TEXT,
    email VARCHAR(100),
    phone VARCHAR(20)
);
-- เพิ่มคอลัมน์ในกรณีอัพเกรดระบบ
ALTER TABLE staff
    ADD COLUMN IF NOT EXISTS division VARCHAR(100),
    ADD COLUMN IF NOT EXISTS note TEXT,
    ADD COLUMN IF NOT EXISTS email VARCHAR(100),
    ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- บันทึกเวลาเข้างาน/ออกงาน
CREATE TABLE IF NOT EXISTS attendances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    checkin_time DATETIME,
    checkout_time DATETIME,
    work_status TINYINT DEFAULT 2,
    note TEXT,
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);
-- เพิ่มคอลัมน์สถานะการทำงานหากยังไม่มี
ALTER TABLE attendances
    ADD COLUMN IF NOT EXISTS work_status TINYINT DEFAULT 2;

-- การลา
CREATE TABLE IF NOT EXISTS leaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    start_date DATE,
    end_date DATE,
    leave_type ENUM('ลาป่วย','ลากิจ','ลาพักร้อน','อื่นๆ') DEFAULT 'ลากิจ',
    reason TEXT,
    status ENUM('รอดำเนินการ','อนุมัติ','ไม่อนุมัติ') DEFAULT 'รอดำเนินการ',
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

-- อบรม/ดูงาน
CREATE TABLE IF NOT EXISTS trainings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    topic VARCHAR(200),
    place VARCHAR(200),
    start_date DATE,
    end_date DATE,
    description TEXT,
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

-- กิจกรรมอื่น ๆ
CREATE TABLE IF NOT EXISTS activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    activity_name VARCHAR(200),
    activity_date DATE,
    description TEXT,
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

-- โครงการ
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(200) NOT NULL,
    start_date DATE,
    end_date DATE,
    status VARCHAR(100),
    description TEXT
);

-- พฤติกรรม/หมายเหตุ
CREATE TABLE IF NOT EXISTS behaviors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    behavior_date DATE,
    description TEXT,
    note TEXT,
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

-- ประวัติพนักงาน
CREATE TABLE IF NOT EXISTS employee_histories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_id CHAR(13) NOT NULL,
    full_name VARCHAR(100),
    position VARCHAR(100),
    department VARCHAR(100),
    division VARCHAR(100),
    start_date DATE,
    email VARCHAR(100),
    note TEXT,
    phone VARCHAR(20)
);
-- ตารางนี้อาจถูกเพิ่มในภายหลัง จึงใช้ ALTER TABLE เพื่อเพิ่มคอลัมน์ใหม่เมื่อจำเป็น
ALTER TABLE employee_histories
    ADD COLUMN IF NOT EXISTS email VARCHAR(100),
    ADD COLUMN IF NOT EXISTS division VARCHAR(100),
    ADD COLUMN IF NOT EXISTS note TEXT,
    ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
