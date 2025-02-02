import os
import xml.etree.ElementTree as ET
import json

base_dir = "votingrecords"

senator_votes = {}

for year in sorted(os.listdir(base_dir), reverse=True):
    year_path = os.path.join(base_dir, year, "bill")
    
    if not os.path.isdir(year_path):
        continue  

    for bill_file in os.listdir(year_path):
        bill_path = os.path.join(year_path, bill_file)
        
        if not bill_file.endswith(".xml"):
            continue  

        try:
            tree = ET.parse(bill_path)
            root = tree.getroot()

            bill_name = bill_file.replace(".xml", "")

            for member in root.findall(".//member"):
                senator_name = member.find("member_full").text.strip()
                vote_cast = member.find("vote_cast").text.strip()  

                if senator_name not in senator_votes:
                    senator_votes[senator_name] = {}

                senator_votes[senator_name][bill_name] = {
                    "year": int(year),
                    "vote": vote_cast
                }

        except ET.ParseError:
            print(f"Error parsing XML: {bill_path}")
        except AttributeError:
            print(f"Missing data in: {bill_path}")

output_file = "senator_votes.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(senator_votes, f, indent=4)

print(f"Senator voting records saved to {output_file}.")