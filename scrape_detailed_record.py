import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_paper_details(url):
    response = requests.get(url)

    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')

        # def find_data_by_title(title):
        #     result = soup.find('p', {'class': 'detail-each-title'}).find_next('p')
        #     if title == 'View Research Summary:':
        #         result = soup.find('p', {'class': 'detail-each-title'}, text=lambda x: x and x.startswith('View')).find_next('p')
        #     if result.find('a'):
        #         return result.find('a').get('href')
        #     return result.get_text(separator='\n')

        title = soup.find('p', {'class': 'detail-title'}).get_text(separator='\n')
        try:
            rs = soup.find('a', {'id': 'rs'})['onclick'].split("'")[1] 
        except Exception: 
            rs = None
        apa_citation = soup.find('p', string=re.compile('APA Citation: ')).find_next('p').get_text(separator='\n')
        try:
            abstract_reach = soup.find('p', string=re.compile('Abstract Created by REACH:')).find_next('p').get_text(separator='\n')
        except Exception: 
            abstract_reach = None
        doi = soup.find('p', string=re.compile('DOI:')).find_next('a').get_text(separator='\n')
        focus = soup.find('p', string=re.compile('Focus:')).find_next('p').get_text(separator='\n')
        subject_affiliation = soup.find('p', string=re.compile('Subject Affiliation: ')).find_next('p').get_text(separator='\n')
        population = soup.find('p', string=re.compile('Population: ')).find_next('p').get_text(separator='\n')
        methodology = soup.find('p', string=re.compile('Methodology: ')).find_next('p').get_text(separator='\n')
        authors = soup.find('p', string=re.compile('Authors:')).find_next('p').get_text(separator='\n')
        abstract = soup.find('p', string=re.compile('Abstract:')).find_next('p').get_text(separator='\n')
        publisher = soup.find('p', string=re.compile('Publisher/Sponsoring Organization:')).find_next('p').get_text(separator='\n')
        publication_type = soup.find('p', string=re.compile('Publication Type:')).find_next('p').get_text(separator='\n')
        author_affiliation = soup.find('p', string=re.compile('Author Affiliation:')).find_next('p').get_text(separator='\n')
        keywords = soup.find('p', string=re.compile('Keywords:')).find_next('p').get_text(separator='\n')
        try:
            reach_publication_type = soup.find('p', string=re.compile('REACH Publication Type: ')).find_next('p').get_text(separator='\n')
        except Exception: 
            reach_publication_type = None
        
        try:
            sponsors = soup.find('p', string=re.compile('Sponsors: ')).find_next('p').get_text(separator='\n')
        except Exception: 
            sponsors = None
        try:
            view_research_summary = soup.find('p', string=re.compile('View Research Summary:')).find_next('a')['href']
        except Exception: 
            view_research_summary = None
        url = soup.find('div', string=re.compile('URL:')).find_next('a')['href']



        return {
            'title': title,
            'rs': rs,
            'apaCitation': apa_citation,
            'abstractReach': abstract_reach,
            'doi': doi,
            'focus': focus,
            'subjectAffiliation': subject_affiliation,
            'population': population,
            'methodology': methodology,
            'authors': authors,
            'abstract': abstract,
            'publisher': publisher,
            'publication_type': publication_type,
            'authorAffiliation': author_affiliation,
            'keywords': keywords,
            # 'research_summary': research_summary,
            # 'url': url,
            'reachPublicationType': reach_publication_type,
            'sponsors': sponsors
        }


# for each line in csv try to scrape the paper details

import csv
import time
uuid_list = []
with open('hrefs.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    json_object = {}
    for i, row in enumerate(reader):
        try:
            print(f"{i}: " + row['links'])
            paper_details = scrape_paper_details(row['links'])
            #get the uuid from the row
            uuid = row['links'].split('=')[1]
            if uuid in uuid_list:
                print('duplicate uuid: ' + uuid)
            else:
                uuid_list.append(uuid)
            


            # append to json object
            json_object[uuid] = paper_details

        except Exception as e:
            print('error for ' + row['links'] + ': ' + str(e))

    print(json.dumps(json_object, indent=4, sort_keys=True))

    with open('reach_data_new.json', 'a') as outfile:
        json.dump(json_object, outfile)   
# Replace 'url_to_the_paper' with the actual URL of the paper
# url = 'https://militaryreach.auburn.edu/dr?id=535b1a14-01f7-4669-977d-972480482bb3'
# paper_details = scrape_paper_details(url)
# print(json.dumps(paper_details, indent=4, sort_keys=True))
# print(paper_details)
# Then, you can use this dictionary to add a new record to your database.