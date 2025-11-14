-- =========================================================
-- RoboUsr MariaDB schema
-- Import this BEFORE running the application.
-- =========================================================
-- Persona definitions
CREATE TABLE
    IF NOT EXISTS persona_profile (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(50) NOT NULL UNIQUE,
        description TEXT,
        tone_formal INT DEFAULT 0,
        tone_funny INT DEFAULT 0,
        tone_angry INT DEFAULT 0,
        PRIMARY KEY (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Time-based persona mapping (HH:MM 24h format; optional DOW mask)
CREATE TABLE
    IF NOT EXISTS persona_schedule (
        id INT NOT NULL AUTO_INCREMENT,
        profile_id INT NOT NULL,
        start_time VARCHAR(5) NOT NULL,
        end_time VARCHAR(5) NOT NULL,
        dow_mask INT DEFAULT 127,
        PRIMARY KEY (id),
        INDEX idx_schedule_profile (profile_id),
        CONSTRAINT fk_schedule_profile FOREIGN KEY (profile_id) REFERENCES persona_profile (id) ON DELETE CASCADE
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Per-chat / per-user persona overrides
CREATE TABLE
    IF NOT EXISTS persona_override (
        id INT NOT NULL AUTO_INCREMENT,
        profile_id INT NOT NULL,
        chat_id VARCHAR(20) NULL,
        user_id VARCHAR(20) NULL,
        PRIMARY KEY (id),
        INDEX idx_override_profile (profile_id),
        INDEX idx_override_chat (chat_id),
        INDEX idx_override_user (user_id),
        CONSTRAINT fk_override_profile FOREIGN KEY (profile_id) REFERENCES persona_profile (id) ON DELETE CASCADE
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Conversation logs (timestamp stored as DATETIME to match ORM)
CREATE TABLE
    IF NOT EXISTS chat_log (
        id INT NOT NULL AUTO_INCREMENT,
        chat_id VARCHAR(20) NOT NULL,
        sender_id VARCHAR(20) NOT NULL,
        message_text TEXT NOT NULL,
        `timestamp` DATETIME NOT NULL,
        is_bot TINYINT (1) DEFAULT 0,
        PRIMARY KEY (id),
        INDEX idx_chat_log_chat (chat_id),
        INDEX idx_chat_log_time (`timestamp`)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;