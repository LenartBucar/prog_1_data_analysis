import bs4
import logging
from typing import List, TypedDict, Optional, Union, Callable
import os
import pprint
import json

logging.basicConfig(level=logging.DEBUG)


def get_soup(folder: str, filename: str) -> Optional[bs4.BeautifulSoup]:
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        logging.warning(f"Location {path} does not exist.")
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    return bs4.BeautifulSoup(data, "html.parser")


def get_field(soup: Union[bs4.BeautifulSoup, bs4.Tag], fieldname: str) -> str:
    if (field := soup.select_one(fieldname)) is not None:
        return field.text.strip()
    return ""


def extract_data(soup: bs4.BeautifulSoup) -> ...:
    soup = clean_tags(soup, ["script", "meta", "head"])
    # soup = clean_selector(soup, ["#global_header", ".responsive_page_menu_ctn", ".responsive_header"])
    # main = soup.select_one(".page_content_ctn")
    title_area = soup.select_one(".page_title_area")
    block = soup.select_one(".block")
    meta = soup.select_one(".game_meta_data")
    desc = soup.select_one(".game_description_column")
    review = soup.select_one(".review_ctn")

    data = {**extract_head(title_area),
            **extract_block(block),
            **extract_meta(meta),
            **extract_desc(desc)}

    return data


def extract_head(tag: bs4.Tag) -> dict:
    return {"title": get_field(tag, "#appHubAppName")}


def extract_block(tag: bs4.Tag) -> dict:
    # Right column data
    data = {}
    right = tag.select_one(".rightcol")
    if right is None:
        return {"description": "",
                "reviews_recemt": {},
                "reviews_all": {},
                "date": "",
                "developer": "",
                "publisher": "",
                "tags": []}

    # DESCRIPTION
    data["description"] = get_field(right, ".game_description_snippet")

    # REVIEWS_AGGREGATED
    # TODO: Fix only one scope of reviews being present
    reviews = right.select_one("#userReviews")
    for scope, review in zip(("reviews_recent", "reviews_all"), reviews.find_all(recursive=False)):
        r = review.select_one(".game_review_summary")
        if r is None:  # No reviews
            data["reviews_recent"] = {}
            data["reviews_all"] = {}
            break
        out = {"text": review.get("data-tooltip-html"),
               "mood": r.string
               }
        data[scope] = out

    # AUTHORS
    data["date"] = get_field(right, ".date")
    for t, name in zip(("developer", "publisher"), right.select(".dev_row")):
        data[t] = name.a.string

    # TAGS
    tags_all = right.select_one(".popular_tags")
    if tags_all is not None:
        data["tags"] = [t.string.strip() for t in tags_all.find_all("a")]
    else:
        data["tags"] = []

    return data


def extract_meta(tag: bs4.Tag) -> dict:
    metadata = {"categories": [], "languages": {}}

    # CATEGORIES
    categories = tag.select_one("#category_block")
    if categories is not None:
        for category in categories.find_all(class_="game_area_details_specs", recursive=False):
            metadata["categories"].append(category.select_one(".name").text.strip())

    # LANGUAGES
    languages = tag.select_one("#languageTable")
    if languages is not None:
        for row in languages.find_all("tr")[1:]:  # skipping the header
            langs = [td for td in row.find_all(recursive=False)]
            metadata["languages"][langs[0].string.strip()] = [bool(check.span) for check in
                                                              langs[1:]]  # True if it supports the feature, False if not.
            # Features are: [interface, full audio, subtitles]

    # AGE RATING
    rating = tag.select_one(".shared_game_rating")
    if rating is not None:
        image = rating.find("img").get("src")
        descriptors = get_field(rating, ".descriptorText").split("\n\n")
        agency = get_field(rating, ".game_rating_agency")
        metadata["rating"] = {
            "image_url": image,
            "descriptors": descriptors,
            "agency": agency,
        }
    else:
        metadata["rating"] = {
            "image_url": "",
            "descriptors": [""],
            "agency": "",
        }

    # METASCORE
    metascore = tag.select_one("#game_area_metascore")
    if metascore is not None:
        metadata["metascore"] = get_field(metascore, ".score")
    else:
        metadata["metascore"] = "N/A"

    awards = tag.select_one("#awardsTable")  # deal with the awards some other time

    return metadata


def extract_desc(tag: bs4.Tag) -> dict:
    description = {"price_data": {}, "sys_req": {}, "dlc": {}}

    # PRICE DATA
    purchase = tag.select_one("#game_area_purchase")
    for zone in purchase.find_all(class_="game_area_purchase_game_wrapper", recursive=False):
        if ("game_purchase_sub_dropdown" in zone["class"] or  # skipping items with purchase options, mainly mtx and subscriptions
                "dynamic_bundle_description" in zone["class"] or  # skipping dynamic bundles
                "master_sub_trial" in zone["class"] or  # skipping trial items
                "bundle_hidden_by_preferences" in zone["class"]  # skip hidden bundles
        ):
            continue
        title = zone.h1.contents[0].strip()
        description["price_data"][title] = {}
        section = description["price_data"][title]  # shortcut to cut down on typing
        price = get_field(zone, ".game_purchase_price")
        if price is None:  # Discount
            section["discount"] = get_field(zone, ".discount_pct")
            section["original"] = get_field(zone, ".discount_original_price")
            section["final"] = get_field(zone, ".discount_final_price")
        else:
            section["discount"] = "-0%"
            section["original"] = price
            section["final"] = price
    # DLCs
    # dlcs = tag.select_one(".game_area_dlc_section")
    dlcs = tag.select_one(".gameDlcBlocks")
    if dlcs is not None:
        # for dlc in dlcs.select_one(".gameDlcBlocks").find_all(class_="game_area_dlc_row", recursive=False):
        for dlc in dlcs.find_all(class_="game_area_dlc_row", recursive=False):
            name = get_field(dlc, ".game_area_dlc_name")
            description["dlc"][name] = {}
            section = description["dlc"][name]  # Shortcut
            discount = dlc.select_one(".discount_block")
            if discount is not None:
                section["discount"] = get_field(discount, ".discount_pct")
                section["original"] = get_field(discount, ".discount_original_price")
                section["final"] = get_field(discount, ".discount_final_price")
            else:
                price = get_field(dlc, ".game_area_dlc_price")
                section["discount"] = "-0%"
                section["original"] = price
                section["final"] = price

    # SYSTEM REQUIREMENTS
    sys_req = tag.select_one(".game_area_sys_req")
    if sys_req is not None:
        full_only = sys_req.select_one(
            ".game_area_sys_req_full") is not None  # check whether there are both minimum and recommended sysreq or full only
        labels = ("full",) if full_only else ("minimum", "recommended")
        names = ("game_area_sys_req_full",) if full_only else (
            "game_area_sys_req_leftCol", "game_area_sys_req_rightCol")
        for name, cls in zip(labels, names):
            description["sys_req"][name] = {}
            srq = sys_req.select_one(f".{cls}")
            if srq is None or (lst := srq.select_one(".bb_ul")) is None:
                # sysreq block present, but no items
                description["sys_req"][name] = {}
                continue
            for li in lst.find_all(recursive=False):
                li = clean_tags(li, "br")
                strong = li.strong
                if strong is not None and strong.next_sibling is not None and strong.next_sibling.text.strip() != "":
                    # check that there is a strong tag and a non-space string outside of the strong tag
                    component = strong.text
                    requirement = strong.next_sibling.text
                else:
                    t = strong.text if strong is not None else li.text
                    if ("require" in t.lower() or  # Skip 64-bit proc/OS warning
                            "please note" in t.lower() or
                            "laptop versions" in t.lower() or
                            "video chipsets must"):  # Skip additional warnings
                        continue
                    component, requirement = t.split(":", maxsplit=1)
                description["sys_req"][name][component.strip()] = requirement.strip()

    return description


def clean_tags(soup: bs4.BeautifulSoup, tags: Union[List[str], str]) -> bs4.BeautifulSoup:
    for t in soup.find_all(tags):
        t.decompose()
    return soup


def clean_selector(soup: bs4.BeautifulSoup, selectors: Union[List[str], str]) -> bs4.BeautifulSoup:
    for s in soup.select(selectors):
        s.decompose()
    return soup


def parse_try(folder: str, outfile: str):
    with open(outfile, "w", encoding="utf-8") as f:
        for num, name in enumerate(os.listdir(folder)):
            if name in ["1059550.html", "1289670.html", "1675180.html"]:
                # Valve index or other products, which are not games
                continue
            try:
                extract_data(get_soup(folder, name))
            except Exception as e:
                print(f"Error in {num} - {name}")
                print(f"{name}\n{e}\n------------------------------------------", file=f)
            else:
                print(f"Done {num} - {name}")


def save_json(folder: str, filename: str, data):
    with open(os.path.join(folder, filename), "w", encoding="utf-8") as j:
        json.dump(data, j, indent=4, ensure_ascii=False)


def parse_data(folder: str) -> dict:
    out = {}
    for num, name in enumerate(os.listdir(folder)):
        if name in ["1059550.html", "1289670.html", "1675180.html"]:
            # Valve index or other products, which are not games
            continue
        print(f"{num}: Working on {name}")
        out[name[:-5]] = extract_data(get_soup(folder, name))  # keys are IDs
    return out


if __name__ == '__main__':
    # pprint.pprint(extract_data(get_soup("../scraper/gamepages", "39210.html")))  # FFXIV
    # pprint.pprint(extract_data(get_soup("../scraper/gamepages", "1151340.html")))  # FO76
    # pprint.pprint(extract_data(get_soup("../scraper/gamepages", "665300.html")))
    # parse_try("../scraper/gamepages", "errors.out")
    save_json("./", "data.json", parse_data("../scraper/gamepages"))
