import os
import sys
from datetime import datetime

from crawler.crawler import Crawler
from src.archiver.archiver import Archiver
from utils import utils


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/50.0.2661.102 Safari/537.36'
headers = {'User-Agent': user_agent}


def main():
    if len(sys.argv) < 2:
        return
    start_url = sys.argv[-1]
    original_url = utils.add_forward_slash_to_the_end_of_url(start_url)
    start_url = utils.create_full_url_with_protocol(original_url)
    now = datetime.now()
    start_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    start_dir = os.path.dirname(os.path.realpath(__file__))
    start_dir = os.path.join(start_dir, '..')
    dir_full_path = utils.create_initial_dir(
        start_dir, start_time_str, start_url
    )
    archiver = Archiver(user_agent)
    crawler = Crawler(archiver, headers, dir_full_path, original_url)
    crawler.crawl(start_url)
    utils.write_links_file(
        dir_full_path, start_url, "links_short.txt", crawler.links_short
    )
    utils.write_links_file(
        dir_full_path, start_url, "links_failed.txt", crawler.links_failed
    )
    utils.write_archive_urls(
        dir_full_path, start_url, "archive_urls.txt", crawler.archive_urls
    )


if __name__ == '__main__':
    main()
