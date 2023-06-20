CREATE SCHEMA IF NOT EXISTS auth;

CREATE TABLE IF NOT EXISTS auth.user (
    id uuid PRIMARY KEY,
    login TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS auth.role (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS auth.user_profile (
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL,
    registration_dt TIMESTAMP WITH TIME ZONE,
    active BOOLEAN NOT NULL,
    is_staff BOOLEAN NOT NULL,
    role_id TEXT NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.user (id) ON DELETE CASCADE,
    CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES auth.role (id) ON DELETE PROTECT
);

CREATE TABLE IF NOT EXISTS auth.login_history (
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL,
    user_agent TEXT,
    login_dt TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.user (id) ON DELETE CASCADE
);