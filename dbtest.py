import psycopg2

# データベース接続情報
DB_HOST = "localhost"  # Docker Composeを使用している場合は"localhost"で接続可能
DB_PORT = "25432"  # Docker Composeで公開しているポート
DB_NAME = "mydatabase"  # 作成するデータベース名
DB_USER = "postgres"  # デフォルトのユーザー名
DB_PASSWORD = "postgres"  # デフォルトではパスワードなし。設定している場合は適宜変更

try:
    # データベース接続
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname="postgres", user=DB_USER, password=DB_PASSWORD)
    conn.autocommit = True  # データベース作成などの操作を即時反映
    cur = conn.cursor()

    # データベース作成
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"データベース {DB_NAME} を作成しました。")

    # 作成したデータベースに接続
    conn.close()  # 既存の接続を閉じる
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cur = conn.cursor()

    # テーブル作成
    cur.execute("""
        CREATE TABLE mytable (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            age INTEGER
        )
    """)
    print("テーブル mytable を作成しました。")

    # データ挿入 (Optional)
    cur.execute("INSERT INTO mytable (name, age) VALUES (%s, %s)", ("Alice", 30))
    cur.execute("INSERT INTO mytable (name, age) VALUES (%s, %s)", ("Bob", 25))
    print("データを追加しました。")


except psycopg2.Error as e:
    print(f"エラーが発生しました: {e}")

finally:
    if conn:
        cur.close()
        conn.close()
        print("データベース接続を閉じました。")


