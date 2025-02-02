import requests
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET

base_url = 'https://www.senate.gov'
votingrecords_dir = "votingrecords"

if not os.path.exists(votingrecords_dir):
    os.makedirs(votingrecords_dir)

completed_years = set()
incomplete_years = {}

for year in os.listdir(votingrecords_dir):
    year_path = os.path.join(votingrecords_dir, year, "bill")
    
    if os.path.isdir(year_path):
        bills = sorted(os.listdir(year_path))
        
        if bills and "1.xml" in bills: 
            completed_years.add(year)
        else:
            incomplete_years[year] = sorted(int(b.replace(".xml", "")) for b in bills if b.endswith(".xml"))  

r = requests.get(f'{base_url}/legislative/common/generic/roll_call_lists.htm')
soup = BeautifulSoup(r.content, 'html.parser')

div = soup.find('div', class_='newspaperDisplay_3column')

if not div:
    print("Div with class 'newspaperDisplay_3column' not found.")
    exit()

link_list = [link.get('href') for link in div.find_all('a')]
updated_links = [i.replace('.htm', '.xml') for i in link_list]

for i, xml_path in enumerate(updated_links):
    year = str(2025 - i) 

    if year in completed_years:
        print(f"Skipping {year}, already fully processed.")
        continue

    xml_url = f'{base_url}{xml_path}'
    
    r = requests.get(xml_url)
    if r.status_code != 200:
        print(f"Failed to fetch {year} roll call list. Skipping...")
        continue

    os.makedirs(f'votingrecords/{year}/bill', exist_ok=True)

    xml_file_path = f'votingrecords/{year}/{year}.xml'
    with open(xml_file_path, 'w', encoding="utf-8") as f:
        f.write(r.text)

    try:
        tree = ET.ElementTree(ET.fromstring(r.content))
        root = tree.getroot()
    except ET.ParseError:
        print(f"Failed to parse XML for {year}. Skipping...")
        continue

    vote_numbers = [int(vn.text.strip()) for vn in root.findall(".//vote_number") if vn.text]
    
    if not vote_numbers:
        print(f"No votes found for {year}. Skipping...")
        continue

    congress_numbers = [cn.text.strip() for cn in root.findall(".//congress") if cn.text]
    session_numbers = [sn.text.strip() for sn in root.findall(".//session") if sn.text]

    if not (congress_numbers and session_numbers):
        print(f"Missing Congress/Session data for {year}. Skipping vote bills...")
        continue

    congress, session = congress_numbers[0], session_numbers[0]

    last_completed_vote = max(incomplete_years.get(year, [0]) or [0])  

    for vote in sorted(vote_numbers):
        if vote <= last_completed_vote:
            continue 

        bill_url = f'{base_url}/legislative/LIS/roll_call_votes/vote{congress}{session}/vote_{congress}_{session}_{vote}.xml'
        bill_response = requests.get(bill_url)

        if bill_response.status_code == 200:
            bill_path = f'votingrecords/{year}/bill/{vote}.xml'
            with open(bill_path, 'w', encoding="utf-8") as f:
                f.write(bill_response.text)
            print(f"Saved vote {vote} for {year}.")
        else:
            print(f"Failed to fetch vote {vote} for {year}.")

    print(f"Year {year} processed successfully.")

print("Completed downloading Senate voting records.")