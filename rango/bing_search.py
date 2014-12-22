import json
import urllib, urllib2
from rango import keys


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

    username = 'trash.sebastien@gmail.com'

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, keys.BING_API_KEY)

    results = []

    try:
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        response = urllib2.urlopen(search_url).read()

        json_response = json.loads(response)

        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']})

    except urllib2.URLError, e:
        print("Error when querying the Bing API: ", e)

    return results


def main():
    query_search = input("Enter a query: ")

    query_result = run_query(query_search)

    i = 1
    for result in query_result:
        # print("rank : {0}, title: {1}, URL: {2}".format(i,
        #                                                result['title'],
        #                                                result['link']))
        print("rank : ", i)
        print("title : ", result['title'])
        print("URL : ", result['link'])

        i = i + 1

if __name__ == "__main__":
#    import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
    main()
