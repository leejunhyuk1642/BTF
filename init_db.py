import sqlite3
DATABASE_FILE = "local_stores.db"
SCHEMA_FILE = "schema.sql"
def init_database():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        conn.commit()
        print(f"데이터베이스 '{DATABASE_FILE}' 가 '{SCHEMA_FILE}' 로부터 성공적으로 초기화되고, 테이블을 생성하였습니다.")
    except sqlite3.Error as e:
        print(f"데이터베이스 초기화 중 오류가 발생했습니다: {e}")
    except FileNotFoundError:
        print(f"'{SCHEMA_FILE}' 파일을 찾을 수 없습니다. 스키마 파일이 존재하는지 확인해주세요.")
    finally:
        if conn:
            conn.close()
if __name__ == "__main__":
    init_database()