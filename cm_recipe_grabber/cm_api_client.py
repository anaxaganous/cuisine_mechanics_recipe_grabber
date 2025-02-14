import requests
from urllib.parse import urlparse, urljoin
import datetime
import isodate
import yaml
from django.utils.text import slugify


def TITLE_TO_SLUG(title):
    return slugify(title, allow_unicode=True)


class CM_Api_Client():

    API_PATH_BASE = "/api/v1"
    API_TOKEN_PAIR_PATH = API_PATH_BASE + "/token/pair"
    API_TOKEN_REFRESH_PATH = API_PATH_BASE + "/token/refresh"
    API_TOKEN_VERIFY_PATH = API_PATH_BASE + "/token/verify"

    API_TAGS = API_PATH_BASE + "/library/tags"
    API_RECIPE_URLS_ONLY = API_PATH_BASE + "/library/recipe-urls"
    API_MEASURED_INGREDIENTS = API_PATH_BASE + "/library/measured_ingredients"
    API_SOURCE_DETAIL = API_PATH_BASE + "/library/sources/{}"
    API_SOURCE_RECIPE_URLS = API_SOURCE_DETAIL + "/recipe-urls"
    API_AUTHORS = API_PATH_BASE + "/library/authors"
    API_LANGUAGES = API_PATH_BASE + "/library/languages"
    API_RECIPES = API_PATH_BASE + "/library/recipes"


    def __init__(self, url_base, username, password):
        self.url_base = url_base
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()
        self.last_status_code = None
        self.validation_requested = False
        self.ingredient_cache = {}
        self.recipe_tags_cache = {}
        self.language_cache = {}
        self.author_cache = {}

    def cycle_token(self):
        if self.refresh_token:
            url = urljoin(self.url_base, self.API_TOKEN_REFRESH_PATH)
            msg = {
                "refresh": self.refresh_token,
            }
            response = self.session.post(url, json=msg, timeout=5)
            if response.status_code == 200:
                response_json = response.json()
                self.access_token = response_json['access']
                self.refresh_token = response_json['refresh']
                self.update_header()
                return True

        url = urljoin(self.url_base, self.API_TOKEN_PAIR_PATH)
        msg = {
            "username": self.username,
            "password": self.password,
        }
        response = self.session.post(url, json=msg, timeout=5)
        if response.status_code != 200:
            return False

        response_json = response.json()
        self.access_token = response_json['access']
        self.refresh_token = response_json['refresh']
        self.update_header()
        return True
    
    def update_header(self):
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })

    def do_get(self, url, params = {}):
        response = self.session.get(url, params=params, timeout=5)
        if response.status_code != 200:
            if response.status_code == 401:
                self.cycle_token()
                response = self.session.get(url, params=params, timeout=5)
            else:
                raise ConnectionError(f"GET to {url} received response {response.status_code}: {response.content}")
        return response

    def do_put(self, url, msg):
        response = self.session.put(url, json=msg, timeout=5)
        if response.status_code != 200:
            if response.status_code == 401:
                self.cycle_token()
                response = self.session.put(url, json=msg, timeout=5)
            else:
                raise ConnectionError(f"PUT to {url} received response {response.status_code}: {response.content}")
        return response
    
    def do_post(self, url, msg):
        response = self.session.post(url, json=msg, timeout=5)
        if response.status_code != 200:
            if response.status_code == 401:
                self.cycle_token()
                response = self.session.post(url, json=msg, timeout=5)
            else:
                raise ConnectionError(f"POST to {url} received response {response.status_code}: {response.content}")
        return response


    def collect_all_results(self, initial_url, initial_params={}):
        url = initial_url
        print(f"URL {url}")
        results = []
        max_offset = 999999999999999999
        params = {
            "offset": 0,
            "limit": 200,
        }
        params.update(initial_params)
        while params['offset'] < max_offset:
            response = self.do_get(url, params)
            print(f"Response: {repr(response)}")
            js = response.json()
            max_offset = js['count']
            results.extend(js['items'])
            params['offset'] += params['limit']
        return results

    def get_source_detail(self, source_id):
        url = urljoin(self.url_base, self.API_SOURCE_DETAIL.format(source_id))
        response = self.do_get(url)
        js = response.json()
        return js
    
    def get_source_recipe_urls(self, source_id):
        url = urljoin(self.url_base, self.API_SOURCE_RECIPE_URLS.format(source_id))
        return [x['url'] for x in self.collect_all_results(url)]


    def get_domain_urls(self, base_url):
        params = {
            "url__istartswith": base_url,
        }
        url = urljoin(self.url_base, self.API_RECIPE_URLS_ONLY)
        return (x['url'] for x in self.collect_all_results(url, params))

    def cache_recipe_tags(self):
        params = {
            "recipe_usable": True,
        }
        url = urljoin(self.url_base, self.API_TAGS)
        for x in self.collect_all_results(url, params):
            self.recipe_tags_cache[x['name'].strip().lower()] = x['id']
            for tag in x['name'].split("/"):
                self.recipe_tags_cache[tag.strip().lower()] = x['id']


    def get_ingredient_by_name(self, ingredient):
        if ingredient in self.ingredient_cache:
            return self.ingredient_cache[ingredient]
        
        msg = {
            "measured_ingredient_name": ingredient
        }
        url = urljoin(self.url_base, self.API_MEASURED_INGREDIENTS)
        response = self.do_put(url, msg)
        print(f"Received response: {response.content}")
        js = response.json()
        print(f"Response: {js}")
        if js.get('validation_requested'):
            self.validation_requested = True

        self.ingredient_cache[ingredient] = {"measured_ingredient_id": js['id'], "optional": js['optional']}
        return self.ingredient_cache[ingredient]
    
    def get_author(self, name):
        slug = TITLE_TO_SLUG(name)
        if slug in self.author_cache:
            return self.author_cache[slug]
        params = {
            "name": name,
        }
        url = urljoin(self.url_base, self.API_AUTHORS)
        response = self.do_put(url, params)
        print(f"Received response: {response.content}")
        js = response.json()
        print(f"Response: {js}")
        self.author_cache[slug] = js['id']
        return self.author_cache[slug]

    def get_language(self, name):
        slug = TITLE_TO_SLUG(name)
        if slug in self.language_cache:
            return self.language_cache[slug]
        params = {
            "name_slug__iexact": TITLE_TO_SLUG(name),
        }
        url = urljoin(self.url_base, self.API_LANGUAGES)
        response = self.do_get(url, params)
        print(f"Received response: {response.content}")
        js = response.json()
        print(f"Response: {js}")
        if js['count'] == 1:
            self.language_cache[slug] = js['items'][0]['id']
            return self.language_cache[slug]
        return None

    def select_recipe_tags(self, possible_tags):
        found_tags = set()
        for tag in possible_tags:
            tl = tag.lower()
            if tl in self.recipe_tags_cache:
                found_tags.add(self.recipe_tags_cache[tl])

        return list(found_tags)

    def store_recipe(self, scrape_results, source_id, url):
        self.validation_requested = False

        def get_min_max_servings(serv_str):
            if serv_str is None:
                return None, None
            serv_str = serv_str.replace("-", " ")
            nums = [x for x in serv_str.split() if x.isnumeric()]
            if not nums:
                return None, None
            if len(nums) == 1:
                servs = int(nums[0])
                return servs, servs
            if len(nums) == 2:
                servs_1 = int(nums[0])
                servs_2 = int(nums[1])
                if servs_1 < servs_2:
                    return servs_1, servs_2
            return None, None
                

        def split_authors(author_str):
            found_authors = []
            if not author_str:
                return found_authors
            authors = author_str.split(";")
            for author in authors:
                if found := self.get_author(author):
                    found_authors.append(found)
                else:
                    return []

            return found_authors
        
        def get_iso_minutes(dur: int):
            return isodate.duration_isoformat(isodate.duration.Duration(minutes=dur))


        recipe_js = scrape_results.to_json()
        parser_notes = {}

        authors = recipe_js.get("author", "")
        found_authors = split_authors(authors)
        if authors and not found_authors:
            parser_notes["author"] = authors
            authors = []

        prep_time = recipe_js.get("prep_time")
        if prep_time:
            prep_time = get_iso_minutes(prep_time)
        
        cook_time = recipe_js.get("cook_time")
        if cook_time:
            cook_time = get_iso_minutes(cook_time)
        
        total_time = recipe_js.get("total_time")
        if total_time:
            total_time = get_iso_minutes(total_time)
        # language = recipe_js.get("language")
        # language = self.get_language("English")
        serv_min, serv_max = get_min_max_servings(recipe_js.get("yields"))
        ingredients = [self.get_ingredient_by_name(x) for x in recipe_js.get("ingredients", [])]
        # reviews = recipe_js.get("reviews")
        # Collect category / tags / whatever into tags list, push through select recipe tags
        all_tags = recipe_js.get('keywords', [])
        if cat := recipe_js.get('category'):
            all_tags.append(cat)
        if method := recipe_js.get('cooking_method'):
            all_tags.append(method)
        print(f"Checking tags: {all_tags}")
        tag_ids = self.select_recipe_tags(all_tags)
        print(f"Got tag IDs: {tag_ids}")

        if pub_date := scrape_results.schema.data.get('datePublished'):
            publication_date = datetime.datetime.fromisoformat(pub_date).date().isoformat()
        else:
            publication_date = None

        msg = {
            "source_id": source_id,
            "author_ids": found_authors,
            "recipe_ingredients": ingredients,
            "accompaniment_ids": [],
            "tag_ids": tag_ids,
            "request_verification": False,
            "name": recipe_js.get("title"),
            "min_servings": serv_min,
            "max_servings": serv_max,
            "page_number": 1,
            "entry_on_page": 1,
            "cook_time": cook_time,
            "prep_time": prep_time,
            "total_time": total_time,
            "url": url,
            "publication_date": publication_date,
            "parser_notes": yaml.dump(parser_notes) if parser_notes else ""
        }
        # return msg
        url = urljoin(self.url_base, self.API_RECIPES)
        response = self.do_post(url, msg)
        js = response.json()
        if js.get('validation_requested'):
            self.validation_requested = True

        return js['id']


