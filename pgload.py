import psycopg2
import argparse
import random
import time
import threading
import os

def worker(conn_str, workload):
    """
    データベースにトランザクション負荷をかけるワーカースレッド。

    Args:
        conn_str: データベース接続文字列。
        workload: 負荷の度合い (1秒あたりのトランザクション数)。
    """
    conn = psycopg2.connect(conn_str)
    conn.autocommit = False  # トランザクションを手動でコミット
    cursor = conn.cursor()

    while True:
        start_time = time.time()
        try:
            for _ in range(workload):
                # テーブルロック
                cursor.execute("LOCK TABLE users IN EXCLUSIVE MODE")

                # ランダムなユーザー名を生成
                username = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(10))
                password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(20))

                # usersテーブルに挿入
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))

                # 挿入したユーザーを検索
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                inserted_id = cursor.fetchone()[0]

                # 挿入したユーザーを削除
                cursor.execute("DELETE FROM users WHERE id = %s", (inserted_id,))

            conn.commit() # ロック解除もコミットで行われる

        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()  # エラー発生時はロールバック

        elapsed_time = time.time() - start_time
        sleep_time = max(0, 1 - elapsed_time)
        time.sleep(sleep_time)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PostgreSQLデータベースにトランザクション負荷をかける")
    parser.add_argument("workload", type=int, help="負荷の度合い (1秒あたりのトランザクション数)")
    parser.add_argument("--threads", type=int, default=1, help="ワーカースレッドの数")
    args = parser.parse_args()

    # 環境変数からデータベースURLを取得
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable is not set.")
        exit(1)


    threads = []
    for _ in range(args.threads):
        thread = threading.Thread(target=worker, args=(database_url, args.workload))
        threads.append(thread)
        thread.start()

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("負荷テストを終了します...")

