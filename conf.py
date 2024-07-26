import os 



class extractSitemaps:
    def __init__(self, name):
        main_sitemaps = f"collected/{name}/sitemap/main"
        sub_sitemaps = f"collected/{name}/sitemap/sub"

        
        os.makedirs(sub_sitemaps, exist_ok=True)

        self.now = datetime.datetime.now()
        self.url = url
        self.sitemaps = []
        self.sitemapindex = []
        self.sitemap

    def itjobs(self):
        # create a folder to store the data
        name = "itjobs_pt"
        sitemap = self.url_sitemap
        robots = self.url_robots
        os.makedirs(os.path.join("collected",name), exist_ok=True)
        print(f"Processing {name} at {self.now}")
        # get the sitemap
        
        download_sitemap(sitemap)

itjobs()


### get the static sitemap
### get the sitemap index
### get the sitemap index sitemap
### download from linkedin 
### download from angel list