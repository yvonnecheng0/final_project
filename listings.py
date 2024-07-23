import json
import requests
from datetime import datetime, timezone
from databases import *

REPO_URL = "https://raw.githubusercontent.com/Ouckah/Summer2025-Internships/main/.github/scripts/listings.json"


def fetch_listings(url):
    """Pulls the JSON from the REPO_URL and prints errors to terminal, returns JSON response as list"""
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return []
    elif response.status_code == 400:
        print("Client Error!!")
    elif response.status_code == 500:
        print("Server Error!")
    else:
        print(f"Failed to fetch listings: {response.status_code}")
    return []


def format_listing(listing):
    """Parses through a single listing and formats the data. Returns relevant data as dictionary"""
    date_posted = datetime.fromtimestamp(listing['date_posted'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    date_updated = datetime.fromtimestamp(listing['date_updated'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    company_name = listing["company_name"]
    role_title = listing["title"]
    season = listing["season"]
    sponsored = listing["sponsorship"]
    role_locations = listing["locations"]
    posting_url = listing["url"]
    active = 1 if listing["active"] else 0
    return {
        "season": season,
        "posted": date_posted,
        "updated": date_updated,
        "company": company_name,
        "title": role_title,
        "locations": role_locations,
        "url": posting_url,
        "active": active,
        "sponsorship": sponsored
    }


def get_most_recent_listings(listings, n):
    """Returns the n most recently updated internship listings as a list"""
    listings_sorted = sorted(listings, key=lambda x: x['date_updated'], reverse=True)
    return listings_sorted[:n]


def set_listings():
    """Initializes everything, creates jobs_tracker.db if it didn't exist before"""
    create_tables()
    listings = fetch_listings(REPO_URL)
    for listing in listings:
        list_dict = format_listing(listing)
        quick_add_job(list_dict)
