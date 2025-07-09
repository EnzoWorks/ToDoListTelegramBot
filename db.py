import sqlite3

DB_FILE = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT
    )''')
    conn.commit()
    conn.close()

def add_task(user_id, text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (user_id, text))
    conn.commit()
    conn.close()

def get_tasks(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, task FROM tasks WHERE user_id = ? order by id", (user_id,))
    tasks = [row[1] for row in c.fetchall()]
    conn.close()
    return tasks

def delete_task(user_id, index):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("select id from tasks WHERE user_id = ? order by id", (user_id,))
    task_ids = [row[0] for row in c.fetchall()]

    if 0 <= index < len(task_ids):
        c.execute("Delete from tasks where id = ?", (task_ids[index],))
        conn.commit()

    conn.close()

def edit_task(user_id, index, new_text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM tasks WHERE user_id = ? order by id", (user_id,))
    task_ids = [row[0] for row in c.fetchall()]
    if 0 <= index < len(task_ids):
        c.execute("UPDATE tasks SET task = ? WHERE id = ?", (new_text, task_ids[index]))
        conn.commit()
    conn.close()

def clear_tasks(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()