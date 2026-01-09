-- =============================================================================
-- PyService Mini-ITSM Platform - MySQL Initialization Script
-- Creates database with proper character set and initial configuration
-- =============================================================================

-- Use utf8mb4 for full unicode support
CREATE DATABASE IF NOT EXISTS pyservice_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Grant privileges to application user
GRANT ALL PRIVILEGES ON pyservice_db.* TO 'pyservice'@'%';
FLUSH PRIVILEGES;

-- Display success message
SELECT 'PyService database initialized successfully!' AS status;
