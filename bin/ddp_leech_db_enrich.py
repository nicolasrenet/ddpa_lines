# !/usr/bin/env python3

"""
Leeches .xml-files in target file structure system to construct metadata files.
"""

from typing import Dict, Generator, List
from ddp_leech_db_main import get_path_list
import fargv
from tqdm import tqdm
from lxml import etree as ET


def in_archive(charter_atomid):
    """
    @rtype Bool
    """
    return True if len(charter_atomid.split("/")) == 5 else False


# 1) leech into list

def get_cei_header(paths: List[str]) -> Dict[str, str]:
    """
    Returns CEI Headers as Dict, Tags are Keys and their Contents are values
    @param paths: Pathlist to Input cei.xml files
    @return: Dict with Header-Metadata, Elements of cei:text
    """
    content_head = {}
    for file in tqdm(paths):
        with open(file, 'r', encoding='utf-8') as current:
            tree = ET.parse(current)
            root = tree.getroot()
            content_head[file] = root[0].text
    return content_head

def get_cei_content(paths: List[str]) -> Dict[str, str]:
    ns = {'atom': "http://www.w3.org/2005/Atom",
          'cei': "http://www.monasterium.net/NS/cei"}
    content = {}
    for file in tqdm(paths):
        with open(file, 'r', encoding='utf-8') as current:
            tree = ET.parse(current)
            root = tree.getroot()
            children = root.getchildren()
            for child in children:
                ET.dump(child)
    return content


# 2) write into json (with indent)
# 3) put into json at collection level


# build image urls
# leech xml for orig and copy links/refs
# combine base urls and leeched parts and create json? on charter level


if __name__ == "__main__":
    p = {
        "root_dir": "..",
        "charter_dir": "{root_dir}/data/MiM",
        "target_dir": "{root_dir}/data/metadata",
        "file_ext": ".cei.xml"
    }

    # params
    args, _ = fargv.fargv(p)

    # charters
    charter_paths = get_path_list(args.charter_dir, ".cei.xml")
    print(len(charter_paths))

    contents = get_cei_content(charter_paths)
    print(contents)

    # print(len(contents))
    # for x,y in contents.items():
    #     print(x,y)


    # headers = get_cei_header(charter_paths)
    # print(len(headers))
    # for header in headers.items():
    #      print(header)


