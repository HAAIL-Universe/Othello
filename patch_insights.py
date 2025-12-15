from dotenv import load_dotenv
from db.database import init_pool, get_pool


def main():
    load_dotenv()
    init_pool()
    pool = get_pool()
    conn = pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("ALTER TABLE insights ADD COLUMN IF NOT EXISTS user_id TEXT")
        cur.execute("ALTER TABLE insights ALTER COLUMN user_id SET DEFAULT '1'")
        cur.execute("UPDATE insights SET user_id = '1' WHERE user_id IS NULL")
        cur.execute("ALTER TABLE insights ALTER COLUMN user_id SET NOT NULL")
        cur.execute("ALTER TABLE insights ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at::timestamptz")
        cur.execute("ALTER TABLE insights ALTER COLUMN created_at SET DEFAULT NOW()")
        conn.commit()
        print("patched insights table")
    finally:
        pool.putconn(conn)


if __name__ == "__main__":
    main()
