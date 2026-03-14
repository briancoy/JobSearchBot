
import config
from jobspy import scrape_jobs
import sqlite3
import pandas as pd
import sys

def main():
    
    if config.location_mode == "remote":
        search_location = None
        is_remote = True
        search_distance = None
        google_location = "remote"
    else:
        search_location = config.locations[config.location_mode]
        is_remote = False
        search_distance = config.radius
        google_location = search_location
    active_sites = [key for key, value in config.sites_to_search.items() if value is True]

    jobs = scrape_jobs(
        # Build active search lists from config file
        site_name = active_sites,
        search_term = config.job_titles[0],
        google_search_term = f"{config.job_titles[0]} jobs near {google_location} since yesterday",
        location = search_location,
        results_wanted = config.postings_per_site,
        hours_old = config.posting_age,
        country_indeed = "USA",
        is_remote = is_remote,
        distance = search_distance
        )

    print(f"Found {len(jobs)} jobs")
    print(jobs.head())

    with sqlite3.connect("jobs.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
            id TEXT NOT NULL UNIQUE,
            site TEXT,
            job_url TEXT,
            job_url_direct	TEXT,
            title TEXT,
            company TEXT,
            location TEXT,
            date_posted DATE,
            job_type TEXT,
            salary_source TEXT,
            interval TEXT,
            min_amount INTEGER,
            max_amount INTEGER,
            currency TEXT,
            is_remote BOOLEAN,
            job_level TEXT,
            job_function TEXT,
            listing_type TEXT,
            emails TEXT,
            description TEXT,
            company_industry TEXT,
            company_url TEXT,
            company_logo TEXT,
            company_url_direct TEXT,
            company_addresses TEXT,
            company_num_employees INTEGER,
            company_revenue INTEGER,
            company_description	TEXT,
            skills TEXT,
            experience_range TEXT,
            company_rating FLOAT,
            company_reviews_count INTEGER,
            vacancy_count INTEGER,
            work_from_home_type TEXT
            )
        """)
        jobs.to_sql('jobs', conn, if_exists='append', index = False)
    

if __name__ == "__main__":
    main()

    
