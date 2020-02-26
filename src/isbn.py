
import re
import requests

def find_isbn(data):
    regex_pattern = r'(ISBN[-:]*(1[03])*[ ]*(: ){0,1})*(([0-9Xx][- \'"]*){13}|([0-9Xx][- \'"]*){10})'
    # regex_pattern = r'/((978[\--– ])?[0-9][0-9\--– ]{10}[\--– ][0-9xX])|((978)?[0-9]{9}[0-9Xx])/'
    x = re.search(regex_pattern, data)
    if x:
        data = re.sub('[ISBN^(: )]+', '', x.group())
        line = re.sub('[!@#$\'\"-+*()[]|\/&_=\{\}:;<>/?]', '', data)
        return line
    else:
        None

def check_isbn(isbn):
    # Using abebooks to do a search on the isbn
    # This only works when there is internet
    url = 'https://www.abebooks.com/servlet/SearchResults?isbn=' + isbn
    resp = requests.get(url)
    found_isbn = False
    if url == resp.url:
        found_isbn = True
    return found_isbn, url