import os
import re
import requests
from datetime import datetime  
from xml.etree import ElementTree as ET
import pandas as pd

name = "itjobs_pt"
robots_url = "https://www.itjobs.pt/robots.txt"
sitename_utl = "https://www.itjobs.pt/sitemap.xml"

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d")

def download_main_sitemap(sitemap_url):
    filename = f"sitemap_{current_date}.xml"
    # Set a user-agent header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        # Write the content to a local file
        with open(f"collected/{name}/sitemap/main/{filename}", "wb") as file:
            file.write(response.content)
        print(f"Sitemap downloaded successfully as {filename}.")
    else:
        print(f"Failed to download sitemap. Status code: {response.status_code}")



def get_last_sitemap():
    # Parse the XML file
    main_sitemaps = f"collected/{name}/sitemap/main"
    sub_sitemaps = f"collected/{name}/sitemap/sub"
    os.makedirs(sub_sitemaps, exist_ok=True)
    # List all files in the directory
    all_main_sitemaps = os.listdir(main_sitemaps)
    # Define a regex pattern to match files with the format sitemap_YYYYMMDD.xml
    pattern = re.compile(r'sitemap_(\d{8}).xml')
    # Create a list to store matched files and their dates
    dated_files = []

    for file in all_main_sitemaps:
        match = pattern.match(file)
        if match:
            # Extract the date part of the filename
            date_str = match.group(1)
            # Parse the date string to a datetime object
            date = datetime.strptime(date_str, '%Y%m%d')
            dated_files.append((file, date))
    # Sort the files by date
    dated_files.sort(key=lambda x: x[1], reverse=True)
    # Get the latest file
    latest_file = dated_files[0][0] if dated_files else None

    full_main_sitemap = os.path.join(f"collected/{name}/sitemap/main",latest_file)
    return full_main_sitemap

    # print all the files in the main sitemap folder
    # download them inside the sub sitemap folder
    # store the sitemap urls in a database for future reference
    # store all data in the database including emails and phone numbers and other contact information




def extract_urls_from_sitemap(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('.//ns:loc', namespaces)]

    return urls

def main():
    file_path = '/Users/mcessid/Documents/Projects/Essid Solutions/Internal/Development/Github/jobbot/itjobs_pt/sitemap/main/sitemap_20240725.xml'  # Update this to the correct path
    urls = extract_urls_from_sitemap(file_path)

    urls_df = pd.DataFrame(urls, columns=["URL"])
    print(urls_df)

if __name__ == "__main__":
    main()