import os
import psycopg2
from psycopg2 import Error


def run_migrations():
    try:
        # Connect to your PostgreSQL database
        conn = psycopg2.connect(
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_NAME"]
        )

        conn.autocommit = False  # We'll commit manually at the end
        cur = conn.cursor()

        print("Running migrations...")

        # ────────────────────────────────────────────────
        # Complete migration script – pure PostgreSQL
        # ────────────────────────────────────────────────
        migration_sql = """
        -- 1. Enable UUID extension
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


        -- 2. Drop tables in reverse dependency order (mainly for dev/reset)
        DROP TABLE IF EXISTS user_roles     CASCADE;
        DROP TABLE IF EXISTS members        CASCADE;
        DROP TABLE IF EXISTS operators      CASCADE;
        DROP TABLE IF EXISTS organisations  CASCADE;
        DROP TABLE IF EXISTS roles          CASCADE;


        -- 3. ROLES (static seed data)
        CREATE TABLE roles (
            id   uuid PRIMARY KEY,
            name text NOT NULL UNIQUE
        );

        INSERT INTO roles (id, name) VALUES
            (uuid_generate_v5(uuid_nil(), 'member'),             'member'),
            (uuid_generate_v5(uuid_nil(), 'parent'),             'parent'),
            (uuid_generate_v5(uuid_nil(), 'operator'),           'operator'),
            (uuid_generate_v5(uuid_nil(), 'organisation_admin'), 'organisation_admin')
        ON CONFLICT (name) DO NOTHING;


        -- 4. ORGANISATIONS
        CREATE TABLE organisations (
            id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
            name       text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now()
        );


        -- 5. OPERATORS
        CREATE TABLE operators (
            id              uuid PRIMARY KEY,
            username        text NOT NULL,
            organisation_id uuid NOT NULL,
            created_at      timestamptz NOT NULL DEFAULT now(),

            CONSTRAINT fk_operator_user
                FOREIGN KEY (id)
                REFERENCES auth.users(id)
                ON DELETE CASCADE,

            CONSTRAINT fk_operator_organisation
                FOREIGN KEY (organisation_id)
                REFERENCES organisations(id)
                ON DELETE CASCADE,

            CONSTRAINT operators_id_organisation_unique
                UNIQUE (id, organisation_id)
        );

        CREATE INDEX idx_operators_organisation_id
            ON operators(organisation_id);


        -- 6. MEMBERS
        CREATE TABLE members (
            id              uuid PRIMARY KEY,
            operator_id     uuid NOT NULL,
            organisation_id uuid NOT NULL,
            username        text NOT NULL UNIQUE,
            first_name      text NOT NULL,
            created_at      timestamptz NOT NULL DEFAULT now(),

            CONSTRAINT fk_member_user
                FOREIGN KEY (id)
                REFERENCES auth.users(id)
                ON DELETE CASCADE,

            CONSTRAINT fk_member_operator_org
                FOREIGN KEY (operator_id, organisation_id)
                REFERENCES operators(id, organisation_id)
                ON DELETE CASCADE
        );

        CREATE INDEX idx_members_operator_id
            ON members(operator_id);

        CREATE INDEX idx_members_organisation_id
            ON members(organisation_id);


        -- 7. USER_ROLES (scoped many-to-many)
        CREATE TABLE user_roles (
            user_id         uuid NOT NULL,
            role_id         uuid NOT NULL
                REFERENCES roles(id)
                ON DELETE CASCADE,
            organisation_id uuid NOT NULL
                REFERENCES organisations(id)
                ON DELETE CASCADE,

            PRIMARY KEY (user_id, role_id, organisation_id),

            CONSTRAINT fk_user_roles_user
                FOREIGN KEY (user_id)
                REFERENCES auth.users(id)
                ON DELETE CASCADE
        );

        CREATE INDEX idx_user_roles_user_id
            ON user_roles(user_id);

        CREATE INDEX idx_user_roles_role_id
            ON user_roles(role_id);

        CREATE INDEX idx_user_roles_organisation_id
            ON user_roles(organisation_id);


        -- 8. Very permissive RLS (development only – tighten for production!)
        ALTER TABLE organisations ENABLE ROW LEVEL SECURITY;
        ALTER TABLE user_roles     ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "dev_read_all_organisations"
            ON organisations FOR SELECT
            USING (true);

        CREATE POLICY "dev_read_all_user_roles"
            ON user_roles FOR SELECT
            USING (true);
        """

        cur.execute(migration_sql)

        conn.commit()
        print("Migrations completed successfully.")

    except Error as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.rollback()

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    run_migrations()