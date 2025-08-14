# ------------------------------
# file: meeting_assistant/db/migrations.sql
# ------------------------------
-- Run this once to set up schema
CREATE TABLE IF NOT EXISTS sessions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  uuid VARCHAR(64) NOT NULL UNIQUE,
  title VARCHAR(255) DEFAULT '',
  main_topic VARCHAR(255) DEFAULT '',
  start_time DATETIME,
  end_time DATETIME,
  duration_min INT DEFAULT 0,
  status VARCHAR(32) DEFAULT 'idle',
  audio_path VARCHAR(512) DEFAULT ''
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS transcripts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_uuid VARCHAR(64) NOT NULL,
  full_text LONGTEXT,
  summary TEXT,
  goal JSON,
  agenda JSON,
  attendance JSON,
  decisions JSON,
  action_items JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_uuid) REFERENCES sessions(uuid) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
