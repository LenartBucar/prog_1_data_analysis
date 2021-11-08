import csv
import json
import re
import pprint
from typing import Dict, List

data_sample = {"1016120": {
    "title": "PGA TOUR 2K21",
    "description": "Play against the pros. Play with your crew. In PGA TOUR 2K21, you can play by the rules or create your own featuring a new PGA TOUR Career Mode, licensed courses and more! Powered by The Golf Club.",
    "reviews_recent": {
        "text": "79% of the 153 user reviews in the last 30 days are positive.",
        "mood": "Mostly Positive"
    },
    "reviews_all": {
        "text": "83% of the 3,606 user reviews for this game are positive.",
        "mood": "Very Positive"
    },
    "date": "20 Aug, 2020",
    "developer": "HB Studios Multimedia Ltd.",
    "publisher": "2K",
    "tags": [
        "Sports",
        "Simulation",
        "Local Multiplayer",
        "Golf",
        "Turn-Based",
        "Character Customization"
    ],
    "categories": [
        "Single-player",
        "Online PvP",
        "Shared/Split Screen PvP",
        "Online Co-op",
        "Shared/Split Screen Co-op",
        "Steam Achievements",
        "Full controller support",
        "In-App Purchases",
        "Steam Turn Notifications",
        "Includes level editor",
        "Remote Play on Tablet",
        "Remote Play on TV",
        "Remote Play Together"
    ],
    "languages": {
        "English": [
            True,
            True,
            True
        ],
        "French": [
            True,
            False,
            False
        ],
        "Italian": [
            True,
            False,
            False
        ],
        "German": [
            True,
            False,
            False
        ],
        "Spanish - Spain": [
            True,
            False,
            False
        ],
        "Japanese": [
            True,
            False,
            False
        ],
        "Korean": [
            True,
            False,
            False
        ],
        "Simplified Chinese": [
            True,
            False,
            False
        ],
        "Traditional Chinese": [
            True,
            False,
            False
        ]
    },
    "rating": {
        "image_url": "https://store.cloudflare.steamstatic.com/public/shared/images/game_ratings/PEGI/3.png",
        "descriptors": [
            ""
        ],
        "agency": "Rating for: PEGI"
    },
    "metascore": "74",
    "price_data": {
        "Buy PGA TOUR 2K21": {
            "discount": "-0%",
            "original": "59,99€",
            "final": "59,99€"
        },
        "Buy PGA TOUR 2K21 Deluxe Edition": {
            "discount": "-0%",
            "original": "69,99€",
            "final": "69,99€"
        },
        "Buy PGA TOUR 2K21 Baller Edition": {
            "discount": "-0%",
            "original": "79,99€",
            "final": "79,99€"
        }
    },
    "sys_req": {
        "minimum": {
            "OS:": "Windows 7x64 / Windows 8.1x64 / Windows 10x64",
            "Processor:": "Intel Core i5-760 @ 2.80GHz or equivalent",
            "Memory:": "4 GB RAM",
            "Graphics:": "AMD Radeon HD 5770 or NVIDIA GTX 650 with 1GB Video Ram",
            "DirectX:": "Version 11",
            "Storage:": "12 GB available space",
            "Sound Card:": "DirectX Compatible Sound Device"
        },
        "recommended": {
            "OS:": "Windows 7x64 / Windows 8.1x64 / Windows 10x64",
            "Processor:": "Intel Core i5-4670 CPU @ 3.40GHz or equivalent",
            "Memory:": "8 GB RAM",
            "Graphics:": "AMD Radeon HD 7850 or NVIDIA GTX 660 with 2GB video RAM",
            "DirectX:": "Version 11",
            "Storage:": "12 GB available space",
            "Sound Card:": "DirectX Compatible Sound Device"
        }
    },
    "dlc": {
        "PGA TOUR 2K21 Baller Pack": {
            "discount": "-0%",
            "original": "24,99€",
            "final": "24,99€"
        },
        "PGA TOUR 2K21 Callaway Club Drop Pack": {
            "discount": "-0%",
            "original": "9,99€",
            "final": "9,99€"
        },
        "PGA TOUR 2K21 Puma Swag Pack": {
            "discount": "-0%",
            "original": "9,99€",
            "final": "9,99€"
        }
    }
},
}

game_data__header = ["id", "title", "description", "date", "dev_id", "pub_id", "metascore", "age_rating", "agency"]
game_reviews__header = ["id", "total_recent", "positive_recent", "mood_recent", "total_all", "positive_all", "mood_all"]
entities__header = ["id", "name"]  # developers and publishers, IDs are internal
info__header = ["id", "tag", "type"]  # type -> "T" for tag, "C" for category, "R" for rating descriptor
price__header = ["id", "name", "discount", "original", "final",
                 "type"]  # type -> "M" for main purchase option, "D" for DLC
language__header = ["id", "language", "interface", "audio", "subtitles"]
sysreq_fields = ["OS", "CPU", "RAM", "Graphics", "DirectX", "Disk Space", "Additional"]
sysreq__header = ["id", *sysreq_fields, "type"]  # type -> "M" for minimum, "R" for recommeded,
sysreq__fix = {'Additional Notes': "Additional",
               'Additional Notes:': "Additional",
               'Additional:': "Additional",
               'Audio:': "Audio",
               'Built-in Graphics:': "Built-In Graphics",
               'Co-op/Multiplayer Hosting:': "Co-op/Multiplayer Hosting",
               'Computer:': "Computer",
               'Controller support:': "Controller support",
               'DirectX Version:': "DirectX",
               'DirectX version:': "DirectX",
               'DirectX:': "DirectX",
               'DirectX® Version:': "DirectX",
               'DirectX®': "DirectX",
               'DirectX®:': "DirectX",
               'Direct®:': "DirectX",
               'Disk Space:': "Disk Space",
               'Display:': "Display",
               'Download Size:': "Disk Space",
               'Drive Space:': "Disk Space",
               'Further information:': "Additional",
               'Graphics': "Graphics",
               'Graphics Card:': "Graphics",
               'Graphics:': "Graphics",
               'Hard Disk Space': "Disk Space",
               'Hard Disk Space:': "Disk Space",
               'Hard Disk:': "Disk Space",
               'Hard Drive': "Disk Space",
               'Hard Drive:': "Disk Space",
               'Hard disk space:': "Disk Space",
               'Internet Connection:': "Network",
               'Internet:': "Network",
               'Memory': "RAM",
               'Memory:': "RAM",
               'Network:': "Network",
               'Note': "Additional",
               'Note:': "Additional",
               'OS': "OS",
               'OS Version:': "OS",
               'OS:': "OS",
               'Operating system:': "OS",
               'Operating System:': "OS",
               'Other Requirements:': "Other",
               'Other requirements:': "Other",
               'Other:': "Other",
               'Peripherals:': "Peripherals",
               'Processor': "CPU",
               'Processor:': "CPU",
               'RAM:': "RAM",
               'Sound': "Audio",
               'Sound Card': "Audio",
               'Sound Card:': "Audio",
               'Sound:': "Audio",
               'Storage:': "Disk Space",
               'Storage (high-quality audio):': 'Disk Space',
               'Supported OS:': "OS",
               'Supported Video Cards:': "Graphics",
               'System Memory:': "RAM",
               'Video Card': "Graphics",
               'Video Card:': "Graphics",
               'Video Memory:': "VRAM",
               'Video:': "Graphics"}

HEADERS = [game_data__header, game_reviews__header, info__header, price__header, language__header, sysreq__header]

ENTITIES = []  # TODO: maybe a better data structure?

PATTERNS: Dict[str, re.Pattern] = {
    "agency": re.compile("Rating for: (.*)"),
    "age_rating": re.compile(r".*/(.*)\..+"),  # capture the filename of the URL
    "review_num": re.compile(r"(\d{2})% of the ([\d,]+) user reviews")
}


def load_json(filename: str) -> dict:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_ent_id(ent: str) -> int:
    """
    Returns the ID of the entity. If the ID doesn't exist yet, it gives it a new one.
    THE FUNCTION MODIFIES THE GLOBAL VARIABLE `ENTITIES`, if the given entity doesn't have an ID yet
    :param ent: name of the entity
    :return: ID of the entity, -1 for None
    """
    if ent is None:
        return -1
    if ent not in ENTITIES:
        ENTITIES.append(ent)
    return ENTITIES.index(ent)


def make_csv_row(game_id: str, data: dict):
    game_data = make_data_row(game_id, data)
    reviews = make_rating_row(game_id, data)
    tags = generate_tags(game_id, data)
    prices = generate_prices(game_id, data)
    return game_data, reviews, tags, prices


def make_data_row(game_id: str, data: dict) -> dict:
    if data["rating"]["agency"] != "":
        agency = PATTERNS["agency"].match(data["rating"]["agency"]).group(1)
    else:
        agency = ""
    if data["rating"]["image_url"] != "":
        age_rating = PATTERNS["age_rating"].match(data["rating"]["image_url"]).group(1)
    else:
        age_rating = ""
    game_data = {
        "id": game_id,
        "title": data["title"],
        "description": data["description"],
        "date": data["date"],
        "dev_id": get_ent_id(data.get("developer")),
        "pub_id": get_ent_id(data.get("publisher")),
        "metascore": data["metascore"],
        "age_rating": age_rating,
        "agency": agency,
    }
    return game_data


def make_rating_row(game_id: str, data: dict) -> dict:
    if data.get("reviews_recent", {}) == {}:
        data["reviews_recent"] = {"text": "", "mood": ""}
    if "last 30 days" not in data["reviews_recent"]["text"]:  # in case the game is very new
        data["reviews_all"] = data["reviews_recent"]
        data["reviews_recent"] = {"text": "", "mood": ""}
    match_r = PATTERNS["review_num"].match(data["reviews_recent"]["text"])
    if match_r is not None:
        p_recent = int(match_r.group(1))
        n_recent = int(match_r.group(2).replace(",", ""))
    else:
        p_recent = 0
        n_recent = 0
    match_a = PATTERNS["review_num"].match(data["reviews_all"]["text"])
    if match_a is not None:
        p_all = int(match_a.group(1))
        n_all = int(match_a.group(2).replace(",", ""))
    else:
        p_all = 0
        n_all = 0
    game_reviews = {
        "id": game_id,
        "total_recent": n_recent,
        "positive_recent": int(n_recent * p_recent / 100),
        "mood_recent": data["reviews_recent"]["mood"],
        "total_all": n_all,
        "positive_all": int(n_all * p_all / 100),
        "mood_all": data["reviews_all"]["mood"],
    }

    return game_reviews


def generate_tags(game_id: str, data: dict) -> List[dict]:
    tags = []

    for t, tag_list in zip(("T", "C", "R"), (data["tags"], data["categories"], data["rating"]["descriptors"])):
        for tag in tag_list:
            if tag == "":
                continue
            tags.append(
                {"id": game_id,
                 "tag": tag,
                 "type": t,
                 }
            )

    # tags = [{"id": game_id, "tag": tag, "type": t} for t, tag in zip(("T", "C", "R"), (data["tags"], data["categories"], data["rating"]["descriptors"]))]

    return tags


def generate_prices(game_id: str, data: dict) -> List[dict]:
    prices = []

    for t, price_list in zip(("M", "D"), (data["price_data"], data["dlc"])):
        price_list: Dict[str, Dict[str, str]]
        for name, values in price_list.items():
            prices.append(
                {
                    "id": game_id,
                    "name": name,
                    "discount": values["discount"],
                    "original": values["original"],
                    "final": values["final"],
                    "type": t
                }
            )
    return prices


def generate_languages(game_id: str, data: dict) -> List[dict]:
    languages = []

    for language, support in data["languages"].items():
        if len(support) == 1:  # language not supported
            continue
        languages.append({
            "id": game_id,
            "language": language,
            "interface": support[0],
            "audio": support[1],
            "subtitles": support[2],
        })

    return languages


def generate_sys_reqs(game_id: str, data: dict):
    sys_reqs = []
    for t, reqs in data["sys_req"].items():
        reqs = {sysreq__fix.get(k, ""): v for k, v in reqs.items() if sysreq__fix.get(k,
                                                                                      "") in sysreq_fields}  # fix the utter mess of possible field names, and filter to the interesting ones
        sys_reqs.append({
            "id": game_id,
            **reqs,
            "type": t[0].upper(),
        })

    return sys_reqs


CSV_GENERATORS = [make_data_row, make_rating_row, generate_tags, generate_prices, generate_languages, generate_sys_reqs]


def write_csvs(filenames: List[str], ent_name: str, data_all: dict):
    for filename, header, generator in zip(filenames, HEADERS, CSV_GENERATORS):
        print(f"Working on {filename}")
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, header)
            writer.writeheader()
            for g_id, g_data in data_all.items():
                row = generator(g_id, g_data)
                if type(row) == list:
                    writer.writerows(row)
                else:
                    writer.writerow(row)

    with open(ent_name, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, entities__header)
        writer.writeheader()
        writer.writerows([{"id": n, "name": name} for n, name in enumerate(ENTITIES)])


if __name__ == '__main__':
    data = load_json("data.json")
    filenames = ["CSV/game_data.csv",
                 "CSV/game_reviews.csv",
                 "CSV/game_info.csv",
                 "CSV/game_price.csv",
                 "CSV/game_languages.csv",
                 "CSV/game_sysreq.csv"]
    write_csvs(filenames, "CSV/entities.csv", data)
    # for g_id, g_data in data.items():
    #     print(make_csv_row(g_id, g_data))
    # print({k for _, v in data.items() for k in v.keys()})
    # sysreq_keys = set()
    # for k, v in data.items():
    #     sysreq_keys.update(v["sys_req"].get("minimum", {}).keys())
    #     sysreq_keys.update(v["sys_req"].get("recommended", {}).keys())
    # print(sorted(sysreq_keys))
