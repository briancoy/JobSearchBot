#-------------------------------------------------------------------------------------------------#
# Configuration file for JobSearchBot
#
# This file contains the configuration for the searches that JobSearchBot will conduct
#-------------------------------------------------------------------------------------------------#


# The names of the job positions returned from each site
job_titles = [
    "data analyst",
    "business analyst",
    "data engineer",
    "analytics engineer"
]

# Locations to be searched, recommend to include city, state - ZIP - And remote if wanted
# Location mode can be "city", "zip", or "remote"

location_mode = "remote"
locations = [
    "Bowling Green, KY",
    "42104",
    "Remote"
]

# Distance from location in miles to search
radius = 50

# Job search settings

# Time frame for job postings (in hours)
posting_age = 24

# Number of postings returned for each site
postings_per_site = 100

# Sites to search. Default to all being True, change to False to not search
sites_to_search = {
    "linkedin": True,
    "indeed": True,
    "glassdoor": True,
    "zip_recruiter": True,
    "google": True
}

# Email settings
# Crrently only works with Gmail as a sender using a Gmail App Password
# Gmail App Password Setup
# You cannot use your regular Gmail password — Google requires an App Password:
# Go to myaccount.google.com/apppasswords
# Sign in → select "Mail" and "Windows Computer" (or any device)
# Copy the generated 16-character password into EMAIL_PASSWORD in config.py
# Make sure 2-Step Verification is enabled on your Google account first


email_enabled = True
email_sender = "your.email@email.com" # Source email address
email_password = "email_password"
email_recipients = ["your.email@email.com"] # Can be a list of emails addresses


