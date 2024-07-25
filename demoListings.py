from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from listings import setListings

app = Flask(__name__)

@app.route('/display-jobs')
def display_jobs():
    setListings()
    conn = sqlite3.connect('job_tracker.db')
    cur = conn.cursor()

    # Fetch data from jobs table
    cur.execute('SELECT * FROM jobs')
    jobs = cur.fetchall()

    conn.close()

    # Print fetched data for debugging
    print("Jobs:", jobs)

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
