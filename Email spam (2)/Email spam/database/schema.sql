-- Email Spam Detection System PostgreSQL Schema

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'USER' CHECK (role IN ('USER', 'ADMIN')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Email Detections Table
CREATE TABLE IF NOT EXISTS email_detections (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    prediction VARCHAR(20) NOT NULL CHECK (prediction IN ('Spam', 'Not Spam')),
    spam_probability DOUBLE PRECISION NOT NULL,
    not_spam_probability DOUBLE PRECISION NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('Safe', 'Suspicious', 'High Risk')),
    reasons JSONB DEFAULT '[]'::jsonb,
    url_count INT DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    detection_id INT NOT NULL REFERENCES email_detections(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    feedback VARCHAR(20) NOT NULL CHECK (feedback IN ('Correct', 'Incorrect')),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_detection_feedback UNIQUE (detection_id, user_id)
);

-- Model Metrics Table
CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    accuracy DOUBLE PRECISION NOT NULL,
    precision_score DOUBLE PRECISION NOT NULL,
    recall_score DOUBLE PRECISION NOT NULL,
    f1_score DOUBLE PRECISION NOT NULL,
    train_samples INT NOT NULL,
    test_samples INT NOT NULL,
    confusion_matrix JSONB NOT NULL,
    evaluated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_detections_user_id ON email_detections(user_id);
CREATE INDEX IF NOT EXISTS idx_detections_created_at ON email_detections(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_detections_prediction ON email_detections(prediction);
CREATE INDEX IF NOT EXISTS idx_feedback_detection_id ON feedback(detection_id);

-- Insert Default Accounts if they do not exist
INSERT INTO users (name, email, password_hash, role, is_active)
VALUES 
    ('Security Admin', 'admin@spamshield.com', 'scrypt:32768:8:1$YPCjqLhsEZ7tknNR$befe2890eb2b8cd96df957e23acd083313af2979cea95423a74b38dd7277f2fa66d1316561945f9d2788ca59dff4bd27b4baeaba2604eab4c31fc5368c1c208c', 'ADMIN', TRUE),
    ('Demo Analyst', 'user@demo.com', 'scrypt:32768:8:1$Zfr299nbbotcuJCz$18956766e814b2515a1d46c80ac5629fb906ff5fe7ba300d25b79adc279ca3d202d498a8fbb0a3a3db308753dda35fadbbdf191e7c7cb3967b93c2585a933837', 'USER', TRUE)
ON CONFLICT (email) DO NOTHING;
