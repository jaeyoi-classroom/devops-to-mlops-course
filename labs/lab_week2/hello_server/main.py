from flask import Flask
import psycopg2

app = Flask(__name__)

#
# 기본 실습
#

@app.route("/")
def hello_docker():
    return "<p>Hello, Docker!</p>"


#
# Database 연동 실습
# 

def get_db_connection():
    conn = psycopg2.connect(
        host="db",  # Postgres 컨테이너의 이름을 사용
        database="postgres",
        user="postgres",
        password="password"
    )
    return conn
    
@app.route("/visit")
def visit():
    conn = get_db_connection()
    cur = conn.cursor()

    # 테이블이 존재하지 않으면 생성
    cur.execute('''
        CREATE TABLE IF NOT EXISTS visit_count (
            id SERIAL PRIMARY KEY,
            count INTEGER NOT NULL
        )
    ''')

    # count 값이 있는지 확인, 없으면 초기값을 삽입
    cur.execute('SELECT count FROM visit_count WHERE id = 1')
    row = cur.fetchone()

    if row is None:
        cur.execute('INSERT INTO visit_count (id, count) VALUES (1, 1)')
        count = 1
    else:
        count = row[0]
        cur.execute('UPDATE visit_count SET count = %s WHERE id = 1', (count + 1,))

    conn.commit()
    cur.close()
    conn.close()

    return f'{count}번째 방문입니다.'
