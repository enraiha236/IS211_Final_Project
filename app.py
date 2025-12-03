from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'W6OaEXQz0J'
app.api_key = "AIzaSyAnitWzWKUY-gMwje4VjBy5BTJUgO05KYE"

db_file = "students.db"

def get_db():
    return sqlite3.connect(db_file)

# create tables if not exists
with get_db() as con:
    con.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY, 
                    username TEXT UNIQUE, 
                    password TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY, 
                    user_id INTEGER, 
                    title TEXT, 
                    author TEXT, 
                    pages TEXT, 
                    rating TEXT, 
                    thumb TEXT, 
                    FOREIGN KEY(user_id) REFERENCES users(id))""")
    cur = con.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    if count == 0:
        con.execute("INSERT INTO users (username, password) VALUES ('admin', 'password')")
    con.commit()

@app.route('/', methods=['GET'])
def index():
    if not session.get("user"):
        return redirect(url_for("login"))

    user_id = session["user"]["id"]
    con = get_db()
    con.row_factory = sqlite3.Row
    cur = con.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    session["user"]["username"] = cur.fetchone()["username"]

    cur = con.execute("SELECT * FROM books WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    con.close()
    user_books = [dict(r) for r in rows]
    return render_template('index.html', books=user_books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        con = get_db()
        con.row_factory = sqlite3.Row
        cur = con.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        row = cur.fetchone()
        con.close()
        if row:
            session["user"] = {"id": row["id"], "username": row["username"]}
            flash("Login success", "success")
            return redirect(url_for("index"))
        flash("Login failed", "error")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        con = get_db()
        try:
            con.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            con.commit()
            flash("Account created", "success")
            return redirect(url_for("login"))
        except:
            flash("Username already exists", "error")
            return redirect(url_for("register"))
        finally:
            con.close()
    return render_template("register.html")

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("Logged out", "success")
    return redirect(url_for("login"))

@app.route('/search_isbn', methods=['POST'])
def search_isbn():
    if not session.get("user"):
        return redirect(url_for("login"))
    isbn = request.form['isbn']
    url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={app.api_key}'
    response = requests.get(url)
    data = response.json()
    if 'items' not in data:
        flash("Book not found", "error")
        return redirect(url_for("index"))
    results = []
    for item in data['items']:
        info = item.get('volumeInfo', {})
        results.append({
            'title': info.get('title', 'N/A'),
            'author': ', '.join(info.get('authors', ['Unknown'])),
            'pages': str(info.get('pageCount', '')),
            'rating': str(info.get('averageRating', '')),
            'thumb': info.get('imageLinks', {}).get('thumbnail', '')
        })
    return render_template("index.html", isbn_results=results, search_mode="isbn", books=[])

@app.route('/search_title', methods=['POST'])
def search_title():
    if not session.get("user"):
        return redirect(url_for("login"))
    title = request.form['title']
    url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:{title}&key={app.api_key}'
    response = requests.get(url)
    data = response.json()
    if 'items' not in data:
        flash("No books found", "error")
        return redirect(url_for("index"))
    results = []
    for item in data['items']:
        info = item.get('volumeInfo', {})
        results.append({
            'title': info.get('title', 'N/A'),
            'author': ', '.join(info.get('authors', ['Unknown'])),
            'pages': str(info.get('pageCount', '')),
            'rating': str(info.get('averageRating', '')),
            'thumb': info.get('imageLinks', {}).get('thumbnail', '')
        })
    return render_template("index.html", title_results=results, search_mode="title", books=[])

@app.route('/add_book', methods=['POST'])
def add_book():
    if not session.get("user"):
        return redirect(url_for("login"))
    book = {
        'title': request.form['title'],
        'author': request.form['author'],
        'pages': request.form['pages'],
        'rating': request.form['rating'],
        'thumb': request.form['thumb']
    }
    user_id = session["user"]["id"]
    with get_db() as con:
        con.execute("INSERT INTO books (user_id, title, author, pages, rating, thumb) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, book["title"], book["author"], book["pages"], book["rating"], book["thumb"]))
        con.commit()
    flash("Book saved", "success")
    return redirect(url_for("index"))

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if not session.get("user"):
        return redirect(url_for("login"))
    user_id = session["user"]["id"]
    with get_db() as con:
        cur = con.execute("SELECT id FROM books WHERE user_id = ?", (user_id,))
        ids = [r[0] for r in cur.fetchall()]
        if index < 0 or index >= len(ids):
            flash("Invalid book index", "error")
            return redirect(url_for("index"))
        book_id = ids[index]
        con.execute("DELETE FROM books WHERE id = ?", (book_id,))
        con.commit()
    flash("Book removed", "success")
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)