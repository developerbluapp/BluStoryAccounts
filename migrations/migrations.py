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
        create table if not exists students (
            id uuid primary key references auth.users(id) on delete cascade,
            license_holder_id uuid not null,
            username text not null,
            created_at timestamptz default now()
        );
    """)
    cur.execute("""
-- 1. Enable the extension
create extension if not exists "uuid-ossp";

-- 2. Drop the old integer-based table if it exists 
-- (Warning: This deletes existing role data, which is fine for 4 default roles)
drop table if exists roles cascade;

-- 3. Create roles table with the correct UUID type
create table roles (
    id uuid primary key, 
    name text not null unique
);

-- 4. Insert using UUID v5 (Deterministic Hashes)
insert into roles (id, name) values
    (uuid_generate_v5(uuid_nil(), 'student'), 'student'),
    (uuid_generate_v5(uuid_nil(), 'parent'), 'parent'),
    (uuid_generate_v5(uuid_nil(), 'licenseholder'), 'licenseholder');

-- 5. Add/Alter the students table
-- If the column exists as an int, we drop it and add it as UUID
alter table students drop column if exists role_id;

alter table students
add column role_id uuid 
references roles(id) 
on delete set null 
default uuid_generate_v5(uuid_nil(), 'student');

-- 6. Re-create the index
create index if not exists idx_students_role_id on students(role_id);
    """)
    print("Migrations completed successfully.")
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_migrations()
