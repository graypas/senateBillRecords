import requests
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET

base_url = 'https://www.senate.gov'
completed_years_file = "completed_years.txt"

if os.path.exists(completed_years_file):
    with open(completed_years_file, "r") as f:
        completed_years = set(f.read().splitlines())
else:
    completed_years = set()

r = requests.get(f'{base_url}/legislative/common/generic/roll_call_lists.htm')
soup = BeautifulSoup(r.content, 'html.parser')

div = soup.find('div', class_='newspaperDisplay_3column')

if not div:
    print("Div with class 'newspaperDisplay_3column' not found.")
    exit()

link_list = [link.get('href') for link in div.find_all('a')]
updated_links = [i.replace('.htm', '.xml') for i in link_list]

votenumberbyyear = {}

for i, xml_path in enumerate(updated_links):
    year = 2025 - i  

    if str(year) in completed_years:
        print(f"Skipping {year}, already processed.")
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

    vote_numbers = [vn.text.strip() for vn in root.findall(".//vote_number") if vn.text]
    votenumberbyyear[year] = vote_numbers

    congress_numbers = [cn.text.strip() for cn in root.findall(".//congress") if cn.text]
    session_numbers = [sn.text.strip() for sn in root.findall(".//session") if sn.text]

    if not (congress_numbers and session_numbers):
        print(f"Missing Congress/Session data for {year}. Skipping vote bills...")
        continue

    congress, session = congress_numbers[0], session_numbers[0]

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

    with open(completed_years_file, "a") as f:
        f.write(f"{year}\n")
    completed_years.add(str(year))  

print("Completed downloading Senate voting records.")


# import requests
# from bs4 import BeautifulSoup
# import os
# import xml.etree.ElementTree as ET

# base_url = 'https://www.senate.gov'

# r = requests.get(f'{base_url}/legislative/common/generic/roll_call_lists.htm')
# soup = BeautifulSoup(r.content, 'html.parser')

# div = soup.find('div', class_='newspaperDisplay_3column')

# if not div:
#     print("Div with class 'newspaperDisplay_3column' not found.")
#     exit()

# link_list = [link.get('href') for link in div.find_all('a')]
# updated_links = [i.replace('.htm', '.xml') for i in link_list]

# votenumberbyyear = {}

# for i, xml_path in enumerate(updated_links):
#     year = 2025 - i  
#     xml_url = f'{base_url}{xml_path}'
    
#     r = requests.get(xml_url)
#     if r.status_code != 200:
#         print(f"Failed to fetch {year} roll call list. Skipping...")
#         continue

#     os.makedirs(f'votingrecords/{year}/bill', exist_ok=True)

#     xml_file_path = f'votingrecords/{year}/{year}.xml'
#     with open(xml_file_path, 'w', encoding="utf-8") as f:
#         f.write(r.text)

#     try:
#         tree = ET.ElementTree(ET.fromstring(r.content))
#         root = tree.getroot()
#     except ET.ParseError:
#         print(f"Failed to parse XML for {year}. Skipping...")
#         continue

#     vote_numbers = [vn.text.strip() for vn in root.findall(".//vote_number") if vn.text]
#     votenumberbyyear[year] = vote_numbers

#     congress_numbers = [cn.text.strip() for cn in root.findall(".//congress") if cn.text]
#     session_numbers = [sn.text.strip() for sn in root.findall(".//session") if sn.text]

#     if not (congress_numbers and session_numbers):
#         print(f"Missing Congress/Session data for {year}. Skipping vote bills...")
#         continue

#     congress, session = congress_numbers[0], session_numbers[0]

#     for vote in vote_numbers:
#         bill_url = f'{base_url}/legislative/LIS/roll_call_votes/vote{congress}{session}/vote_{congress}_{session}_{vote}.xml'
#         bill_response = requests.get(bill_url)

#         if bill_response.status_code == 200:
#             bill_path = f'votingrecords/{year}/bill/{vote}.xml'
#             with open(bill_path, 'w', encoding="utf-8") as f:
#                 f.write(bill_response.text)
#             print(f"Saved vote {vote} for {year}.")
#         else:
#             print(f"Failed to fetch vote {vote} for {year}.")

# print("Completed downloading Senate voting records.")
