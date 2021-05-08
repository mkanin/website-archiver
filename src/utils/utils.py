import os
import uuid
from urllib.parse import urlparse


def read_urls(filename):
    filename = filename.strip()
    with open(filename, 'r') as fp:
        urls = []
        for url in fp:
            print('Reading the url {url} from the input file "{input_file}"'
                  .format(url=url, input_file=filename))
            url = url.strip()
            urls.append(url)
        return urls


def create_initial_dir(start_dir, start_time_str, url):
    parsed = urlparse(url)
    domain = parsed.netloc
    dir_full_path = os.path.join(start_dir, 'sites', start_time_str, domain)
    if not os.path.exists(dir_full_path):
        os.makedirs(dir_full_path)
    return dir_full_path


def write_links_file(dir_full_path, start_url, filename, links):
    parsed = urlparse(start_url)
    path = parsed.path
    head, tail = os.path.split(path)
    if head[0] == '/':
        head = head[1:]
    dir_full_path = os.path.join(dir_full_path, head)
    if not os.path.exists(dir_full_path):
        os.makedirs(dir_full_path)
    links_str = '\n'.join(links)
    links_str += '\n'
    id = uuid.uuid1()
    rel_filename = '{id_hex}_{filename}'.format(
        id_hex=id.hex, filename=filename
    )
    filename = os.path.join(dir_full_path, rel_filename)
    open(filename, 'w').write(links_str)


def write_archive_urls(dir_full_path, start_url, filename, archive_urls):
    parsed = urlparse(start_url)
    path = parsed.path
    head, tail = os.path.split(path)
    if head[0] == '/':
        head = head[1:]
    dir_full_path = os.path.join(dir_full_path, head)
    archive_urls_str = ""
    for url, archive_url in archive_urls.items():
        archive_urls_str += '{} ; {}\n'.format(url, archive_url)
    id = uuid.uuid1()
    rel_filename = '{id_hex}_{filename}'.format(
        id_hex=id.hex, filename=filename
    )
    filename = os.path.join(dir_full_path, rel_filename)
    open(filename, 'w').write(archive_urls_str)


def add_forward_slash_to_the_end_of_url(url):
    if url[-1] != '/':
        url += '/'
    return url


def create_full_url_with_protocol(url):
    if url[0:4] != 'http':
        url = 'http://' + url
    return url
