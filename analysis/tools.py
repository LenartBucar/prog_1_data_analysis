import re
from typing import List, Tuple

import csv  # testing
import pprint


def get_os(os_string: str) -> Tuple[List[str], bool, bool]:
    """
    Check which OSs are supported
    :param os_string: OS string from Steam
    :return: list of supported OSs, support for 32 bit systems, support for 64 bit systems
    """
    checks = ["vista", "xp", "7", "8", "10"]
    available = list(filter(lambda x: x in os_string.lower(), checks))
    return available, "32" in os_string, "64" in os_string


def get_ram(ram_string: str) -> List[float]:
    nums = re.compile(r"([\d.]+)\s*(?:MB|GB)")
    return [x/1000 if x > 100 else x for x in map(float, nums.findall(ram_string))]  # convert MB into GB where needed


def get_disk(disk_string: str) -> Tuple[int, str]:  # TODO: WTF
    if disk_string == "" or "TBD" in disk_string:
        return 0, ""
    size_pattern = re.compile(r"([\d.]+)[\s+]*(GB|MB|gig)")
    match = size_pattern.search(disk_string)
    # if match is None:
    #     print(repr(disk_string))
    size, unit = match.groups()
    return float(size), unit


if __name__ == '__main__':
    with open("../parser/CSV/game_sysreq.csv", "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    disk = [(d["Disk Space"], get_disk(d["Disk Space"])) for d in data]
    pprint.pprint(disk)
