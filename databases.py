import sqlite3
import os
from datetime import date
from argon2 import PasswordHasher

DEFAULT_DB = "job_tracker.db"
ph = PasswordHasher()


def create_tables(db=DEFAULT_DB):
    """Creates the 3 tables used for job listings: users, jobs, and applications"""
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    posted TEXT NOT NULL,
                    updated TEXT NOT NULL,
                    company TEXT NOT NULL,
                    title TEXT NOT NULL,
                    season TEXT NOT NULL,
                    sponsorship TEXT NOT NULL,
                    active BOOLEAN NOT NULL,
                    locations TEXT NOT NULL,
                    url TEXT NOT NULL
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    job_id INTEGER NOT NULL,
                    application_date TEXT,
                    status TEXT DEFAULT 'Ready to Apply' NOT NULL,
                    date_last_updated TEXT NOT NULL,
                    recruiter_name TEXT,
                    recruiter_email TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                )''')

    c.execute('''CREATE VIEW IF NOT EXISTS applications_jobs_view AS
                     SELECT applications.id AS application_id,
                            applications.job_id,
                            applications.application_date,
                            applications.status,
                            applications.date_last_updated,
                            applications.recruiter_name,
                            applications.recruiter_email,
                            jobs.posted AS job_posted,
                            jobs.updated AS job_updated,
                            jobs.company AS job_company,
                            jobs.title AS job_title,
                            jobs.season AS job_season,
                            jobs.sponsorship AS job_sponsorship,
                            jobs.active AS job_active,
                            jobs.locations AS job_locations,
                            jobs.url AS job_url
                     FROM applications
                     JOIN jobs ON applications.job_id = jobs.id
                  ''')


def register_user(username, email, password, db=DEFAULT_DB):
    """Adds a new user to users table, if user already exists return 1 as error code, return 2 if unknown failure"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    try:
        hashed_password = ph.hash(password)
        c.execute('''INSERT INTO users (username, email, password) VALUES (?, ?, ?)''',
                  (username, email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            conn.close()
            return 1
        else:
            conn.close()
            return 2
    finally:
        conn.close()


def is_user(id_or_username, db=DEFAULT_DB):
    """Checks if username or id exists in users table, returns boolean"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    if isinstance(id_or_username, int):
        c.execute('''SELECT id FROM users WHERE id = ?''', (id_or_username,))
    else:
        c.execute('''SELECT id FROM users WHERE username = ?''', (id_or_username,))
    result = c.fetchone()
    conn.close()

    return result is not None


def find_user_by_username(username, db=DEFAULT_DB):
    """Grabs user by their username in users table, returns the entire row"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user


def verify_user(username, password, db=DEFAULT_DB):
    """Verifies that the username + password combo exists in users table, return boolean"""
    user = find_user_by_username(username, db)
    if user:
        hashed_password = user[3]  # assuming password is the 4th column
        try:
            ph.verify(hashed_password, password)
            return True
        except:
            return False
    return False


def remove_user(username, db=DEFAULT_DB):
    """Removes a user from users table, returns 1 if user doesn't exist, returns 2 if unknown failure"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    try:
        if not is_user(username, db=db):
            conn.close()
            return 1
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
    except sqlite3.Error:
        conn.close()
        return 2
    finally:
        if conn:
            conn.close()


def get_user_id_by_username(username, db=DEFAULT_DB):
    """Gets the id of a user from their username, returns None if not found"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = c.fetchone()
    conn.close()
    if user_id:
        return user_id[0]
    return None


def is_job(company, role, season, db=DEFAULT_DB):
    """Checks if the company + role + season combo exists in jobs table, return boolean"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT id FROM jobs WHERE company = ? AND title = ? AND season = ?", (company, role, season))
    result_dupe = c.fetchone()
    conn.close()
    return result_dupe is not None


def is_job_id(job_id, db=DEFAULT_DB):
    """Checks if job_id is a valid id in the jobs table, returns boolean"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))
    result_id = c.fetchone()
    return result_id is not None


def add_job(posted_date, updated, company, title, season, sponsorship, active, locations, url, db=DEFAULT_DB):
    """Adds a new job to the jobs table, returns 1 if the job already exists"""
    if is_job(company, title, season, db):
        return 1
    conn = sqlite3.connect(db)
    c = conn.cursor()
    locations_str = ','.join(locations)
    c.execute('''
        INSERT INTO jobs (posted, updated, company, title, season, sponsorship, active, locations, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (posted_date, updated, company, title, season, sponsorship, active, locations_str, url))
    conn.commit()
    conn.close()


def quick_add_job(dic, db=DEFAULT_DB):
    """Adds a new job from the dictionary returned from listings.format_listings, returns 1 if already in jobs"""
    add_job(dic["posted"], dic["updated"], dic["company"], dic["title"],
            dic["season"], dic["sponsorship"], dic["active"], dic["locations"], dic["url"], db=db)


def add_application(user_id, job_id, application_date, status, date_last_updated, recruiter_name=None,
                    recruiter_email=None, db=DEFAULT_DB):
    """Adds a new application to the applications table, returns 1 if user not found, 2 if job not found"""
    if not is_user(user_id, db=db):
        return 1
    elif not is_job_id(job_id, db=db):
        return 2
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''INSERT INTO applications (user_id, job_id, application_date, status, date_last_updated, 
    recruiter_name, recruiter_email) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, job_id, application_date, status, date_last_updated, recruiter_name, recruiter_email))
    conn.commit()
    conn.close()


def quick_add_app(user_id, job_id, db=DEFAULT_DB):
    """Adds an application to applications table. Default dates set to today, status set to Ready to Apply"""
    app_date = date.today().strftime('%Y-%m-%d')
    add_application(user_id, job_id, app_date, "Ready to Apply", app_date, None, None, db=db)


def is_application(user_id, job_id, db=DEFAULT_DB):
    """Returns if an application for that user_id/username and job exists, returns 1 if no user found, 2 if job not
    found"""
    if not is_user(user_id, db=db):
        return 1
    elif not is_job_id(job_id, db=db):
        return 2
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT 1 FROM applications WHERE user_id = ? AND job_id = ?', (user_id, job_id))
    result = c.fetchone()
    conn.close()
    return result is not None


def update_application_status(application_id, status, db=DEFAULT_DB):
    """Updates 'status' column in applications table, updates dates to today"""
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''UPDATE applications
                 SET status = ?
                 WHERE id = ?''',
              (status, application_id))
    conn.commit()
    conn.close()
    update_date(application_id, db=db)


def update_date(application_id, db=DEFAULT_DB):
    """Updates 'date last updated' to today for a given application"""
    today = date.today().strftime('%Y-%m-%d')
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''UPDATE applications
                 SET date_last_updated = ?
                 WHERE id = ?''',
              (today, application_id))
    conn.commit()
    conn.close()


def update_recruiter_info(application_id, recruiter_name=None, recruiter_email=None, db=DEFAULT_DB):
    """Updates 'recruiter __' columns in applications database, updates date to today"""
    today = date.today().strftime('%Y-%m-%d')
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''UPDATE applications
                 SET date_last_updated = ?, recruiter_name = ?, recruiter_email = ?
                 WHERE id = ?''',
              (today, recruiter_name, recruiter_email, application_id))
    conn.commit()
    conn.close()
    update_date(application_id, db=db)


# GETTER METHODS
def get_status(application_id, db=DEFAULT_DB):
    """Gets the 'status' attribute of an application from the applications table, returns None if not found"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT status FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_user_id(application_id, db=DEFAULT_DB):
    """Gets the corresponding user id from the applications table, returns None if not found"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT user_id FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_job_id(application_id, db=DEFAULT_DB):
    """Gets the corresponding job id from the applications table, returns None if not found"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT job_id FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_recruiter_name(application_id, db=DEFAULT_DB):
    """Gets the recruiter name from the applications table, returns None if not found"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT recruiter_name FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_recruiter_email(application_id, db=DEFAULT_DB):
    """Gets the recruiter email from applications table, returns None if not found"""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT recruiter_email FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def print_table(table, db):
    """Prints a table to the terminal"""
    print("\n")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table}")
    rows = c.fetchall()
    column_names = [description[0] for description in c.description]
    print(f"{' | '.join(column_names)}")
    for row in rows:
        print(f"{' | '.join(map(str, row))}")

    conn.close()
    print("\n")


def reset_all(db):
    """Resets everything by deleting the entire database including all tables inside. Use with caution."""
    if not os.path.exists(db):
        print("Can't delete a database that doesn't exist!")
        return 1
    try:
        with sqlite3.connect(db) as conn:
            c = conn.cursor()
            c.execute('''DELETE FROM users''')
            c.execute('''DELETE FROM jobs''')
            c.execute('''DELETE FROM applications''')
            c.execute('''DROP TABLE IF EXISTS users''')
            c.execute('''DROP TABLE IF EXISTS jobs''')
            c.execute('''DROP TABLE IF EXISTS applications''')
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        return 1
    finally:
        if os.path.exists(db):
            os.remove(db)
            print(f"Database {db} removed.")
    return 0
