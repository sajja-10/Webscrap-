#!/usr/bin/env python3
import csv
import requests
from bs4 import BeautifulSoup
import os


# Takes a URL and returns the content of that URL as a soup object
def make_request(url):
    # Make request and save the response
    response = requests.get(url)
    # Parse the HTML content using Beautiful Soup
    return BeautifulSoup(response.content, "html.parser")

BASE_URL = 'https://liquipedia.net'

# Define the URL of the web page you want to scrape
url = "https://liquipedia.net/pubgmobile/Portal:Players"

# Get the HTML content of the page
soup = make_request(url)

# Find all anchor tags (a) with href attributes
anchor_tags = soup.find_all("a", href=True)

# List of links to visit
to_visit = set()

# Extract the href values and print them
# Get all the URLs present on https://liquipedia.net/pubgmobile/Portal:Players page
for anchor in anchor_tags:
    if '/pubgmobile/Portal:Players/' in anchor["href"]:
        to_visit.add(anchor['href'])

# Lists of URLs to visit updated by creating links and adding the BASE_URL
to_visit = set([BASE_URL + str(t) for t in to_visit])

# Create a CSV file to store the data
csv_file_name = 'players.csv'


# Final result
def return_table_content(table):
    try:
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
                if index == 0:
                  try:
                      for child in con.contents:
                          a_tag = child.find("a")
                          img_title = child.find("img")
                          player_id = a_tag.get_text()
                          player_link = BASE_URL + '/pubgmobile/' + str(player_id)
                          
                          # Extract country name from the HTML structure
                          country_element = con.find("span", class_="flag")
                          country_name = country_element.find("img")["alt"] if country_element else ""
                          
                          tmp['player_id'] = player_id
                          tmp["player_link"] = player_link
                          tmp["country_name"] = country_name  # Add country name to the dictionary
                      # Handle cases where the value is null
                  except IndexError as e:
                      tmp["player_id"] = ''
                      tmp["player_link"] = ''
                      tmp["country_name"] = ''
                                            
               
                if index == 1:
                    try:
                        real_name = con.contents[0].strip()
                        tmp["real_name"] = real_name
                    # Handle cases where the value is null
                    except IndexError as e:
                        tmp['real_name'] = ''
                # Contains country name and ID of the player
               
                if index == 2:
                    try:
                        for child in con.contents:
                            a_tag = (child.find("a"))
                            team_link = a_tag.get("href")
                            team_name = a_tag.contents[0].get("alt")
                            tmp['team_link'] = BASE_URL + '/' + str(team_link)
                            tmp['team_name'] = team_name
                    # Handle cases where the value is null
                    except IndexError as e:
                        tmp["team_link"] = ''
                        tmp['team_name'] = ''
                if index == 3:
                    try:
                        socials = []
                        for a_tag in (con.contents):
                            socials.append(a_tag.get('href'))
                        tmp['socials'] = socials
                    # Handle cases where the value is null
                    except IndexError as e:
                        tmp["socials"] = []

            # Append the player data to the list
            user_data.append(tmp)

        return user_data
    except Exception as e:
        print(f"Exception on return_table_content function with exception: {e}")
        pass

# ...
fieldnames = ['real_name', 'player_id', 'country_name', 'team_name', 'player_link', 'team_link', 'socials']

# Visit all the URLs in the to_visit set
for url in to_visit:
    print(f"Scraping data from {url}...")
    # Find all the table elements using its class name
    soup = make_request(url)
    tables = soup.find_all("table", class_="wikitable collapsible smwtable")

    if not tables:
        print(f"No tables found on {url}. Skipping...")
        continue  # Skip this URL and move on to the next one

    # Write the scraped data to the CSV file for each table
    for table in tables:
        scraped_data = return_table_content(table)
        with open(csv_file_name, mode='a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Check if the CSV file is empty, and if so, write the header row
            if os.path.getsize(csv_file_name) == 0:
                writer.writeheader()

            for item in scraped_data:
                writer.writerow(item)

    print(f"Scraping from {url} completed. Data appended to {csv_file_name}")

print("Scraping process finished. CSV file created: players_data.csv")
