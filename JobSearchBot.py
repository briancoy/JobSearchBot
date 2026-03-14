# main.py

import config
import searchBot
import sqlite3

DB = "jobs.db"

def init_db():
    """Creates all tables on first run. Safe to call every startup."""
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        # Key/value settings store — flexible, no schema changes needed to add settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key     TEXT NOT NULL UNIQUE,
                value   TEXT
            )
        """)

        # Separate table for job title search terms (one per row — easy to add/remove)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_titles (
                title   TEXT NOT NULL UNIQUE
            )
        """)

        # Separate table for email recipients (one per row)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_recipients (
                address TEXT NOT NULL UNIQUE
            )
        """)

        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id                      TEXT NOT NULL UNIQUE,
                site                    TEXT,
                job_url                 TEXT,
                job_url_direct          TEXT,
                title                   TEXT,
                company                 TEXT,
                location                TEXT,
                date_posted             DATE,
                job_type                TEXT,
                salary_source           TEXT,
                interval                TEXT,
                min_amount              INTEGER,
                max_amount              INTEGER,
                currency                TEXT,
                is_remote               BOOLEAN,
                job_level               TEXT,
                job_function            TEXT,
                listing_type            TEXT,
                emails                  TEXT,
                description             TEXT,
                company_industry        TEXT,
                company_url             TEXT,
                company_logo            TEXT,
                company_url_direct      TEXT,
                company_addresses       TEXT,
                company_num_employees   INTEGER,
                company_revenue         INTEGER,
                company_description     TEXT,
                skills                  TEXT,
                experience_range        TEXT,
                company_rating          FLOAT,
                company_reviews_count   INTEGER,
                vacancy_count           INTEGER,
                work_from_home_type     TEXT
            )
        """)

        # Seed default settings from config.py if settings table is empty
        cursor.execute("SELECT COUNT(*) FROM settings")
        if cursor.fetchone()[0] == 0:
            defaults = [
                ("location_mode",     config.location_mode),
                ("city",              config.locations["city"]),
                ("zip",               config.locations["zip"]),
                ("radius",            str(config.radius)),
                ("posting_age",       str(config.posting_age)),
                ("postings_per_site", str(config.postings_per_site)),
                ("linkedin",          str(config.sites_to_search["linkedin"])),
                ("indeed",            str(config.sites_to_search["indeed"])),
                ("glassdoor",         str(config.sites_to_search["glassdoor"])),
                ("zip_recruiter",     str(config.sites_to_search["zip_recruiter"])),
                ("google",            str(config.sites_to_search["google"])),
                ("email_enabled",     str(config.email_enabled)),
                ("email_sender",      config.email_sender),
                ("email_password",    config.email_password),
            ]
            cursor.executemany(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", defaults
            )

        # Seed job titles from config if table is empty
        cursor.execute("SELECT COUNT(*) FROM job_titles")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT OR IGNORE INTO job_titles (title) VALUES (?)",
                [(t,) for t in config.job_titles]
            )

        # Seed email recipients from config if table is empty
        cursor.execute("SELECT COUNT(*) FROM email_recipients")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT OR IGNORE INTO email_recipients (address) VALUES (?)",
                [(r,) for r in config.email_recipients]
            )

        conn.commit()
    print("Database initialized.")


def main():
    init_db()   # ← Always run at startup

    print("\nWelcome to JobSearchBot")
    print("  search  - Start a new search")
    print("  options - Change settings")
    print("  list    - Show saved job postings")
    print("  exit    - Quit\n")

    user_input = ""
    while user_input != "exit":
        user_input = input("Enter an option or 'exit' to quit: ").lower()

        if user_input == "search":
            searchBot.main()

        elif user_input == "options":
            print("Settings editor coming soon.")

        elif user_input == "list":
            with sqlite3.connect(DB) as conn:
                cursor = conn.cursor()
                saved_jobs = cursor.execute("""
                    SELECT id, site, job_url, title, company FROM jobs
                """).fetchall()
            if not saved_jobs:
                print("No saved jobs found.")
            else:
                for job in saved_jobs:
                    print(job)

        elif user_input != "exit":
            print("Unrecognized option. Try 'search', 'options', 'list', or 'exit'.")

    print("Goodbye!")


if __name__ == "__main__":
    main()
