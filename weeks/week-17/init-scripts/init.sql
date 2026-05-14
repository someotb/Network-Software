-- Tickets Database Initialization Script

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    priority INTEGER DEFAULT 3 CHECK (priority >= 1 AND priority <= 5),
    assignee_id INTEGER,
    reporter_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_assignee ON tickets(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tickets_reporter ON tickets(reporter_id);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at DESC);

-- Insert sample data
INSERT INTO tickets (title, description, status, priority, assignee_id, reporter_id) VALUES
    ('Setup development environment', 'Install all required tools and dependencies', 'new', 3, NULL, 1),
    ('Fix login bug', 'Users cannot login with special characters in password', 'in_progress', 5, 2, 1),
    ('Add dark mode', 'Implement dark theme for the application', 'new', 2, NULL, 3),
    ('Database migration', 'Migrate from MySQL to PostgreSQL', 'resolved', 4, 2, 1),
    ('Update documentation', 'Add API documentation for new endpoints', 'closed', 1, 3, 2);
-- Users Database Initialization Script

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'agent', 'user')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Insert sample users (password is 'password123' hashed with bcrypt)
INSERT INTO users (username, email, password_hash, role) VALUES
    ('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6', 'admin'),
    ('agent1', 'agent1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6', 'agent'),
    ('user1', 'user1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6', 'user');
