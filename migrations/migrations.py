import os
import psycopg2
from psycopg2 import Error

def run_migrations():
    conn = None
    try:
        # 1. Environment-aware connection logic
        env = os.getenv("ENVIRONMENT", "development")
        prefix = "TEST_" if env == "test" else ""
        
        conn = psycopg2.connect(
            user=os.environ[prefix + "DB_USER"],
            password=os.environ[prefix + "DB_PASSWORD"],
            host=os.environ[prefix + "DB_HOST"],
            port=os.environ[prefix + "DB_PORT"],
            dbname=os.environ[prefix + "DB_NAME"]
        )

        conn.autocommit = False
        cur = conn.cursor()

        print(f"Running migrations for environment: {env}...")

        # 2. The Universal SQL Script
        migration_sql = """
        -- =========================================
        -- 1. SUPABASE COMPATIBILITY LAYER
        -- =========================================
        -- On local PG, this creates the missing 'auth' schema.
        -- On Supabase, this does nothing.
        CREATE SCHEMA IF NOT EXISTS auth;
        
        CREATE TABLE IF NOT EXISTS auth.users (
            id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
            email       text UNIQUE,
            created_at  timestamptz DEFAULT now()
        );

        -- Enable UUID extension
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        -- =========================================
        -- 2. CLEANUP (Reverse Dependency Order)
        -- =========================================
        DROP TABLE IF EXISTS user_roles     CASCADE;
        DROP TABLE IF EXISTS members        CASCADE;
        DROP TABLE IF EXISTS operators      CASCADE;
        DROP TABLE IF EXISTS organisations  CASCADE;
        DROP TABLE IF EXISTS roles          CASCADE;

        -- =========================================
        -- 3. TABLES
        -- =========================================
        
        CREATE TABLE roles (
            id   uuid PRIMARY KEY,
            name text NOT NULL UNIQUE
        );

        INSERT INTO roles (id, name) VALUES
            (uuid_generate_v5(uuid_nil(), 'member'),             'member'),
            (uuid_generate_v5(uuid_nil(), 'parent'),             'parent'),
            (uuid_generate_v5(uuid_nil(), 'operator'),           'operator'),
            (uuid_generate_v5(uuid_nil(), 'organisation_admin'), 'organisation_admin')
        ON CONFLICT (id) DO NOTHING;

        CREATE TABLE organisations (
            id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
            name       text NOT NULL,
            created_at timestamptz DEFAULT now()
        );

        CREATE TABLE operators (
            id              uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
            username        text NOT NULL,
            organisation_id uuid NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
            created_at      timestamptz DEFAULT now(),
            UNIQUE (id, organisation_id)
        );

        CREATE TABLE members (
            id              uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
            operator_id     uuid NOT NULL,
            organisation_id uuid NOT NULL,
            username        text NOT NULL UNIQUE,
            first_name      text NOT NULL,
            created_at      timestamptz DEFAULT now(),
            FOREIGN KEY (operator_id, organisation_id) 
                REFERENCES operators(id, organisation_id) ON DELETE CASCADE
        );

        CREATE TABLE user_roles (
            user_id         uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            role_id         uuid NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            organisation_id uuid NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, role_id, organisation_id)
        );

        -- =========================================
        -- 4. RLS POLICIES
        -- =========================================
        ALTER TABLE organisations ENABLE ROW LEVEL SECURITY;
        ALTER TABLE user_roles     ENABLE ROW LEVEL SECURITY;

        -- 'TO public' works in both standard PG and Supabase
        CREATE POLICY "read_organisations" ON organisations FOR SELECT TO public USING (true);
        CREATE POLICY "read_user_roles" ON user_roles FOR SELECT TO public USING (true);
        """

        cur.execute(migration_sql)
        conn.commit()
        print("Migrations completed successfully.")

    except Error as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    run_migrations()