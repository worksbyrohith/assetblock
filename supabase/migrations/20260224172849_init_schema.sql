-- AssetBlock Database Schema
-- Initial Migration

CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    uid         VARCHAR(128) UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    username    VARCHAR(100),
    role        VARCHAR(20) DEFAULT 'client',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
    id          SERIAL PRIMARY KEY,
    asset_name  VARCHAR(255) NOT NULL,
    hash        VARCHAR(64) UNIQUE NOT NULL,
    file_type   VARCHAR(50),
    file_size   BIGINT DEFAULT 0,
    description TEXT DEFAULT '',
    status      VARCHAR(20) DEFAULT 'Active',
    owner_uid   VARCHAR(128) REFERENCES users(uid) ON DELETE SET NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transfer_history (
    id              SERIAL PRIMARY KEY,
    asset_id        INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    from_uid        VARCHAR(128),
    to_uid          VARCHAR(128),
    from_email      VARCHAR(255),
    to_email        VARCHAR(255),
    transferred_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note            TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS activity_log (
    id          SERIAL PRIMARY KEY,
    uid         VARCHAR(128),
    email       VARCHAR(255),
    action      VARCHAR(100),
    details     TEXT DEFAULT '',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
