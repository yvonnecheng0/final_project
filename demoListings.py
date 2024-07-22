from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from listings import setListings
from databases import register_user, verify_user

app = Flask(__name__)

setListings()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        result = register_user(login, email, password)
        if result == 1:
            return 'User already exists'
        elif result == 2:
            return 'Unknown error occurred'
        return f'User {login} was created'
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_user = request.form['login']
        password = request.form['password']
        if verify_user(login_user, password):
            return f'User {login_user} is logged in'
        return 'Incorrect login or password'
    return render_template('login.html')


@app.route('/display-jobs')
def display_jobs():
    conn = sqlite3.connect('job_tracker.db')
    cur = conn.cursor()

    # Fetch data from jobs table
    cur.execute('SELECT * FROM jobs')
    jobs = cur.fetchall()

    conn.close()

    return render_template('display_jobs.html', jobs=jobs)


if __name__ == '__main__':
    app.run(debug=True)
