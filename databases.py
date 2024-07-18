import sqlite3

def create_tables(db="job_tracker.db"):
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
                    id INTEGER PRIMARY KEY,
                    company TEXT NOT NULL,
                    title TEXT NOT NULL,
                    location TEXT NOT NULL,
                    url TEXT NOT NULL,
                    date TEXT NOT NULL
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
def register_user(username, email, password, db="job_tracker.db"):
    conn = sqlite3.connect(db)
    c = conn.cursor()  
    try:
        c.execute('''INSERT INTO users (username, email, password) VALUES (?, ?, ?)''',
                  (username, email, password))
        conn.commit()
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            print("Error: Username or email already exists.")
            return 1
        else:
            print(f"Error: {e}")
            return 2
    finally:
        conn.close()

# Returns if that username exists in database
def is_user(username, db="job_tracker.db"):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT id FROM users WHERE username = ?''', (username,))
    result = c.fetchone()
    conn.close()
    
    return result is not None

# Removes a user to users database, returns 1 if user doesn't exist, returns 2 if unknown failure
def remove_user(username, db="job_tracker.db"):
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        if not is_user(username, db=db):
            return 1
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error removing user: {e}")
        return 2
    finally:
        if conn:
            conn.close()

# Adds a new job to jobs table
def add_job(id, company, title, location, url, date, db="job_tracker.db"):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    # Insert a new job into the jobs table
    c.execute('''INSERT INTO jobs (id, company, title, location, url, date)
                 VALUES (?, ?, ?, ?, ?)''', (id, company, title, location, url, date))
    
    conn.commit()
    conn.close()

# Adds a new application to applications table
def add_application(user_id, job_id, application_date, status, date_last_updated, recruiter_name=None, recruiter_email=None, db="job_tracker.db"):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''INSERT INTO applications (user_id, job_id, application_date, status, date_last_updated, recruiter_name, recruiter_email) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, job_id, application_date, status, date_last_updated, recruiter_name, recruiter_email))
    conn.commit()
    conn.close()

# Updates "status" column in applications database, allows for "date" to be updated too
def update_application_status(application_id, status, date_last_updated, db="job_tracker.db"):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''UPDATE applications
                 SET status = ?, date_last_updated = ?
                 WHERE id = ?''',
              (status, date_last_updated, application_id))
    conn.commit()
    conn.close()

# Updates "recruiter info" column in applications database, allows for "date" to be updated too
def update_recruiter_info(application_id, date_last_updated, recruiter_name=None, recruiter_email=None, db="job_tracker.db"):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''UPDATE applications
                 SET date_last_updated = ?, recruiter_name = ?, recruiter_email = ?
                 WHERE id = ?''',
              (date_last_updated, recruiter_name, recruiter_email, application_id))
    conn.commit()
    conn.close()


# !!! DO NOT RUN THIS METHOD UNLESS YOU WANT TO DELETE ALL THE TABLES FROM THE DATABASE !!!
# !!! FOR TESTING AND DEBUGGING PURPOSES ONLY !!!

def reset_all(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''DELETE FROM users''')
    c.execute('''DELETE FROM jobs''')
    c.execute('''DELETE FROM applications''')
    c.execute('''DROP TABLE IF EXISTS users''')
    c.execute('''DROP TABLE IF EXISTS jobs''')
    c.execute('''DROP TABLE IF EXISTS applications''')
    conn.commit()
    conn.close()