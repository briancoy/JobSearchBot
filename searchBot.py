
import config
from jobspy import scrape_jobs
import csv

from jobspy import scrape_jobs
jobs = scrape_jobs(
    # Build active search lists from config file
    site_name = [key for key, value in config.sites_to_search.items() if value is True],
    search_term = config.job_titles[0],
    google_search_term = f"{config.job_titles[0]} jobs near {config.locations[0]} since yesterday",
    location = config.locations[0],
    results_wanted = config.postings_per_site,
    hours_old = config.posting_age,
    country_indeed = "USA",
    distance = config.radius
    )

print(f"Found {len(jobs)} jobs")
print(jobs.head())
jobs.to_csv("jobs.csv", quoting = csv.QUOTE_NONNUMERIC, escapechar = "\\", index = False)


