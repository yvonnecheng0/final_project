from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_sqlite_db():
    conn = sqlite3.connect('leetcode.db')
    print("Opened database successfully")

    conn.execute('CREATE TABLE IF NOT EXISTS problems (name TEXT, difficulty TEXT, time_taken INTEGER)')
    print("Table created successfully")
    conn.close()

init_sqlite_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add-problem/', methods=['POST'])
def add_problem():
    if request.method == 'POST':
        try:
            name = request.form['name']
            difficulty = request.form['difficulty']
            time_taken = request.form['time_taken']

            with sqlite3.connect('leetcode.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO problems (name, difficulty, time_taken) VALUES (?, ?, ?)", (name, difficulty, time_taken))
                con.commit()
                msg = "Record successfully added."
        except:
            con.rollback()
            msg = "Error occurred in insert operation"
        finally:
            con.close()
            return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
