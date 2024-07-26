import sqlite3
import os
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_urls_to_download(db_path):
    logging.info("Fetching URLs to download from the database 📋")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, sitemap_url FROM all_sitemaps WHERE downloaded = 0')
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_url_as_downloaded(db_path, url_id):
    logging.info(f"Marking URL with ID {url_id} as downloaded ✅")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE all_sitemaps SET downloaded = 1 WHERE id = ?', (url_id,))
    conn.commit()
    conn.close()

def download_and_save_webpage(url, save_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        logging.info(f"Saved webpage from {url} to {save_path}")
    else:
        logging.warning(f"Failed to download webpage from {url} (status code: {response.status_code})")

def main():
    logging.info("Script started 🏁")
    db_path = '/Users/mcessid/Documents/Projects/Essid Solutions/Internal/Development/Github/jobbot/itjobs_pt/urls_database.db'
    html_save_dir = '/Users/mcessid/Documents/Projects/Essid Solutions/Internal/Development/Github/jobbot/itjobs_pt/html'
    
    # Ensure the save directory exists
    os.makedirs(html_save_dir, exist_ok=True)

    urls_to_download = fetch_urls_to_download(db_path)
    total_urls = len(urls_to_download)
    logging.info(f"Total URLs to download: {total_urls}")

    for count, (url_id, url) in enumerate(urls_to_download, start=1):
        logging.info(f"Downloading {count}/{total_urls}: {url}")
        filename = f"{url_id}.html"
        save_path = os.path.join(html_save_dir, filename)
        
        download_and_save_webpage(url, save_path)
        mark_url_as_downloaded(db_path, url_id)
        remaining = total_urls - count
        logging.info(f"Remaining URLs to download: {remaining}")

    logging.info("Script finished successfully ✅")

if __name__ == "__main__":
    main()
