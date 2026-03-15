# main.py
import config
import sqlite3
from jobspy import scrape_jobs
import pandas as pd


DB = "jobs.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key     TEXT NOT NULL UNIQUE,
                value   TEXT
            )
        """)

        # Job search table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_titles (
                title   TEXT NOT NULL UNIQUE
            )
        """)

        # Email recipient table
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS black_list (
                id                      TEXT NOT NULL UNIQUE,
                site                    TEXT,
                title                   TEXT,
                company                 TEXT,
                location                TEXT
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
                ("list_limit",        "25"),
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
    init_db()   # ensure the jobs DB exists, crete it if it doesn't

    print("\nWelcome to JobSearchBot")
    print("  search  - Start a new search")
    print("  options - Change settings")
    print("  list    - Show saved job postings")
    print("  exit    - Quit\n")

    user_input = ""
    while user_input != "exit":
        user_input = input("Enter an option or 'exit' to quit: ").lower()

        if user_input == "search":
            job_search()

        elif user_input == "options":
            options_menu()

        elif user_input == "list":
            limit = int(get_setting("list_limit") or 25)       # ← read from DB
            with sqlite3.connect(DB) as conn:
                cursor = conn.cursor()
                saved_jobs = cursor.execute("""
                    SELECT id, site, title, company, location
                    FROM jobs
                    ORDER BY date_posted DESC
                    LIMIT ?                                     -- ← apply the limit
                """, (limit,)).fetchall()
            if not saved_jobs:
                print("No saved jobs found.")
            else:
                print(f"\n{'ID':<40} {'Site':<12} {'Title':<35} {'Company':<30} {'Location'}")
                print("-" * 130)
                for job in saved_jobs:
                    print(f"{str(job[0]):<40} {str(job[1]):<12} {str(job[2]):<35} {str(job[3]):<30} {str(job[4])}")
                print(f"\nShowing {len(saved_jobs)} of most recent postings (limit: {limit})\n")

        elif user_input != "exit":
            print("Unrecognized option. Try 'search', 'options', 'list', or 'exit'.")

    print("Goodbye!")

def save_jobs_to_db(jobs, conn):
    cursor = conn.cursor()

    cols = ", ".join(jobs.columns)
    placeholders = ", ".join(["?" for _ in jobs.columns])
    sql = f"INSERT OR IGNORE INTO jobs ({cols}) VALUES ({placeholders})"

    rows = [tuple(row) for row in jobs.itertuples(index = False, name = None)]

    cursor.executemany(sql, rows)
    conn.commit()

    inserted = cursor.rowcount
    skipped = len(jobs) - inserted
    print(f"Saved {inserted} new jobs. Skipped {skipped} duplicates.")

def job_search():
    
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
        save_jobs_to_db(jobs, conn)

def get_setting(key):
    """Read a single setting value from the database."""
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        result = cursor.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
    return result[0] if result else None

def set_setting(key, value):
    """Write a single setting value to the database."""
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE settings SET value = ? WHERE key = ?", (str(value), key)
        )
        conn.commit()

def options_menu():
    opt_input = ""
    while opt_input != "back":

        # Show current settings summary each time the menu loads
        print("\n--- Current Settings ---")
        print(f"  Location mode : {get_setting('location_mode')}")
        print(f"  City          : {get_setting('city')}")
        print(f"  ZIP           : {get_setting('zip')}")
        print(f"  Radius        : {get_setting('radius')} miles")
        print(f"  Posting age   : {get_setting('posting_age')} hours")
        print(f"  Per site      : {get_setting('postings_per_site')} results")
        print(f"  Email enabled : {get_setting('email_enabled')}")
        print(f"  Email sender  : {get_setting('email_sender')}")
        print("\n--- Options Menu ---")
        print("  location  - Change location settings")
        print("  search    - Change search settings")
        print("  sites     - Toggle job sites on/off")
        print("  titles    - Edit job title search terms")
        print("  email     - Change email settings")
        print("  back      - Return to main menu")
        print("")

        opt_input = input("Choose a setting to change: ").lower().strip()

        if opt_input == "location":
            change_location_settings()
        elif opt_input == "search":
            change_search_settings()
        elif opt_input == "sites":
            change_site_settings()
        elif opt_input == "titles":
            change_job_titles()
        elif opt_input == "email":
            change_email_settings()
        elif opt_input != "back":
            print("Unrecognized option.")
        # show the main menu again
        print("  search  - Start a new search")
        print("  options - Change settings")
        print("  list    - Show saved job postings")
        print("  exit    - Quit\n")

def change_location_settings():
    print("\n-- Location Settings --")
    print("  Location mode options: city, zip, remote")
    
    mode = input(f"  Location mode [{get_setting('location_mode')}]: ").strip().lower()
    if mode in ("city", "zip", "remote"):
        set_setting("location_mode", mode)
        print(f"  ✓ Location mode set to '{mode}'")
    elif mode:
        print("  Invalid mode. Must be city, zip, or remote.")

    city = input(f"  City [{get_setting('city')}]: ").strip()
    if city:
        set_setting("city", city)
        print(f"  ✓ City set to '{city}'")

    zip_code = input(f"  ZIP [{get_setting('zip')}]: ").strip()
    if zip_code:
        set_setting("zip", zip_code)
        print(f"  ✓ ZIP set to '{zip_code}'")

    radius = input(f"  Radius in miles [{get_setting('radius')}]: ").strip()
    if radius:
        if radius.isdigit():
            set_setting("radius", radius)
            print(f"  ✓ Radius set to {radius} miles")
        else:
            print("  Invalid radius — must be a number.")

def change_search_settings():
    print("\n-- Search Settings --")

    age = input(f"  Max posting age in hours [{get_setting('posting_age')}]: ").strip()
    if age:
        if age.isdigit():
            set_setting("posting_age", age)
            print(f"  ✓ Posting age set to {age} hours")
        else:
            print("  Invalid value — must be a number.")

    per_site = input(f"  Results per site [{get_setting('postings_per_site')}]: ").strip()
    if per_site:
        if per_site.isdigit():
            set_setting("postings_per_site", per_site)
            print(f"  ✓ Results per site set to {per_site}")
        else:
            print("  Invalid value — must be a number.")

    # ← Add this block
    limit = input(f"  Max jobs to display in list [{get_setting('list_limit')}]: ").strip()
    if limit:
        if limit.isdigit():
            set_setting("list_limit", limit)
            print(f"  ✓ List limit set to {limit}")
        else:
            print("  Invalid value — must be a number.")


def change_site_settings():
    sites = ["linkedin", "indeed", "glassdoor", "zip_recruiter", "google"]
    print("\n-- Job Site Toggle --")

    for site in sites:
        current = get_setting(site)
        toggle = input(f"  {site:<15} (currently {current}) — enable? [y/n]: ").strip().lower()
        if toggle == "y":
            set_setting(site, "True")
            print(f"  ✓ {site} enabled")
        elif toggle == "n":
            set_setting(site, "False")
            print(f"  ✓ {site} disabled")# blank input = keep current value

def change_job_titles():
    print("\n-- Job Title Search Terms --")

    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        titles = [row[0] for row in cursor.execute("SELECT title FROM job_titles").fetchall()]

    print("  Current titles:")
    for i, t in enumerate(titles, 1):
        print(f"    {i}. {t}")

    print("\n  add <title>    - Add a new title")
    print("  remove <title> - Remove a title")
    print("  done           - Finish editing titles")

    while True:
        cmd = input("\n  Command: ").strip()

        if cmd.lower() == "done":
            break
        elif cmd.lower().startswith("add "):
            new_title = cmd[4:].strip().lower()
            with sqlite3.connect(DB) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO job_titles (title) VALUES (?)", (new_title,)
                )
                conn.commit()
            print(f"  ✓ Added '{new_title}'")
        elif cmd.lower().startswith("remove "):
            rem_title = cmd[7:].strip().lower()
            with sqlite3.connect(DB) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM job_titles WHERE title = ?", (rem_title,)
                )
                conn.commit()
            print(f"  ✓ Removed '{rem_title}'")
        else:
            print("  Unknown command. Use 'add <title>', 'remove <title>', or 'done'.")

def change_email_settings():
    print("\n-- Email Settings --")

    enabled = input(f"  Email enabled [{get_setting('email_enabled')}] — enable? [y/n]: ").strip().lower()
    if enabled == "y":
        set_setting("email_enabled", "True")
        print("  ✓ Email enabled")
    elif enabled == "n":
        set_setting("email_enabled", "False")
        print("  ✓ Email disabled")

    sender = input(f"  Sender address [{get_setting('email_sender')}]: ").strip()
    if sender:
        set_setting("email_sender", sender)
        print(f"  ✓ Sender set to '{sender}'")

    password = input("  App password (leave blank to keep current): ").strip()
    if password:
        set_setting("email_password", password)
        print("  ✓ Password updated")

    # Recipients
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        recipients = [r[0] for r in cursor.execute(
            "SELECT address FROM email_recipients"
        ).fetchall()]
    print(f"  Current recipients: {recipients}")
    
    add_rec = input("  Add recipient (leave blank to skip): ").strip()
    if add_rec:
        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO email_recipients (address) VALUES (?)", (add_rec,)
            )
            conn.commit()
        print(f"  ✓ Added '{add_rec}'")

    rem_rec = input("  Remove recipient (leave blank to skip): ").strip()
    if rem_rec:
        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM email_recipients WHERE address = ?", (rem_rec,)
            )
            conn.commit()
        print(f"  ✓ Removed '{rem_rec}'")


if __name__ == "__main__":
    main()
