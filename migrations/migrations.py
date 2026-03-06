import os
from urllib.parse import urlparse

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
-- 1️⃣ Enable UUID extension
-- =========================================
create extension if not exists "uuid-ossp";


-- =========================================
-- 2️⃣ ROLES TABLE
-- =========================================
drop table if exists user_roles cascade;
drop table if exists roles cascade;

create table roles (
    id uuid primary key,
    name text not null unique
);

insert into roles (id, name) values
    (uuid_generate_v5(uuid_nil(), 'member'), 'member'),
    (uuid_generate_v5(uuid_nil(), 'parent'), 'parent'),
    (uuid_generate_v5(uuid_nil(), 'operator'), 'operator');


-- =========================================
-- 3️⃣ LICENSE HOLDERS (1-to-1 with auth.users)
-- =========================================
create table if not exists license_holders (
    id uuid primary key
        references auth.users(id)
        on delete cascade,
    created_at timestamptz default now()


);


-- =========================================
-- 4️⃣ MEMBERS
-- =========================================
create table if not exists members (
    id uuid primary key
        references auth.users(id)
        on delete cascade,

    license_holder_id uuid not null
        references license_holders(id)
        on delete cascade,

    username text not null unique,
    first_name text not null,
    created_at timestamptz default now()
);


-- =========================================
-- 5️⃣ UNIFIED USER_ROLES (THE IMPORTANT PART)
-- =========================================
create table if not exists user_roles (
    user_id uuid
        references auth.users(id)
        on delete cascade,

    role_id uuid
        references roles(id)
        on delete cascade,

    primary key (user_id, role_id)
);

create index if not exists idx_user_roles_user_id
    on user_roles(user_id);

create index if not exists idx_user_roles_role_id
    on user_roles(role_id);
    """)
    print("Migrations completed successfully.")
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_migrations()
