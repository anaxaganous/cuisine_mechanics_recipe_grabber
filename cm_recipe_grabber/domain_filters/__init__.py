from urllib.parse import urlparse


domain_url_filters = {
    "www.epicurious.com": lambda x: urlparse(x).path.startswith("/recipes/"),

}

def get_domain_filter_func(url):
    return domain_url_filters.get(urlparse(url).netloc, None)