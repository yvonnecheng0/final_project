from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from listings import set_listings
from databases import register_user, verify_user, find_user_by_username, quick_add_app, is_application, \
    get_user_id_by_username

app = Flask(__name__)
app.secret_key = '072e2133647804bfed29c69aed595c28'

set_listings()


@app.route('/')
def my_home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('user_home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login_user = request.form['login']
        email = request.form['email']
        password = request.form['password']
        result = register_user(login_user, email, password)
        if result == 1:
            flash('User already exists')
        elif result == 2:
            flash('Unknown error occurred')
        else:
            session['user'] = login_user
            return redirect(url_for('my_home'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_user = request.form['login']
        password = request.form['password']
        if verify_user(login_user, password):
            session['user'] = login_user
            return redirect(url_for('my_home'))
        flash('Incorrect login or password')
    return render_template('login.html')


@app.route('/display-jobs')
def display_jobs():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('job_tracker.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM jobs')
    jobs = cur.fetchall()
    conn.close()
    return render_template('display_jobs.html', jobs=jobs)


@app.route('/show-applications')
def show_applications():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    user = find_user_by_username(username)
    if not user:
        return redirect(url_for('login'))
    user_id = user[0]
    conn = sqlite3.connect('job_tracker.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM applications_jobs_view WHERE application_id IN 
                       (SELECT id FROM applications WHERE user_id = ?)''', (user_id,))
    applications = cur.fetchall()
    conn.close()
    return render_template('view_applications.html', applications=applications)


@app.route('/add-application/<int:job_id>', methods=['POST'])
def add_application(job_id):
    if 'user' not in session:
        flash('You must be logged in to apply for a job.')
        return redirect(url_for('login'))

    username = session['user']
    user_id = get_user_id_by_username(username)

    if is_application(user_id, job_id):
        flash('You have already applied for this job.')
        return redirect(url_for('display_jobs'))

    quick_add_app(user_id, job_id)
    flash('Application submitted successfully!')
    return redirect(url_for('display_jobs'))


@app.route('/logout')
def logout():
    # Clear the user from the session
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
