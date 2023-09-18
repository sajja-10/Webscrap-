#!/usr/bin/env python3
import csv
import requests
from bs4 import BeautifulSoup, Tag
import os

# Takes a URL and returns the content of that URL as a soup object
def make_request(url):
    # Make request and save the response
    response = requests.get(url)
    # Parse the HTML content using Beautiful Soup
    return BeautifulSoup(response.content, "html.parser")

BASE_URL = 'https://liquipedia.net'

# Define the URL of the web page you want to scrape
url = "https://liquipedia.net/pubgmobile/Portal:Statistics/Player_earnings"

# Get the HTML content of the page
soup = make_request(url)

# Find all anchor tags (a) with href attributes
anchor_tags = soup.find_all("a", href=True)

# List of links to visit
to_visit = set()

# Extract the href values and print them
# Get all the URLs present on https://liquipedia.net/pubgmobile/Portal:Statistics/Player_earnings page
for anchor in anchor_tags:
    if '/pubgmobile/Portal:Statistics/Player_earnings' in anchor["href"]:
        to_visit.add(anchor['href'])

# Lists of URLs to visit updated by creating links and adding the BASE_URL
to_visit = set([BASE_URL + str(t) for t in to_visit])

# Create a CSV file to store the data
csv_file_name = 'stat_player.csv'

def return_table_content(table):
    player_info = []
    # Find the correct HTML structure within the div element
    # where player IDs and links are located
    name_spans = table.find_all("span", class_="name")
    for span in name_spans:
        a_tag = span.find("a")
        country_element = span.find_parent("tr").find("div", class_="block-player")
        country_name = country_element.find("img")["alt"] if country_element else ""
        if a_tag:
            player_id = a_tag.get_text()
            player_link = BASE_URL + a_tag["href"]
            
            player_info.append({"player_id": player_id, "player_link": player_link, "country_name": country_name})
    
    user_data = []
    # Find all table rows using the <tr> tag
    rows = table.find_all("tr")
    for row in rows[1:]:
        cells = row.find_all("td")
        tmp = {'country_name': ''}  # Default value for country_name
        for index, con in enumerate(cells):
            # Removing entries on the list whose value is ' '
            con.contents = (list(filter(lambda x: x != ' ', con.contents)))
            # Real name of the player


            if index == 3:
                try:
                    first = con.contents[0].strip()
                    tmp["first"] = first
                except IndexError as e:
                    tmp['first'] = ''

            if index == 4:
                try:
                    second = con.contents[0].strip()
                    tmp["second"] = second
                except IndexError as e:
                    tmp['second'] = ''

            if index == 5:
                try:
                    third = con.contents[0].strip()
                    tmp["third"] = third
                except IndexError as e:
                    tmp['third'] = ''

            if index == 6:
                try:
                    earnings = con.contents[0].strip()
                    tmp["earnings"] = earnings
                except IndexError as e:
                    tmp['earnings'] = ''
                    
            

        # Append the player data to the list
        if player_info:
            user_data.append({**tmp, **player_info.pop(0)})
        else:
            user_data.append(tmp)  # Append a row with default values if player_info is empty

    return user_data

# Field names for CSV
fieldnames = ['player_id', 'player_link', 'first', 'second', 'third', 'earnings', 'country_name']

# Visit all the URLs in the to_visit set
for url in to_visit:
    print(f"Scraping data from {url}...")
    soup = make_request(url)
    tables = soup.find_all("div", class_="table-responsive")

    if not tables:
        print(f"No tables found on {url}. Skipping...")
        continue  # Skip this URL and move on to the next one

    with open(csv_file_name, mode='a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()

        scraped_data = return_table_content(tables[0])  # Use return_table_content directly
        writer.writerows(scraped_data)

    print(f"Scraping from {url} completed. Data appended to {csv_file_name}")

print("Scraping process finished. CSV file created: x.csv")
