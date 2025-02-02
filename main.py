# import requests
# from bs4 import BeautifulSoup
# import os
# import xml.etree.ElementTree as ET

# base_url = 'https://www.senate.gov'

# r = requests.get(f'{base_url}/legislative/common/generic/roll_call_lists.htm')
# soup = BeautifulSoup(r.content, 'html.parser')

# div = soup.find('div', class_='newspaperDisplay_3column')

# link_list = []
# year = 2025 

# if div:
#     links = div.find_all('a')
#     for link in links:
#         link_list.append(link.get('href'))
# else:
#     print("Div with class 'newspaperDisplay_3column' not found.")

# updated_links = [i.replace('.htm', '.xml') for i in link_list]

# votenumberbyyear = {}

# for i in range(len(updated_links)):
#     xml_url = f'{base_url}{updated_links[i]}'
#     r = requests.get(xml_url)

#     if r.status_code == 200:
#         os.makedirs(f'votingrecords/{year}/bill', exist_ok=True)

#         xml_file_path = f'votingrecords/{year}/{year}.xml'
#         with open(xml_file_path, 'w', encoding="utf-8") as f:
#             f.write(r.text)  

#         tree = ET.parse(xml_file_path)
#         root = tree.getroot()

#         vote_number = [vote_number.text.strip() for vote_number in root.findall(".//vote_number") if vote_number.text]
#         votenumberbyyear[year] = vote_number

#         numbercongress = [congress.text.strip() for congress in root.findall(".//congress") if congress.text]

#         session = [session.text.strip() for session in root.findall(".//session") if session.text]

#         for yr, bills in votenumberbyyear.items():
#             xml_url = f'{base_url}/legislative/LIS/roll_call_votes/vote{numbercongress[0]}{session[0]}/vote_{numbercongress[0]}_{session[0]}_{bills[0]}.xml'
#             r = requests.get(xml_url)
#             with open(f'votingrecords/{year}/bill/{bills[0]}.xml', 'w', encoding="utf-8") as f:
#                 f.write(r.text)

import requests
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET

base_url = 'https://www.senate.gov'

# Fetch the main Senate roll call vote page
r = requests.get(f'{base_url}/legislative/common/generic/roll_call_lists.htm')
soup = BeautifulSoup(r.content, 'html.parser')

# Find the div containing vote links
div = soup.find('div', class_='newspaperDisplay_3column')

if not div:
    print("Div with class 'newspaperDisplay_3column' not found.")
    exit()

# Extract and update vote list links
link_list = [link.get('href') for link in div.find_all('a')]
updated_links = [i.replace('.htm', '.xml') for i in link_list]

# Dictionary to track votes per year
votenumberbyyear = {}

# Loop through each year
for i, xml_path in enumerate(updated_links):
    year = 2025 - i  # Deduce the year based on order
    xml_url = f'{base_url}{xml_path}'
    
    # Request the XML file
    r = requests.get(xml_url)
    if r.status_code != 200:
        print(f"Failed to fetch {year} roll call list. Skipping...")
        continue

    # Create directories
    os.makedirs(f'votingrecords/{year}/bill', exist_ok=True)

    # Save the XML file
    xml_file_path = f'votingrecords/{year}/{year}.xml'
    with open(xml_file_path, 'w', encoding="utf-8") as f:
        f.write(r.text)

    # Parse XML file
    try:
        tree = ET.ElementTree(ET.fromstring(r.content))
        root = tree.getroot()
    except ET.ParseError:
        print(f"Failed to parse XML for {year}. Skipping...")
        continue

    # Extract vote numbers
    vote_numbers = [vn.text.strip() for vn in root.findall(".//vote_number") if vn.text]
    votenumberbyyear[year] = vote_numbers

    # Extract Congress and Session numbers
    congress_numbers = [cn.text.strip() for cn in root.findall(".//congress") if cn.text]
    session_numbers = [sn.text.strip() for sn in root.findall(".//session") if sn.text]

    if not (congress_numbers and session_numbers):
        print(f"Missing Congress/Session data for {year}. Skipping vote bills...")
        continue

    congress, session = congress_numbers[0], session_numbers[0]

    # Fetch and save individual bill votes
    for vote in vote_numbers:
        bill_url = f'{base_url}/legislative/LIS/roll_call_votes/vote{congress}{session}/vote_{congress}_{session}_{vote}.xml'
        bill_response = requests.get(bill_url)

        if bill_response.status_code == 200:
            bill_path = f'votingrecords/{year}/bill/{vote}.xml'
            with open(bill_path, 'w', encoding="utf-8") as f:
                f.write(bill_response.text)
            print(f"Saved vote {vote} for {year}.")
        else:
            print(f"Failed to fetch vote {vote} for {year}.")

print("Completed downloading Senate voting records.")
