import os
import psycopg2


def run_migrations():
    conn = psycopg2.connect(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"]
    )
    cur = conn.cursor()
    print("Running migrations...")

    cur.execute("""
-- =========================================
-- Enable UUID extension
-- =========================================
create extension if not exists "uuid-ossp";


-- =========================================
-- Drop tables (for dev reset)
-- =========================================
drop table if exists user_roles cascade;
drop table if exists members cascade;
drop table if exists operators cascade;
drop table if exists organisations cascade;
drop table if exists roles cascade;


-- =========================================
-- ROLES
-- =========================================
create table roles (
    id uuid primary key,
    name text not null unique
);

insert into roles (id, name) values
(uuid_generate_v5(uuid_nil(), 'member'), 'member'),
(uuid_generate_v5(uuid_nil(), 'parent'), 'parent'),
(uuid_generate_v5(uuid_nil(), 'operator'), 'operator');


-- =========================================
-- ORGANISATIONS
-- =========================================
create table organisations (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    created_at timestamptz default now()
);


-- =========================================
-- OPERATORS (belong to organisation)
-- =========================================
create table operators (
    id uuid primary key
        references auth.users(id)
        on delete cascade,

    organisation_id uuid not null
        references organisations(id)
        on delete cascade,

    created_at timestamptz default now()
);

create index idx_operator_org
    on operators(organisation_id);


-- =========================================
-- MEMBERS (belong to operator)
-- =========================================
create table members (
    id uuid primary key
        references auth.users(id)
        on delete cascade,

    operator_id uuid not null
        references operators(id)
        on delete cascade,

    username text not null unique,
    first_name text not null,

    created_at timestamptz default now()
);

create index idx_member_operator
    on members(operator_id);


-- =========================================
-- USER ROLES
-- =========================================
create table user_roles (
    user_id uuid
        references auth.users(id)
        on delete cascade,

    role_id uuid
        references roles(id)
        on delete cascade,

    primary key (user_id, role_id)
);

create index idx_user_roles_user_id
    on user_roles(user_id);

create index idx_user_roles_role_id
    on user_roles(role_id);

    """)

    print("Migrations completed successfully.")

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    run_migrations()