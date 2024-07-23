import csv
import pandas as pd
from sqlalchemy import create_engine
import sqlite3
from JobSpy.src.jobspy import scrape_jobs


jobs = scrape_jobs(
    site_name=["indeed"], #"""", "linkedin", "zip_recruiter", "glassdoor""""
    search_term="Intern",
    #location="Dallas, TX",
    results_wanted=5000000,
    hours_old=744, # (only Linkedin/Indeed is hour specific, others round up to days old)
    country_indeed='USA',  # only needed for indeed / glassdoor
    
    # linkedin_fetch_description=True # get full description , direct job url , company industry and job level (seniority level) for linkedin (slower)
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
    
)
# 
unnecessary_columns = ['logo_photo_url', 'banner_photo_url', 'ceo_name', 'ceo_photo_url', 'company_num_employees', 'company_revenue', 'salary_source', 'company_url', 'company_url_direct', 'company_addresses','company_num_employees', 'company_revenue', 'company_description']
for col in jobs.columns:
    if col in unnecessary_columns:
        jobs = jobs.drop(columns=[col])
pd.set_option('display.max_rows', None)
#print(jobs.job_type)
#print(jobs.title)

#is_engineer = jobs['title'].str.contains('IT', case=False, na=False)
is_software = jobs['title'].str.contains('software', case=False, na=False)
is_data =  (jobs['title'].str.contains('data', case=False, na=False))
is_machine = (jobs['title'].str.contains('machine l', case=False, na=False))
is_product = (jobs['title'].str.contains('product', case=False, na=False))
product_jobs = jobs[is_product]
is_manager = product_jobs['title'].str.contains('manager', case=False, na=False)

filtered_rows = jobs[is_software| is_manager | is_data | is_machine]
print(filtered_rows['title'])
print(filtered_rows.shape)



def create_database():
    engine = create_engine('sqlite:///indeed_database.db')
    filtered_rows.to_sql("indeed_jobs", engine, if_exists = 'replace', index=False)
    print("DataFrame has been written to the SQL database.")
def check_outputs():
    conn = sqlite3.connect('indeed_database.db')

    # Query the schema of the table 'my_table'
    cursor = conn.execute("PRAGMA table_info(indeed_jobs)")
    columns = cursor.fetchall()

    # Print the column information
    for column in columns:
        print(column)

    conn.close()
create_database()
