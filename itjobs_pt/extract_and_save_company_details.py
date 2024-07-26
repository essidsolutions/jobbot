import xml.etree.ElementTree as ET
import sqlite3
import os
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_urls_from_sitemap(file_path):
    logging.info("Starting to parse the XML sitemap 📄")
    tree = ET.parse(file_path)
    root = tree.getroot()

    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('.//ns:loc', namespaces)]
    
    logging.info(f"Extracted {len(urls)} URLs from the sitemap 🌐")
    return urls

def save_urls_to_db(urls, db_path):
    logging.info("Connecting to the SQLite database 🗄️")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE
    )
    ''')

    logging.info("Inserting URLs into the database 🚀")
    for url in urls:
        try:
            cursor.execute('INSERT INTO urls (url) VALUES (?)', (url,))
        except sqlite3.IntegrityError:
            logging.warning(f"Duplicate URL found and ignored: {url} ⚠️")
            # Ignore duplicate URLs
            pass

    conn.commit()
    conn.close()
    logging.info("URLs have been saved to the database 🎉")

def fetch_urls_from_db(db_path):
    logging.info("Fetching URLs from the database 📋")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT url FROM urls')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def extract_all_sitemaps(urls):
    logging.info("Extracting all sitemaps from the URLs 🌐")
    all_sitemaps = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    for url in urls:
        logging.info(f"Fetching sitemaps from URL: {url}")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tree = ET.ElementTree(ET.fromstring(response.content))
            root = tree.getroot()

            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            sitemaps = [elem.text for elem in root.findall('.//ns:loc', namespaces)]
            all_sitemaps.extend(sitemaps)
            logging.info(f"Extracted {len(sitemaps)} sitemaps from {url}")
        else:
            logging.warning(f"Failed to fetch sitemaps from {url} (status code: {response.status_code})")

    return all_sitemaps

def extract_company_details(sitemap_urls):
    logging.info("Extracting company details from each sitemap URL")
    company_details_list = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    for url in sitemap_urls:
        logging.info(f"Fetching company details from URL: {url}")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            details = {
                'name': soup.find('h1', {'class': 'title'}).get_text(strip=True) if soup.find('h1', {'class': 'title'}) else '',
                'about': soup.find('h2', {'class': 'company-description'}).get_text(strip=True) if soup.find('h2', {'class': 'company-description'}) else '',
                'logo': soup.find('div', {'class': 'company-logo'}).find('img')['src'] if soup.find('div', {'class': 'company-logo'}) and soup.find('div', {'class': 'company-logo'}).find('img') else '',
                'address': soup.find('span', itemprop='address').get_text(strip=True) if soup.find('span', itemprop='address') else '',
                'email': soup.find('a', href=lambda x: x and x.startswith('mailto:')).get_text(strip=True) if soup.find('a', href=lambda x: x and x.startswith('mailto:')) else '',
                'website': soup.find('a', href=lambda x: x and x.startswith('http')).get_text(strip=True) if soup.find('a', href=lambda x: x and x.startswith('http')) else '',
                'social_links': ', '.join([a['href'] for a in soup.find_all('a', href=lambda x: x and ('facebook' in x or 'linkedin' in x))]),
                'posted_jobs': ', '.join([a['href'] for a in soup.find_all('a', {'class': 'title'})])
            }
            company_details_list.append(details)
        else:
            logging.warning(f"Failed to fetch company details from {url} (status code: {response.status_code})")

    return company_details_list

def save_company_details_to_db(company_details, db_path):
    logging.info("Connecting to the SQLite database to save company details 🗄️")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS company_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        about TEXT,
        logo TEXT,
        address TEXT,
        email TEXT,
        website TEXT,
        social_links TEXT,
        posted_jobs TEXT
    )
    ''')

    logging.info("Inserting company details into the database 🚀")
    for details in company_details:
        cursor.execute('''
        INSERT INTO company_details (name, about, logo, address, email, website, social_links, posted_jobs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (details['name'], details['about'], details['logo'], details['address'], details['email'], details['website'], details['social_links'], details['posted_jobs']))

    conn.commit()
    conn.close()
    logging.info("Company details have been saved to the database 🎉")

def main():
    logging.info("Script started 🏁")
    current_dir = os.getcwd()
    sitemap_file_path = os.path.join(current_dir, 'itjobs_pt/sitemap/main/sitemap_20240725.xml')  # Corrected path
    db_path = os.path.join(current_dir, 'itjobs_pt', 'urls_database.db')  # Save the database in the specified path

    urls = extract_urls_from_sitemap(sitemap_file_path)
    save_urls_to_db(urls, db_path)

    # Fetch the main URLs from the database
    urls_from_db = fetch_urls_from_db(db_path)

    # Extract all sitemaps from the URLs
    sitemaps = extract_all_sitemaps(urls_from_db)

    # Extract company details from the sitemap URLs
    company_details_list = extract_company_details(sitemaps)
    save_company_details_to_db(company_details_list, db_path)

    # Fetch and display the company details from the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM company_details')
    company_details_from_db = cursor.fetchall()
    conn.close()

    company_details_df = pd.DataFrame(company_details_from_db, columns=["ID", "Name", "About", "Logo", "Address", "Email", "Website", "Social Links", "Posted Jobs"])
    logging.info(f"Fetched {len(company_details_from_db)} company details from the database 🗃️")
    print(company_details_df)

    logging.info("Script finished successfully ✅")

if __name__ == "__main__":
    main()
