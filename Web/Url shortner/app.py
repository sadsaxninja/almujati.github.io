from flask import Flask, request, jsonify, redirect, render_template
import string
import random
import sqlite3

app = Flask(__name__)

# Database setup
DATABASE = 'urls.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 long_url TEXT NOT NULL,
                 short_key TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

# Generate a unique short key
def generate_short_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    long_url = data.get('long_url')

    if not long_url:
        return jsonify({'error': 'No URL provided'}), 400

    short_key = generate_short_key()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    try:
        c.execute('INSERT INTO urls (long_url, short_key) VALUES (?, ?)', (long_url, short_key))
        conn.commit()
    except sqlite3.IntegrityError:
        # If the short_key already exists, regenerate it
        short_key = generate_short_key()
        c.execute('INSERT INTO urls (long_url, short_key) VALUES (?, ?)', (long_url, short_key))
        conn.commit()

    conn.close()

    short_url = f"{request.host_url}{short_key}"
    return jsonify({'short_url': short_url})

@app.route('/<short_key>')
def redirect_to_long_url(short_key):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT long_url FROM urls WHERE short_key = ?', (short_key,))
    result = c.fetchone()
    conn.close()

    if result:
        long_url = result[0]
        return redirect(long_url)
    else:
        return "URL not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)