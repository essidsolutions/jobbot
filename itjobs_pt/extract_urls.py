import xml.etree.ElementTree as ET
import sqlite3
import os
import pandas as pd
import logging


sitename_utl = "https://www.itjobs.pt/sitemap.xml"
robots_url = "https://www.itjobs.pt/robots.txt"

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
    cursor.execute('SELECT * FROM urls')
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    logging.info("Script started 🏁")
    current_dir = os.getcwd()
    sitemap_file_path = os.path.join(current_dir, 'itjobs_pt/sitemap/main/sitemap_20240725.xml')  # Corrected path
    db_path = os.path.join(current_dir, 'itjobs_pt', 'urls_database.db')  # Save the database in the specified path

    urls = extract_urls_from_sitemap(sitemap_file_path)
    save_urls_to_db(urls, db_path)

    # Fetch and display the URLs from the database
    urls_from_db = fetch_urls_from_db(db_path)
    urls_df = pd.DataFrame(urls_from_db, columns=["ID", "URL"])
    logging.info(f"Fetched {len(urls_from_db)} URLs from the database 🗃️")
    print(urls_df)

    logging.info("Script finished successfully ✅")

if __name__ == "__main__":
    main()
