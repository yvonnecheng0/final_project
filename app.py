from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from listings import set_listings
from databases import register_user, verify_user, find_user_by_username, quick_add_app, is_application, \
    get_user_id_by_username, update_application_status, update_recruiter_info
import openai
import logging
from dotenv import load_dotenv
import os
import git

from problems_leet import get_problems_by_user, add_problem, delete_problem, update_problem

app = Flask(__name__)
load_dotenv()
# Set the OpenAI API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

app.secret_key = '072e2133647804bfed29c69aed595c28'
set_listings()


logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def my_home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('user_home.html')


@app.route('/leetcode/')
def leetcode():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = get_user_id_by_username(session['user'])
    problems = get_problems_by_user(user_id)

    return render_template('leetcode.html', problems=problems)


@app.route('/add-problem/', methods=['POST'])
def add_problem_route():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = get_user_id_by_username(session['user'])
    name = request.form['name']
    difficulty = request.form['difficulty']
    time_taken = request.form['time_taken']

    result = add_problem(user_id, name, difficulty, time_taken)
    if result == 0:
        flash("Problem successfully added.")
    else:
        flash(result)

    return redirect(url_for('leetcode'))


@app.route('/delete-problem/<int:problem_id>', methods=['POST'])
def delete_problem_route(problem_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    message = delete_problem(problem_id)
    flash(message)
    return redirect(url_for('leetcode'))


@app.route('/update-problem/<int:problem_id>', methods=['POST'])
def update_problem_route(problem_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    name = request.form.get('name')
    difficulty = request.form.get('difficulty')
    time_taken = request.form.get('time_taken')

    message = update_problem(problem_id, name, difficulty, time_taken)
    flash(message)
    return redirect(url_for('leetcode'))


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


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a bot helping the user practice behavioral interviews for technical roles."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message['content'].strip()
            return jsonify({'reply': reply})
        except Exception as e:
            logging.error(f"Error in chat endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500


@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/ychengproj2/final_project')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


if __name__ == '__main__':
    app.run(debug=True)
