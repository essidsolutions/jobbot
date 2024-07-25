import os
import re
import requests
from datetime import datetime  
from xml.etree import ElementTree as ET

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d")

def download_main_sitemap(name, sitemap_url):
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


def download_all_sitemaps(name):
    # Parse the XML file
    main_sitemaps = f"collected/{name}/sitemap/main"
    sub_sitemaps = f"collected/{name}/sitemap/sub"
    os.makedirs(sub_sitemaps, exist_ok=True)
    # print all the files in the main sitemap folder
    # download them inside the sub sitemap folder
    # store the sitemap urls in a database for future reference
    # store all data in the database including emails and phone numbers and other contact information
    
def download_htmls(name):
    # Parse the XML file
    # Get the URLs
    # Download the HTML files
    # Store the HTML files in a folder
    # Store the HTML files in a database
    # Delete the HTML files after a certain period of time
    pass

