import sqlite3

def view_posts():
    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reddit_post;")
        rows = cursor.fetchall()
        cursor.execute("SELECt COUNT(*) FROM reddit_post")
        count = cursor.fetchall()
        print(f"Total posts in the database: {count[0][0]}")

        if len(rows) == 0:
            print("No posts found in the database.")
        else:
            print("ID\tTitle\tSelftext\tSubreddit\tCreated")
            print("-" * 70)
            for row in rows:
                print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    view_posts()