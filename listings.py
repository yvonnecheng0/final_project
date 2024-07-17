import json
import requests
from datetime import datetime, timezone

REPO_URL = "https://raw.githubusercontent.com/Ouckah/Summer2025-Internships/main/.github/scripts/listings.json"

# Pulls the JSON info from the REPO_URL and handles errors
def fetch_listings(url):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return []
    elif (response.status_code == 400):
        print("Client Error!!")
    elif (response.status_code == 500):
        print("Server Error!")
    else:
        print(f"Failed to fetch listings: {response.status_code}")
    return []

# Parses through a single listing and formats the data. Returns relevant data as dictionary
def format_listing(listing):
    date_updated = datetime.fromtimestamp(listing['date_updated'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    company_name = listing["company_name"]
    role_title = listing["title"]
    role_locations = listing["locations"]
    posting_url = listing["url"]
    return {"date": date_updated, "company": company_name, "title": role_title, "locations": role_locations, "url": posting_url}

# Gets the n most recently posted internship listings
def get_most_recent_listings(listings, n):
    listings_sorted = sorted(listings, key=lambda x: x['date_updated'], reverse=True)
    return listings_sorted[:n]

# Iterates through listings and prints each one out to terminal
def display_listings(listings):
    for listing in listings:
        data = format_listing(listing)
        print(f"Company: {data["company"]}")
        print(f"Title: {data["title"]}")
        print(f"Location: {', '.join(data["locations"])}")
        print(f"Date Updated: {data["date"]}")
        print(f"URL: {data["url"]}")
        print('\n')

# Main method that handles user input
def main():
    while True:
        listings = fetch_listings(REPO_URL)
        if listings:
            n = int(input("Enter the number of most recent job listings to display: "))
            most_recent_listings = get_most_recent_listings(listings, n)
            display_listings(most_recent_listings)
            print(f"Those were the most recent {n} listings.\n")
            break
        else:
            print("No listings found.")
        

if __name__ == "__main__":
    main()
