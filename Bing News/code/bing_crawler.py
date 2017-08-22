import time

from celery.utils.log import get_task_logger
from py_ms_cognitive import PyMsCognitiveNewsSearch

from helpers.datetime import utc_timestamp
from helpers.extract_url import process_url
from helpers.mongo import MongoCollectionWrapper, find_duplicate_and_mark
from proj.settings import (
    API_SOURCE, BING_API, BING_KEY, CRAWL_TIMESTAMP,
    DOCUMENT_IS_PROCESSED_CLUSTERING, DOCUMENT_IS_PROCESSED_FIELD,
    HAS_BEEN_DOWNLOADED, IS_NEEDS_TRANSLATION, NUM_DOWNLOAD_ATTEMPTS,
    ORIGINAL_URL, TIMESTAMP, TITLE, URL, UUID,
)

logger = get_task_logger(__name__)
MAX_TO_CRAWL = 1000
SEARCH_LIMIT = 100


def save_query_results(entry, collection):
    """Save the entry if its URL is valid and not a duplicate.

    Returns True if a new document has been inserted into collection,
    False otherwise.
    """
    short_url = entry.url

    # Short URL is extracted (it's wrapped in a bing url and its GET params)
    # and cleaned (there still can be extra params that disallow duplicate
    # recognition).
    url, uuid = process_url(short_url)
    if not url:
        return False

    # Is this URL in the DB already?
    duplicate = find_duplicate_and_mark(
        collection=collection,
        uuid=uuid,
        original_url=short_url
    )
    if duplicate:
        return False

    try:
        obj = {
            HAS_BEEN_DOWNLOADED: False,
            CRAWL_TIMESTAMP: utc_timestamp(),
            TIMESTAMP: utc_timestamp(entry.date_published),
            TITLE: entry.name,
            UUID: uuid,
            URL: url,
            ORIGINAL_URL: short_url,
            NUM_DOWNLOAD_ATTEMPTS: 0,
            DOCUMENT_IS_PROCESSED_FIELD: False,
            DOCUMENT_IS_PROCESSED_CLUSTERING: False,
            API_SOURCE: BING_API,
            IS_NEEDS_TRANSLATION: False,
        }
        collection.insert_one(obj)
    except Exception:
        logger.exception("Failed to process results")
        return False

    return True


def crawl_bing(queries, collection_name):
    start_time = time.time()
    num_api_calls = 0
    total_saved_urls = 0

    collection = MongoCollectionWrapper(collection_name)
    for query, market in queries:
        num_crawled = 0
        num_new_results = 0
        num_api_calls_per_query = 0
        custom_params = "?freshness=Week"
        if market:
            custom_params += "&mkt=" + market
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

            any_result_added = False
            for result in results:
                result_added = save_query_results(result, collection)
                if result_added:
                    num_new_results += 1

                any_result_added = any_result_added or result_added

            # Nothing new found so there is no reason to continue.
            if not any_result_added:
                break

            # If we hit less than the limit then calling again will return
            # the same results. Thus, simply stop.
            if len(results) < SEARCH_LIMIT:
                break

        logger.info(
            u"Crawled %d urls (%d new, %d api calls) for \"%s\" (Market: %s)",
            num_crawled,
            num_new_results,
            num_api_calls_per_query,
            query,
            market
        )
        total_saved_urls += num_new_results

    logger.info(
        "Made %d api calls and saved %d urls.",
        num_api_calls,
        total_saved_urls
    )
    logger.info("Time elapsed: %d seconds.", (int(time.time() - start_time)))
    logger.info("Done")
    
