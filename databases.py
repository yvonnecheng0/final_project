import sqlite3
import os
from datetime import date
from argon2 import PasswordHasher

DEFAULT_DB = "job_tracker.db"
ph = PasswordHasher()


def create_tables(db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Creates users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

    # Creates jobs table
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

    # Creates applications table
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


# Adds a new user to users database, if user already exists return 1 as error code, return 2 if unknown failure
def register_user(username, email, password, db=DEFAULT_DB):
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


# Returns if that username or user id exists in database
def is_user(id_or_username, db=DEFAULT_DB):
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
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user


def verify_user(username, password, db=DEFAULT_DB):
    user = find_user_by_username(username, db)
    if user:
        hashed_password = user[3]  # assuming password is the 4th column
        try:
            ph.verify(hashed_password, password)
            return True
        except:
            return False
    return False


# Removes a user to users database, returns 1 if user doesn't exist, returns 2 if unknown failure
def remove_user(username, db=DEFAULT_DB):
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


def is_job(company, role, season, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT id FROM jobs WHERE company = ? AND title = ? AND season = ?", (company, role, season))
    result_dupe = c.fetchone()
    conn.close()
    return result_dupe is not None


def is_job_id(job_id, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))
    result_id = c.fetchone()
    return result_id is not None


# Adds a new job to jobs table
def add_job(posted_date, updated, company, title, season, sponsorship, active, locations, url, db=DEFAULT_DB):
    if is_job(company, title, season, db):
        print(f"The {season} {title} at {company} already exists. Not inserting.")
        return
    conn = sqlite3.connect(db)
    c = conn.cursor()
    locations_str = ','.join(locations)
    c.execute('''
        INSERT INTO jobs (posted, updated, company, title, season, sponsorship, active, locations, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (posted_date, updated, company, title, season, sponsorship, active, locations_str, url))
    conn.commit()
    conn.close()


# Adds a new job from the dictionary returned from listings.format_listings
def quick_add_job(dic, db=DEFAULT_DB):
    add_job(dic["posted"], dic["updated"], dic["company"], dic["title"],
            dic["season"], dic["sponsorship"], dic["active"], dic["locations"], dic["url"], db=db)


# Adds a new application to applications table, returns 1 if user not found, 2 if job not found
def add_application(user_id, job_id, application_date, status, date_last_updated, recruiter_name=None,
                    recruiter_email=None, db=DEFAULT_DB):
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


# Adds an application from user_id and job_id. Default application/update date set to today,
# status set to Ready to Apply
def quick_add_app(user_id, job_id, db=DEFAULT_DB):
    app_date = date.today().strftime('%Y-%m-%d')
    add_application(user_id, job_id, app_date, "Ready to Apply", app_date, None, None, db=db)


# Returns if an application for that user_id (can also be username) and job exists, returns 1 if no user found,
# 2 if job not found
def is_application(user_id, job_id, db=DEFAULT_DB):
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


# Updates "status" column in applications database, updates date to today
def update_application_status(application_id, status, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''UPDATE applications
                 SET status = ?
                 WHERE id = ?''',
              (status, application_id))
    conn.commit()
    conn.close()
    update_date(application_id, db=db)


# Updates "date last updated" to today for a given application
def update_date(application_id, db=DEFAULT_DB):
    today = date.today().strftime('%Y-%m-%d')
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''UPDATE applications
                 SET date_last_updated = ?
                 WHERE id = ?''',
              (today, application_id))
    conn.commit()
    conn.close()


# Updates "recruiter info" column in applications database, updates date to today
def update_recruiter_info(application_id, recruiter_name=None, recruiter_email=None, db=DEFAULT_DB):
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
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT status FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_user_id(application_id, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT user_id FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_job_id(application_id, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT job_id FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_recruiter_name(application_id, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT recruiter_name FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_recruiter_email(application_id, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT recruiter_email FROM applications WHERE id = ?''', (application_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def print_table(table, db):
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


# !!! DO NOT RUN THIS METHOD UNLESS YOU WANT TO DELETE ALL THE TABLES FROM THE DATABASE !!!
# !!! FOR TESTING AND DEBUGGING PURPOSES ONLY !!!

def reset_all(db):
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
