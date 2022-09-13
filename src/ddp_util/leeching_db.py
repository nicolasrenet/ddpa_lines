# goal: derive target file structure form mom-db dump (as it is)

import os
import random
from pathlib import Path
from pathlib import PurePosixPath

#list paths of all charters in directory
def get_charter_paths(charter_dir, extension):
    """
    returns generator of file paths
    """
    for entry in os.scandir(charter_dir):
        if entry.is_file() and entry.name.endswith(extension):
            yield Path(entry.path)
        elif entry.is_dir():
            yield from get_charter_paths(entry.path, extension)
        else:
            continue


def get_path_list(directory, extension):
    """returns List containing File Paths"""
    return [f"{PurePosixPath(path)}" for path in get_charter_paths(directory, extension)]



if __name__ == "__main__":
    """
    directory in IDE --> use full path
    in bash --> relative
    """
    directory = "/home/florian/Documents/zim/didipcv/data/db/mom-data/metadata.charter.public"
    extension = ".cei.xml"

    paths = get_path_list(directory, extension)
    print(len(paths))


# New

# def get_atom_ids(path_sample):
#     """
#     reads paths and extracts atom id
#     """
#     print(path_sample[1])


# get atom_id from charter


# derive provenance from atom_id, assert file structure, build file tree


# def get_names_from_charter_xml(xml)


# def get_charter_xml_path_elements(


# def leech_charter_xml(charter_xml, root_dir, namespaces, extension):
#     with open(charter_xml, "rb") as f:


#     xml = str(urlopen(charter_url).read(), "utf8")


#     archive_name, fond_name, charter_atomid = get_names_from_charter_xml(xml)
#     archive_name, fond_name, charter_name = get_charter_path_elements(archive_name, fond_name, charter_atomid)

#     charter_full_path=f"{root_dir}/{archive_name}/{fond_name}/{charter_name}"
#     Path(charter_full_path).mkdir(parents=True, exist_ok=True)

#     store_charter(charter_html=charter_html, charter_full_path=charter_full_path, charter_atomid=charter_atomid)
