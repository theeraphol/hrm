-- HRM database schema
CREATE DATABASE IF NOT EXISTS hrm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hrm;

-- ข้อมูลบุคลากร
CREATE TABLE IF NOT EXISTS staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_id CHAR(13) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    position VARCHAR(100),
    department VARCHAR(100),
    start_date DATE,
    email VARCHAR(100),
    phone VARCHAR(20)
);

-- บันทึกเวลาเข้างาน/ออกงาน
CREATE TABLE IF NOT EXISTS attendances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    checkin_time DATETIME,
    checkout_time DATETIME,
    note TEXT,
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

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
    note TEXT,
    phone VARCHAR(20)
);
