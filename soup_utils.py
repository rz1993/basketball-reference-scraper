import re
import requests
from bs4 import BeautifulSoup, Comment

def soup_from_url(url, suppressOutput=True):
    """
    This function grabs the url and returns and returns the BeautifulSoup object
    """
    if not suppressOutput:
        print(url)

    try:
        r = requests.get(url)
    except:
        return None
    return BeautifulSoup(r.text, "html5lib")

def find_comment(soup):
    return soup.find(text=lambda text: isinstance(text, Comment))

def find_all_comments(soup):
    return soup.findAll(text=lambda text: isinstance(text, Comment))

def parse_dollar_amounts(s):
    return s.replace(',', '').replace('$', '')

def text_pattern(pattern):
    """ Second tier function for returning a matching function
    based on the regular expression
    """

    pattern = re.compile(pattern)
    def parser(soup, first=True):
        # Navigable string is returned when we pass text kwarg
        nav_string = soup.findAll(text=pattern)
        if not nav_string:
            return None
        # Slightly hacky, but assume we just want first tag
        nav_string = nav_string[0]
        if first:
            return re.findall(pattern, nav_string)[0].strip()
        return map(lambda x: x.strip(), re.findall(pattern, nav_string))

    return parser
