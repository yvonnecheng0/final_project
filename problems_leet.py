import sqlite3


def add_problem(user_id, name, difficulty, time_taken):
    """Inserts a new problem to leetcode table, returns 0 if success, raises exception otherwise"""
    try:
        with sqlite3.connect('job_tracker.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO leetcode (user_id, name, difficulty, time_taken) VALUES (?, ?, ?, ?)",
                        (user_id, name, difficulty, time_taken))
            con.commit()
            return 0
    except Exception as e:
        return f"Error: {e}"


def get_problems_by_user(user_id):
    """Returns all the leetcode problems entered by that user"""
    try:
        with sqlite3.connect('job_tracker.db') as con:
            cur = con.cursor()
            cur.execute("SELECT id, name, difficulty, time_taken FROM leetcode WHERE user_id = ?", (user_id,))
            problems = cur.fetchall()
            return problems
    except Exception as e:
        return f"Error: {e}"


def delete_problem(problem_id):
    """Deletes a problem given its ID"""
    try:
        with sqlite3.connect('job_tracker.db') as con:
            cur = con.cursor()
            cur.execute("DELETE FROM leetcode WHERE id = ?", (problem_id,))
            con.commit()
            return "Problem deleted successfully."
    except Exception as e:
        return f"Error: {e}"


def update_problem(problem_id, name=None, difficulty=None, time_taken=None):
    """Allows user to update the name, difficulty, or time_taken for the problem"""
    try:
        with sqlite3.connect('job_tracker.db') as con:
            cur = con.cursor()
            if name:
                cur.execute("UPDATE leetcode SET name = ? WHERE id = ?", (name, problem_id))
            if difficulty:
                cur.execute("UPDATE leetcode SET difficulty = ? WHERE id = ?", (difficulty, problem_id))
            if time_taken:
                cur.execute("UPDATE leetcode SET time_taken = ? WHERE id = ?", (time_taken, problem_id))
            con.commit()
            return "Problem updated successfully."
    except Exception as e:
        return f"Error: {e}"
