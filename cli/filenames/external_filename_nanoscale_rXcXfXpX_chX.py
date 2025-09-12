import re
import os
import sys
import logging
import datetime
from typing import Optional, Dict, Any, List

# Example path:
# /share/data/external-datasets/nanoscale/Plate_5/hs/55195c81-c4c6-4327-b7fc-b0b50de675b2/images/r03c07/r03c07f01p01-ch01t01.tiff

PATH_RE = re.compile(
    r".*/external-datasets/"
    r"(?P<project>[^/]+)/"
    r"(?P<plate>[^/]+)/"
    r"hs/(?P<guid>[^/]+)/"
    r"images/"
    r"r(?P<row>\d+)c(?P<col>\d+)/"
    r"r(?P=row)c(?P=col)f(?P<site>\d+)p(?P<z>\d+)-"
    r"ch(?P<channel>\d+)"
    r"(?:t(?P<timepoint>\d+))?"
    r"\.(?P<extension>tif|tiff|png|jpg|jpeg)$",
    re.IGNORECASE
)

def row_to_letter(row: int) -> Optional[str]:
    """Convert row number to A–Z, then a–z. Return None if out of range."""
    if 1 <= row <= 26:
        return chr(64 + row)   # A-Z
    elif 27 <= row <= 52:
        return chr(96 + (row - 26))  # a-z
    return None

def parse_path_and_file(path: str) -> Optional[Dict[str, Any]]:
    try:
        m = PATH_RE.search(path)
        if m is None:
            return None

        # everything before /hs/
        match_folder = re.match(r"^(?P<folder>.*?)/hs/", path)
        if match_folder is None:
            return None
        folder = match_folder.group("folder")

        # file creation timestamp -> date parts
        try:
            c_time = os.path.getctime(path)
            date_create = datetime.datetime.fromtimestamp(c_time)
        except Exception:
            date_create = None

        # Pull named groups
        project   = m.group("project")
        plate     = m.group("plate")
        row       = m.group("row")
        col       = m.group("col")
        site      = m.group("site")
        z         = m.group("z")
        channel   = m.group("channel")
        extension = m.group("extension").lower()
        timepoint = m.group("timepoint") or "1"

        # well like A02 / E14 / b44 (for 1536 plate)
        row_num = int(row)
        row_as_chr = row_to_letter(row_num)
        if row_as_chr is None:
            return None   # stop parsing if invalid row

        col_str = f"{int(col):02d}"
        well = row_as_chr + col_str

        return {
            "path": path,
            "folder": folder,
            "filename": os.path.basename(path),
            "date_year": (date_create.year if date_create else "2025"),
            "date_month": (date_create.month if date_create else "01"),
            "date_day_of_month": (date_create.day if date_create else "01"),
            "project": project,
            "magnification": "?x",
            "plate": plate,
            "plate_acq_name": path,
            "well": well,
            "wellsample": site,
            "z": z,
            "channel": channel,
            "is_thumbnail": False,
            "guid": m.group("guid"),
            "extension": extension,
            "timepoint": int(timepoint),
            "channel_map_id": 41,
            "microscope": "Opera",
            "parser": os.path.basename(__file__)
        }

    except Exception:
        logging.exception("could not parse")
        return None


def find_sample_files(root: str, max_files: int = 10) -> List[str]:
    """Walk `root` and collect up to `max_files` that look like supported image files."""
    supported_ext = (".tif", ".tiff", ".png", ".jpg", ".jpeg")
    found: List[str] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(supported_ext):
                full = os.path.join(dirpath, fn)
                found.append(full)
                if len(found) >= max_files:
                    return found
    return found


def test_multiple_files(root: str, max_files: int = 10) -> None:
    """Find multiple files under root and run parse_path_and_file on them. Exit if any fails."""
    print(f"\nBatch test: scanning for up to {max_files} files under: {root}")

    files = find_sample_files(root, max_files=max_files)
    if not files:
        print("No files found under root path.")
        sys.exit(1)

    for i, p in enumerate(files, start=1):
        res = parse_path_and_file(p)
        if res is None:
            print(f"\n[{i}] FAILED to parse {p}")
            sys.exit(1)
        print(f"\n[{i}] {p}")
        print(str(res))


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG
    )

    # --- Single-file test ---
    test_path = "/share/data/external-datasets/nanoscale/Plate_5/hs/55195c81-c4c6-4327-b7fc-b0b50de675b2/images/r03c07/r03c07f01p01-ch01t01.tiff"
    retval = parse_path_and_file(test_path)
    print(str(retval))

    # --- Multi-file test (will exit if any fails) ---
    root_path = "/share/data/external-datasets/nanoscale/"
    test_multiple_files(root_path, max_files=10)

    root_path = "/share/data/external-datasets/nanoscale/Plate_5/hs/55195c81-c4c6-4327-b7fc-b0b50de675b2/images/r08c04/"
    test_multiple_files(root_path, max_files=10)

    print("--------")
    print("All test files seem to have passed")
    print("--------")
