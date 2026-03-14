# Main system

import config
import searchBot
import sqlite3


print("Welcome to JobSearchBot")
print("Search to start a new search")
print("Options to change settings")
print("List to show saved job postings")
print("")
user_input = ""
while user_input != "exit":
    user_input = input("Enter an option or 'exit' to quit: ").lower()
    if user_input == "search":
        searchBot.main()
    elif user_input == "options":
        pass
    elif user_input == "list":
        with sqlite3.connect("jobs.db") as conn:
            cursor = conn.cursor()
            saved_jobs = cursor.execute("""
                SELECT id, site, job_url, title, company FROM jobs
            """)
            for i in saved_jobs:
                print(f"{i}")