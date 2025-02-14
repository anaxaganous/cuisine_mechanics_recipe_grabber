import requests
from usp.tree import sitemap_tree_for_homepage
from urllib.parse import urlparse, urljoin
import sys
import argparse
import recipe_scrapers
import time
import sqlite3

from cm_recipe_grabber.domain_filters import get_domain_filter_func
from cm_recipe_grabber.cm_api_client import CM_Api_Client

def get_serving_min_max(recipe_js):
    y = recipe_js.get("yields")
    if not y:
        return None, None 
    



    



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cm-host", type=str, default="https://www.cuisinemechanics.com")
    parser.add_argument("-u", "--username", type=str, required=True)
    parser.add_argument("-p", "--password", type=str, required=True)
    parser.add_argument("source_id", type=str)
    args = parser.parse_args()
    
    api_client = CM_Api_Client(url_base=args.cm_host, username=args.username, password=args.password)
    source_detail = api_client.get_source_detail(args.source_id)
    site_url = source_detail["url"]

    domain_filter_func = get_domain_filter_func(site_url)
    if not domain_filter_func:
        sys.exit(f"No filter function found for {site_url}")

    # Pull all known URLS for domain from CM
    known_urls = api_client.get_source_recipe_urls(args.source_id)
    api_client.cache_recipe_tags()
    # Get the sitemap for a domain

    max_count = 5
    session = requests.Session()
    db_con = sqlite3.connect("recipe_grabber.db")
    cursor = db_con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS webpages(url VARCHAR NOT NULL UNIQUE, visited INTEGER NOT NULL DEFAULT 0)")
    db_con.commit()

    if not cursor.execute("SELECT url FROM webpages WHERE visited = 0").fetchone():
        tree = sitemap_tree_for_homepage(site_url)
        for page in tree.all_pages():
            # Filter out URLS we already know about
            # Filter the URLS to remove known non-recipe pages if possible
            if not domain_filter_func(page.url):
                continue
            cursor.execute("INSERT INTO webpages(url) VALUES(?) ON CONFLICT(url) DO NOTHING ", (page.url, ))
        db_con.commit()
    

    for rowid, url in cursor.execute("SELECT rowid, url FROM webpages WHERE visited = 0").fetchall():
        print(f"Getting {url}")
        response = session.get(url, params={}, timeout=5)
        if response.status_code == 200:
            scrape_results = recipe_scrapers.scrape_html(response.content, org_url=url, supported_only=False)
            api_client.store_recipe(scrape_results, args.source_id, url)
            cursor.execute("UPDATE webpages SET visited = 1 WHERE rowid = ?", (rowid,))
            db_con.commit()
            if api_client.validation_requested:
                print("VALIDATION REQUESTED")
            input("Press Enter to continue...")
            # time.sleep(10)
        max_count = max_count - 1
        if response.status_code != 200 or not max_count:
            break


    # Pull each remaining URL
    # rf = RecipeFetcher()
    # url = "https://www.epicurious.com/recipes/food/views/ba-syn-paneer-and-green-bean-stir-fry"
    # print("Getting URL")
    # response = session.get(url, params={}, timeout=5)
    # print("Url fetched.")


    # Feed results into recipe_scraper
    # If it's a recipe, upload to CM
    # Otherwise, update CM that's it's a non-recipe

