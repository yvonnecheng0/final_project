import sqlite3
import os

DEFAULT_DB = "job_tracker.db"

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
                    id TEXT PRIMARY KEY NOT NULL,
                    date TEXT NOT NULL,
                    company TEXT NOT NULL,
                    title TEXT NOT NULL,
                    locations TEXT NOT NULL,
                    url TEXT NOT NULL
                )''')

    # Creates applications table
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    job_id INTEGER NOT NULL,
                    application_date TEXT NOT NULL,
                    status TEXT DEFAULT 'Ready to Apply' NOT NULL,
                    date_last_updated TEXT NOT NULL,
                    recruiter_name TEXT,
                    recruiter_email TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                )''')
    
    # Creates a view of jobs user has applied to + job info
    c.execute('''CREATE VIEW IF NOT EXISTS user_applications AS
                 SELECT 
                     applications.id AS application_id,
                     applications.user_id,
                     applications.application_date,
                     applications.status,
                     applications.date_last_updated,
                     applications.recruiter_name,
                     applications.recruiter_email,
                     jobs.id AS job_id,
                     jobs.company_name,
                     jobs.title,
                     jobs.location,
                     jobs.url,
                     jobs.date_posted
                 FROM applications
                 JOIN jobs ON applications.job_id = jobs.id;''')
    conn.commit()
    conn.close()

# Adds a new user to users database, if user already exists return 1 as error code, return 2 if unknown failure
def register_user(username, email, password, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()  
    try:
        c.execute('''INSERT INTO users (username, email, password) VALUES (?, ?, ?)''',
                  (username, email, password))
        conn.commit()
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            print("Error: Username or email already exists.")
            conn.close()
            return 1
        else:
            print(f"Error: {e}")
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

# Removes a user to users database, returns 1 if user doesn't exist, returns 2 if unknown failure
def remove_user(username, db=DEFAULT_DB):
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        if not is_user(username, db=db):
            conn.close()
            return 1
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error removing user: {e}")
        conn.close()
        return 2
    finally:
        if conn:
            conn.close()

def isJob(job_id, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Adds a new job to jobs table
def add_job(id, date, company, title, locations, url, db=DEFAULT_DB):
    if isJob(id, db):
        print(f"Job with ID {id} already exists. Not inserting.")
        return
    conn = sqlite3.connect(db)
    c = conn.cursor()
    locations_str = ','.join(locations)
    c.execute('''INSERT INTO jobs (id, date, company, title, locations, url)
                 VALUES (?, ?, ?, ?, ?, ?)''', (id, date, company, title, locations_str, url))
    conn.commit()
    conn.close()

# Adds a new job from the dictionary returned from listings.format_listings 
def quick_add_job(dic, db):
    add_job(dic["id"], dic["date"], dic["company"], dic["title"], dic["locations"], dic["url"], db=db)

# Adds a new application to applications table, returns 1 if user not found, 2 if job not found
def add_application(user_id, job_id, application_date, status, date_last_updated, recruiter_name=None, recruiter_email=None, db=DEFAULT_DB):
    if not is_user(user_id, db=db):
        print("User not found.")
        return 1
    elif not isJob(job_id, db=db):
        print("Job not found.")
        return 2
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''INSERT INTO applications (user_id, job_id, application_date, status, date_last_updated, recruiter_name, recruiter_email) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, job_id, application_date, status, date_last_updated, recruiter_name, recruiter_email))
    conn.commit()
    conn.close()

def isApplication(user_id, job_id, db=DEFAULT_DB):
    if not is_user(user_id, db=db):
        print("User not found.")
        return 1
    elif not isJob(job_id, db=db):
        print("Job not found.")
        return 2
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT 1 FROM applications WHERE user_id = ? AND job_id = ?', (user_id, job_id))
    result = c.fetchone()
    conn.close()
    return result is not None

# Updates "status" column in applications database, allows for "date" to be updated too
def update_application_status(application_id, status, date_last_updated, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''UPDATE applications
                 SET status = ?, date_last_updated = ?
                 WHERE id = ?''',
              (status, date_last_updated, application_id))
    conn.commit()
    conn.close()

# Updates "recruiter info" column in applications database, allows for "date" to be updated too
def update_recruiter_info(application_id, date_last_updated, recruiter_name=None, recruiter_email=None, db=DEFAULT_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''UPDATE applications
                 SET date_last_updated = ?, recruiter_name = ?, recruiter_email = ?
                 WHERE id = ?''',
              (date_last_updated, recruiter_name, recruiter_email, application_id))
    conn.commit()
    conn.close()


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