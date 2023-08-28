# import requests
# from bs4 import BeautifulSoup
# import re

# # List of URLs you want to scrape
# urls = ['https://militaryreach.auburn.edu/SearchResult?searchterm=&searchtype=primarysearch&page=1']

# # For storing the scraped hrefs
# hrefs = []

# # Regular expression pattern for hrefs
# pattern = re.compile(r'^dr\?id=[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')

# for url in urls:
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Change 'selector' to the actual selector for your links
#     for link in soup.select('selector'):
#         href = link.get('href')
#         if pattern.match(href):
#             hrefs.append(href)

# # Print out the scraped hrefs
# for href in hrefs:
#     print(href)


import requests
from bs4 import BeautifulSoup
import re
import csv
from concurrent.futures import ThreadPoolExecutor

urls = []
for i in range(2, 30):
    urls.append(f'https://militaryreach.auburn.edu/SearchResult?searchterm=&searchtype=primarysearch&page={i}')

# For storing the scraped hrefs
hrefs = []

# Regular expression pattern for hrefs
pattern = re.compile(r'^dr\?id=[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')
print(urls)

import time
# def fetch_and_parse(url):
for url in urls:
    print(url)
    time.sleep(1)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Change 'selector' to the actual selector for your links
    for link in soup.select('a.search-title'):
        # print(link)
        href = link.get('href')  
        if pattern.match(href):
            print("found")
            # Append to base URL and add to list
            hrefs.append("https://militaryreach.auburn.edu/" + href)

# # Create a ThreadPoolExecutor
# with ThreadPoolExecutor(max_workers=20) as executor:
#     # Start fetching and parsing for all URLs
#     executor.map(fetch_and_parse, urls)

# Save the scraped hrefs to a CSV file
with open('hrefs.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Add column header
    writer.writerow(['links'])
    for href in hrefs:
        writer.writerow([href])