from flask import Flask, render_template
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

if __name__ == '__main__':
    app.run(debug=True)
