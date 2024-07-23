from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from listings import set_listings
from databases import register_user, verify_user, find_user_by_username, quick_add_app, is_application, \
    get_user_id_by_username, update_application_status, update_recruiter_info

app = Flask(__name__)
app.secret_key = '072e2133647804bfed29c69aed595c28'

set_listings()

def init_sqlite_db():
    conn = sqlite3.connect('leetcode.db')
    print("Opened database successfully")

    conn.execute('CREATE TABLE IF NOT EXISTS problems (name TEXT, difficulty TEXT, time_taken INTEGER)')
    print("Table created successfully")
    conn.close()

init_sqlite_db()

@app.route('/')
def my_home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('user_home.html')


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


@app.route('/update_application', methods=['POST'])
def update_application():
    data = request.json
    application_id = data['application_id']
    column = data['column']
    value = data['value']

    try:
        if column == 'status':
            update_application_status(application_id, value)
        elif column in ['recruiter_name', 'recruiter_email']:
            update_recruiter_info(application_id, recruiter_name=value if column == 'recruiter_name' else None,
                                  recruiter_email=value if column == 'recruiter_email' else None)
        else:
            return jsonify({'success': False}), 400
    except Exception as e:
        print(e)  # Log error if needed
        return jsonify({'success': False}), 500

    return jsonify({'success': True})


@app.route('/logout')
def logout():
    # Clear the user from the session
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
