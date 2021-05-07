import concurrent.futures
import os
import time
import urllib.robotparser
from urllib.parse import urljoin, urlparse

import requests as requests
from bs4 import BeautifulSoup


class Crawler:

    def __init__(self, archiver, headers, dir_full_path, original_url):
        self.archiver = archiver
        self.headers = headers
        self.dir_full_path = dir_full_path
        self.original_url = original_url
        self.links_short = []
        self.explored_urls = set()
        self.archive_urls = {}
        self.links_failed = []
        self.rp = urllib.robotparser.RobotFileParser()

    def save_robots(self, robots_url):
        parsed = urlparse(robots_url)
        path = parsed.path
        head, tail = os.path.split(path)
        if head and head[0] == '/':
            head = head[1:]
        dir_full_path = os.path.join(self.dir_full_path, head)
        filename = os.path.join(dir_full_path, tail)
        try:
            response = requests.get(robots_url, headers=self.headers)
        except Exception:
            return -1
        self.explored_urls.add(robots_url)
        if response.status_code == 200:
            try:
                archive_url = self.archiver.archive(robots_url)
            except Exception:
                print("Something went wrong with the url {}".format(
                    robots_url
                ))
            else:
                self.archive_urls[robots_url] = archive_url
                if not os.path.exists(dir_full_path):
                    os.makedirs(dir_full_path)
                if not os.path.exists(filename):
                    open(filename, 'wb').write(response.content)
        else:
            return -1
        return 0

    def create_url_to_robots_file(self, start_url):
        parsed = urlparse(start_url)
        urn = '{scheme}://{netloc}/'.format(
            scheme=parsed.scheme, netloc=parsed.netloc
        )
        robots_url = urljoin(urn, 'robots.txt')
        return robots_url

    def set_robots(self, robots_url):
        self.rp.set_url(robots_url)
        self.rp.read()

    def can_fetch(self, current_url):
        return self.rp.can_fetch("*", current_url)

    def save_to_archive(self, current_url):
        try:
            archive_url = self.archiver.archive(current_url)
        except Exception:
            self.links_failed.append(current_url)
            print("Something went wrong with the url {}".format(current_url))
        else:
            message = "The page {} was saved to the Internet Archive with " \
                      "url {}".format(current_url, archive_url)
            print(message)
        self.archive_urls[current_url] = archive_url if archive_url else ""

    def crawl(self, start_url, additional_urls=[]):
        robots_url = self.create_url_to_robots_file(start_url)
        self.set_robots(robots_url)
        robots_res = self.save_robots(robots_url)
        s = [start_url]
        for additional_url in additional_urls:
            if (
                    additional_url.find(self.original_url) != -1 and
                    additional_url not in s
            ):
                s.append(additional_url)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            while len(s) > 0:
                time.sleep(1)
                current_url = s.pop(0)
                if current_url not in self.explored_urls:
                    self.explored_urls.add(current_url)
                    can_fetch_flag = True
                    if robots_res >= 0:
                        can_fetch_flag = self.can_fetch(current_url)
                    if can_fetch_flag:
                        self.links_short if current_url in self.links_short \
                            else self.links_short.append(current_url)

                        print("Exploring URL {}".format(current_url))
                        if current_url and current_url[0:4] != 'http':
                            continue
                        try:
                            response = requests.get(
                                current_url, headers=self.headers
                            )
                        except Exception:
                            continue
                        if response.status_code not in [200, 201, 301, 302]:
                            continue
                        executor.submit(self.save_to_archive, current_url)
                        content_type = response.headers.get('Content-Type', '')
                        if content_type.find('text/html') == -1:
                            continue
                        soup = BeautifulSoup(response.content, 'html.parser')
                        anchors = soup('a')
                        for anchor in anchors:
                            if 'href' in dict(anchor.attrs):
                                link = anchor['href']
                                local_url = urljoin(current_url, link)
                                local_url = local_url.split('#')[0]
                                if (
                                        local_url.find(
                                            self.original_url
                                        ) != -1 and
                                        local_url not in self.explored_urls
                                ):
                                    s.append(local_url)
