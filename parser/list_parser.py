import bs4
import logging
from typing import List, TypedDict
import os
import pprint
import csv

logging.basicConfig(level=logging.DEBUG)


class GameItem(TypedDict):
    """
    a dictionary containing the ID of a game and its storepage url representing a game on the list
    """
    id: str
    url: str


Products = dict[str, List[GameItem]]


def extract_urls(folder: str, filename: str) -> Products:
    path = os.path.join(folder, filename)
    products = {"games": [], "bundles": [], "other": []}
    if not os.path.exists(path):
        logging.warning(f"Location {path} does not exist.")
        return products
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    soup = bs4.BeautifulSoup(data, "html.parser")
    links = soup.find_all("a")
    for link in links:
        if link.get("data-search-page"):
            if (product_id := link.get("data-ds-packageid")) is not None:
                category = products["other"]
            elif (product_id := link.get("data-ds-bundleid")) is not None:
                category = products["bundles"]
            elif (product_id := link.get("data-ds-appid")) is not None:
                category = products["games"]
            else:
                logging.warning(f"There was an issue with {link.get('href')}")
                logging.debug(link)
                continue
            category.append(
                    {"id": product_id, "url": link.get("href")}
                )
    # pprint.pprint(products, indent=4)
    # print(sum(len(v) for v in products.values()))
    return products


def extract_all_urls(folder: str) -> Products:
    products = {"games": [], "bundles": [], "other": []}
    for name in os.listdir(folder):
        temp_products = extract_urls(folder, name)
        for group, data in temp_products.items():
            for item in data:
                if item["id"] in (i["id"] for i in products[group]):
                    logging.info(f"Duplicate {item} in category {group}, skipping")
                else:
                    products[group].append(item)
    # pprint.pprint(products, indent=4)
    # print(sum(len(v) for v in products.values()))
    return products


def store_urls(products: Products, directory: str) -> None:
    fields = ["id", "url"]
    for category, data in products.items():
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"{category}.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)


if __name__ == '__main__':
    store_urls(extract_all_urls("../scraper/gamelist"), "urls")
    # pprint.pprint(extract_all_urls("../scraper/gamelist"), indent=4)
    # extract_urls("../scraper/gamelist", "1.html")
