import requests
import os
from typing import Optional, Union, TypedDict, List
import time
import logging
import csv
import pprint


class GameItem(TypedDict):
    """
    a dictionary containing the ID of a game and its storepage url representing a game on the list
    """
    id: str
    url: str


# Logging config: saves warnings and above into a file, and prints debug and above to stdout

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")

fh = logging.FileHandler("warnings.log", mode="w", encoding="utf-8")
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

# logging.basicConfig(level=logging.DEBUG)

gamelist_url = "https://store.steampowered.com/search/?filter=topsellers&page={}"
# Steam requests an age check for mature games, which can be avoided by setting an appropriate cookie
age_check_cookies = {"birthtime": "283993201", "mature_content": "1"}


def download_page(url: str, cookies: Optional[dict[str, str]] = None) -> Optional[str]:
    if cookies is None:
        cookies = {}
    try:
        r = requests.get(url, cookies=cookies)
    except requests.exceptions.ConnectionError as e:
        log.warning(f"Could not connect to {url}: {e}")
        return None
    if r.status_code == requests.codes.ok:
        return r.text
    else:
        log.warning(f"Error downloading {url}: {r.status_code}")
        return None


def save(data: str, directory: str, filename: str) -> None:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
    return None


def fetch_page(url: str, directory: str, filename: str, force: bool = False, cookies: Optional[dict[str, str]] = None) -> None:
    path = os.path.join(directory, filename)
    if os.path.exists(path) and not force:
        log.info(f"Skipping {url}, already exists.")
        return None
    if force:
        log.info(f"Redownloading {url}")
    else:
        log.debug(f"Downloading {url}")
    page_data = download_page(url, cookies)
    if page_data is None:
        log.warning(f"Skipping {url}, an error occurred")
        return None
    return save(page_data, directory, filename)


def fetch_gamelist(num: int, force: bool = False, delay: Union[int, float] = 1) -> None:
    for num in range(1, num+1):
        log.debug(f"Attempting Gamelist {num}")
        fetch_page(gamelist_url.format(num), "gamelist", f"{num}.html", force)
        time.sleep(delay)


def load_urls(directory: str, filename: str) -> Optional[List[GameItem]]:
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        log.warning(f"{path} does not exist.")
        return None
    with open(path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def fetch_gamepages(urls: List[GameItem], force: bool = False, delay: Union[int, float] = 1) -> None:
    for url in urls:
        log.debug(f"Attempting game page for {url['id']}: {url['url']}")
        fetch_page(url["url"], "gamepages", f"{url['id']}.html", force, age_check_cookies)
        time.sleep(delay)


if __name__ == '__main__':
    # fetch_gamelist(400)
    fetch_gamepages(load_urls("../parser/urls", "games.csv"))
