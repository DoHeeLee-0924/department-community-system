-- 태그 분류 및 신뢰도 점수 기반 학과 정보공유 커뮤니티 관리 시스템
-- MySQL Workbench에서 실행할 수 있는 기본 스키마와 핵심 조회 쿼리

CREATE DATABASE IF NOT EXISTS department_community
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE department_community;

CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(100) NOT NULL,
    name VARCHAR(50),
    age VARCHAR(10),
    phone VARCHAR(20),
    sns_profile VARCHAR(50) UNIQUE NOT NULL,
    role ENUM('일반', '우수멘토', '학생회') DEFAULT '일반'
);

CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sns_profile VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    category ENUM('수업', '과제', '팀플', '공지', '취업') NOT NULL,
    likes INT DEFAULT 0,
    comments INT DEFAULT 0,
    view_count INT DEFAULT 0,
    archived TINYINT DEFAULT 0,
    FOREIGN KEY (sns_profile) REFERENCES users(sns_profile)
);

CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    sns_profile VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (sns_profile) REFERENCES users(sns_profile)
);

CREATE TABLE IF NOT EXISTS likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    sns_profile VARCHAR(50) NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (sns_profile) REFERENCES users(sns_profile),
    UNIQUE (post_id, sns_profile)
);

-- 핵심 조회 1: 태그별 게시글 조회
SELECT p.id, p.title, p.category, p.sns_profile, p.timestamp
FROM posts p
WHERE p.category = '과제' AND p.archived = 0
ORDER BY p.timestamp DESC;

-- 핵심 조회 2: 정보 신뢰도 점수 기반 상단 노출 조회
SELECT
    p.id,
    p.title,
    p.category,
    p.sns_profile AS writer,
    u.role,
    p.likes,
    p.comments,
    p.view_count,
    (
        CASE u.role
            WHEN '학생회' THEN 3.0
            WHEN '우수멘토' THEN 2.0
            ELSE 1.0
        END * 10
        + p.likes * 2
        + p.comments * 1
        + p.view_count * 0.1
    ) AS trust_score,
    CASE
        WHEN (
            CASE u.role
                WHEN '학생회' THEN 3.0
                WHEN '우수멘토' THEN 2.0
                ELSE 1.0
            END * 10
            + p.likes * 2
            + p.comments * 1
            + p.view_count * 0.1
        ) >= 30
        THEN '상단 노출'
        ELSE '일반 노출'
    END AS exposure_status
FROM posts p
JOIN users u ON p.sns_profile = u.sns_profile
WHERE p.archived = 0
ORDER BY
    CASE WHEN u.role = '학생회' AND p.category = '공지' THEN 1 ELSE 0 END DESC,
    trust_score DESC,
    p.timestamp DESC;
