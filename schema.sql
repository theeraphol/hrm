-- Municipality queue database schema
-- สร้างฐานข้อมูล
CREATE DATABASE IF NOT EXISTS municipality_queue_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE municipality_queue_db;

-- ตารางผู้มารับบริการ
CREATE TABLE citizens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_id CHAR(13) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    birth_date DATE,
    address TEXT,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    person_type ENUM('ทั่วไป', 'ผู้สูงอายุ', 'ผู้พิการ', 'ข้าราชการ', 'ตัวแทน') DEFAULT 'ทั่วไป'
);

-- ตารางหน่วยงาน (กอง/ฝ่าย)
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- ตารางประเภทงานบริการ (ระดับกลาง)
CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- ตารางหัวข้อย่อยของบริการ (งานเฉพาะ)
CREATE TABLE service_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (service_id) REFERENCES services(id)
);

-- ตารางคิวและการให้บริการ
CREATE TABLE queues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    citizen_id INT NOT NULL,
    department_id INT NOT NULL,
    service_id INT NOT NULL,
    service_topic_id INT,
    queue_number VARCHAR(10) NOT NULL,
    service_date DATE NOT NULL,
    checkin_time DATETIME,
    called_time DATETIME,
    service_time_start DATETIME,
    service_time_end DATETIME,
    service_status ENUM('รอเรียก', 'ให้บริการแล้ว', 'ยกเลิก', 'ไม่มา') DEFAULT 'รอเรียก',
    service_channel ENUM('มาหน้าเคาน์เตอร์', 'จองผ่านแอป', 'โทรศัพท์', 'ตู้คีออส') DEFAULT 'มาหน้าเคาน์เตอร์',
    staff_name VARCHAR(100),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (service_topic_id) REFERENCES service_topics(id)
);

-- ตารางความคิดเห็นและประเมินผล
CREATE TABLE feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    queue_id INT NOT NULL,
    satisfaction_score INT CHECK (satisfaction_score BETWEEN 1 AND 5),
    feedback_comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (queue_id) REFERENCES queues(id)
);
