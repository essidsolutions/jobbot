import xml.etree.ElementTree as ET
import sqlite3
import os
import logging
import requests

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

def save_sitemaps_to_db(sitemaps, db_path):
    logging.info("Connecting to the SQLite database to save sitemaps 🗄️")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS all_sitemaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sitemap_url TEXT UNIQUE, 
        downloaded BOOLEAN DEFAULT 0
    )
    ''')

    logging.info("Inserting sitemaps into the database 🚀")
    for sitemap in sitemaps:
        try:
            cursor.execute('INSERT INTO all_sitemaps (sitemap_url) VALUES (?)', (sitemap,))
        except sqlite3.IntegrityError:
            logging.warning(f"Duplicate sitemap found and ignored: {sitemap} ⚠️")
            # Ignore duplicate sitemaps
            pass

    conn.commit()
    conn.close()
    logging.info("Sitemaps have been saved to the database 🎉")

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
    save_sitemaps_to_db(sitemaps, db_path)

    # Fetch and display the sitemaps from the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM all_sitemaps')
    sitemaps_from_db = cursor.fetchall()
    conn.close()

    import pandas as pd
    sitemaps_df = pd.DataFrame(sitemaps_from_db, columns=["ID", "Sitemap URL"])
    logging.info(f"Fetched {len(sitemaps_from_db)} sitemaps from the database 🗃️")
    print(sitemaps_df)

    logging.info("Script finished successfully ✅")

if __name__ == "__main__":
    main()
