import json
import requests
from datetime import datetime, timezone

REPO_URL = "https://raw.githubusercontent.com/Ouckah/Summer2025-Internships/main/.github/scripts/listings.json"

# Pulls the JSON info from the REPO_URL and handles errors
def fetch_listings():
    response = requests.get(REPO_URL)
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

# Gets the n most recently posted internship listings
def get_most_recent_listings(listings, n):
    listings_sorted = sorted(listings, key=lambda x: x['date_updated'], reverse=True)
    return listings_sorted[:n]

# Parses JSON file, formats data, assigns variable names, and prints listings out to terminal
def display_listings(listings):
    for listing in listings:
        date_updated = datetime.fromtimestamp(listing['date_updated'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
        company_name = listing["company_name"]
        role_title = listing["title"]
        print(f"Company: {company_name}")
        print(f"Title: {role_title}")
        print(f"Location: {', '.join(listing['locations'])}")
        print(f"Date Updated: {date_updated}")
        print(f"URL: {listing['url']}")
        print('\n')

# Main method that handles user input
def main():
    while True:
        listings = fetch_listings()
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
