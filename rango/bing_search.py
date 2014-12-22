import json
import urllib, urllib2

# Bing API Key
BING_API_KEY = G0auJySskzKyjbhtLkRwH0VgxBoeEolpsZmE67fFd0k

def run_query(search_terms):
    # Specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    source = 'Web'

    results_per_page = 10
    offset = 0

    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    search_url ="{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
        root_url,
        source,
        results_per_page,
        offset,
        query)

    username = ''

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None,search_url, username, BING_API_KEY)

    results = []

    try:
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        response = urllib2.urlopen(search_url).read()
