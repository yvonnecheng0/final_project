from databases import reset_all
"""Run this file iff you want to delete the job_tracker database and all tables inside."""
if __name__ == '__main__':
    reset_all("job_tracker.db")