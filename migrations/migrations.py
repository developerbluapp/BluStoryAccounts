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
    print("Migrations completed successfully.")
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_migrations()
