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
url = "https://liquipedia.net/pubgmobile/Showmatch_Tournaments"

# Get the HTML content of the page
soup = make_request(url)

# Find all anchor tags (a) with href attributes
anchor_tags = soup.find_all("a", href=True)

# List of links to visit
to_visit = set()

# Extract the href values and print them
# Get all the URLs present on https://liquipedia.net/pubgmobile/Showmatch_Tournaments page
for anchor in anchor_tags:
    if '/pubgmobile/Showmatch_Tournaments' in anchor["href"]:
        to_visit.add(anchor['href'])

# Lists of URLs to visit updated by creating links and adding the BASE_URL
to_visit = set([BASE_URL + str(t) for t in to_visit])



# Create a CSV file to store the data
csv_file_name = 'showmatch.csv'



# ...

# Final result
def return_table_content(table):
    user_data = []
    
    try:
        # Find all table rows using the <div> tag with specific class names
        rows = table.find_all("div", class_="divRow")
        for row in rows:
            cells = row.find_all("div", class_="divCell")
            tmp = {}  # Default value for country_name    
            for index, con in enumerate(cells):
                    try:
                        # Removing entries on the list whose value is ' '
                        con.contents = (list(filter(lambda x: x != ' ', con.contents)))
                
                        if index == 0:
                            # Check if the cell contains an 'a' tag
                            a_tag = con.find("a")
                            if a_tag:
                                tier = a_tag.get_text()
                                tmp['Tier'] = tier
                            else:
                                tmp['Tier'] = ''
                
                        
                        if index == 1:
                            # Check if the cell contains an 'a' tag
                            a_tag = con.find("b")
                            if a_tag:
                                tournament = a_tag.get_text()
                                tmp['Tournament'] = tournament
                            else:
                                tmp['Tournament'] = ''
                
                           
                        if index == 2:
                              date = con.contents[0].strip()
                              tmp["Date"] = date
      
                        if index == 3:
                              prize = con.contents[0].strip()
                              tmp["Prize"] = prize
      
                              
                          
                          
                        if index == 4:
                               location_text = ""
                               for child in con.contents:
                                   if isinstance(child, Tag) and child.name == "span":
                                       location_text += child.get_text()
                                   elif isinstance(child, Tag) and child.name == "div":
                                       location_text += child.get_text()
                                   elif isinstance(child, str):
                                       location_text += child.strip()
                               
                               tmp["Location"] = location_text
                         
                                     
                          
                          
                          
                        if index == 5:
                             for child in con.contents:
                                 if isinstance(child, Tag) and child.name == "span" and not child.has_attr("class"):
                                     participants = child.get_text()
                                     tmp["Participants"] = participants
                                              
                          
                          
                          
                        if index == 6:
                             for child in con.contents:
                                 a_tag = child.find("span", class_="team-template-text")
                                 if a_tag:
                                     x = a_tag.find("a")
                                     if x:
                                         # Extract text outside of brackets
                                         Winner = x.get("title")
                                         Winner_text = Winner.split(" (")[0].strip()
                                     else:
                                         # Handle case where game result is "TBD"
                                         abbr_tag = a_tag.find("abbr", title=True)
                                         if abbr_tag:
                                             Winner_text = abbr_tag.get("title")
                                         else:
                                             Winner_text = ''
                                     tmp["Winner"] = Winner_text
                                     
                        if index == 7:
                             for child in con.contents:
                                 a_tag = child.find("span", class_="team-template-text")
                                 if a_tag:
                                     x = a_tag.find("a")
                                     if x:
                                         # Extract text outside of brackets
                                         Runner_up = x.get("title")
                                         Runner_up_text = Runner_up.split(" (")[0].strip()
                                     else:
                                         # Handle case where game result is "TBD"
                                         abbr_tag = a_tag.find("abbr", title=True)
                                         if abbr_tag:
                                             Runner_up_text = abbr_tag.get("title")
                                         else:
                                             Runner_up_text = ''
                                     
                                     tmp["Runner_up"] = Runner_up_text           
                                     
                    


                    except Exception as e:
                        print(f"Error in processing cell at index {index}: {e}")
            # Append the team data to the list
            user_data.append(tmp)
    except Exception as e:
        print(f"Exception on return_table_content function with exception: {e}")
        pass
    return user_data

# ...
    

# Field names for CSV
fieldnames = [ 'Tier','Tournament', 'Date', 'Prize', 'Location','Participants', 'Winner',  'Runner_up']

# Visit all the URLs in the to_visit set
for url in to_visit:
    print(f"Scraping data from {url}...")
    # Find all the table elements using its class name
    soup = make_request(url)
    tables = soup.find_all("div", class_="divTable table-full-width tournament-card")

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

print(f"Scraping process finished. CSV file created: {csv_file_name}")
