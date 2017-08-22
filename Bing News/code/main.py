import time
import codecs
from py_ms_cognitive import PyMsCognitiveNewsSearch

MAX_TO_CRAWL = 1000
SEARCH_LIMIT = 100


def save_query_results(entry, collection):
    """Save the entry if its URL is not a duplicate.

    Returns True if a new document has been inserted into collection,
    False otherwise.
    """
    
    url = entry.url
    hash_value = hash(url)
    # Is this URL in the hash table?
    duplicate = True if hash_value in collection else False
    if duplicate:
        return False
    else:
        collection[hash_value] = url

    return True


def crawl_bing(queries):
    collection = {}
    start_time = time.time()
    total_num_api_calls = 0
    total_saved_urls = 0
    total_num_crawled = 0
    BING_KEY = '821928f157b54c20aaf50ec76360b7d2'
    for query in queries:
        num_api_calls = 0
        num_crawled = 0
        num_saved_results = 0
        num_api_calls_per_query = 0
        custom_params = "?freshness"
        custom_params += "&mkt=en-us"
        #custom_params = "?mkt=en-us"
        bing = PyMsCognitiveNewsSearch(
            BING_KEY,
            query.encode("utf-8"),
            custom_params=custom_params
        )

        while num_crawled < MAX_TO_CRAWL:
            results = bing.search(limit=SEARCH_LIMIT, format="json")
            num_crawled += len(results)
            num_api_calls += 1
            num_api_calls_per_query += 1
            num_new_results = 0

            any_result_added = False
            for result in results:
                result_added = save_query_results(result, collection)
                if result_added:
                    num_saved_results += 1
                    num_new_results += 1

                any_result_added = any_result_added or result_added

            print num_new_results
            # Nothing new found so there is no reason to continue.
            if not any_result_added:
                break

            # If we hit less than the limit then calling again will return
            # the same results. Thus, simply stop.
            #if len(results) < SEARCH_LIMIT:
            #   break
        
        print "API calls for query ", query, " is ", num_api_calls, " times."
        print "Crawled urls for this query is:", num_crawled
        print "Saved urls for this query is:", num_saved_results
        
             
        total_num_api_calls += num_api_calls
        total_saved_urls += num_saved_results
        total_num_crawled += num_crawled
        
    print "Total number of API calls:", total_num_api_calls
    print "Total number of saved urls:", total_saved_urls
    print "Total number of crawled urls:", total_num_crawled
            
    output = codecs.open("crawl_bing.txt", 'w', encoding = "utf8")
    for url in collection.values():
        output.write(url)
        output.write('\n')
        
    output.close()


def main():
    queries = ['Hillary Clinton','Hillary Rodham Clinton','Secretary Clinton','Sec. Clinton','Secretary of State Hillary Clinton','Mrs. Clinton','Mrs. Bill Clinton']
    crawl_bing(queries)


if __name__ == "__main__":
    main()    
