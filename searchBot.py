import jobspy.google
import config
import csv

from jobspy import scrape_jobs
jobs = scrape_jobs(
    site_name = ["indeed", "linkedin", "zip_recruiter", "google", "glassdoor"],
    search_term = "data analyst",
    google_search_term = "data analyst jobs near bowling green ky since yesterday",
    location = "USA",
    results_wanted = 100,
    hours_old = 48,
    country_indeed = "USA"
    )

print(f"Found {len(jobs)} jobs")
print(jobs.head())
jobs.to_csv("jobs.csv", quoting = csv.QUOTE_NONNUMERIC, escapechar = "\\", index = False)


