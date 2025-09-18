import re
import os
import json
import logging
from functools import lru_cache

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
# /share/mikro/squid/test/cell-density-martin-2022-09-23_2022-10-03_12-58-54.710491/0/D16_2_2_Fluorescence_638_nm_Ex.tiff
#


# Compile a regex pattern to match the structured file path and name, with case-insensitivity for Windows compatibility
__pattern_path_and_file = re.compile(r'''
    ^.*/squid/                                  # Match start and any characters until "/squid/"
    (.*?)/                                      # Capture project name
    (.*?)_                                      # Capture plate
    ([0-9]{4})-([0-9]{2})-([0-9]{2})_           # Capture date (yyyy-mm-dd)
    (.*?)/                                      # Capture time or additional info until the next slash
    (t[0-9]+/)?                                 # Optionally capture timepoint (e.g., "t1/")
    ([A-Z])([0-9]+)_                            # Capture well position (letter and numbers)
    s([0-9]+)_                                  # Capture site index
    x([0-9]+)_                                  # Capture site x coordinate
    y([0-9]+)_                                  # Capture site y coordinate
    (z[0-9]+_)?                                 # Optionally capture site z coordinate
    (.*?)                                       # Capture channel_name (e.g., Fluorescence....., BF....)
    (\..*)                                      # Capture file extension
''', re.IGNORECASE | re.VERBOSE)


CHANNEL_MAP = {

    frozenset({
        "Fluorescence_405_nm_Ex",
        "Fluorescence_488_nm_Ex",
        "Fluorescence_561_nm_Ex",
        "Fluorescence_638_nm_Ex",
        "Fluorescence_730_nm_Ex",
    }): 10,

    frozenset({
        "Fluorescence_405_nm_Ex",
        "Fluorescence_488_nm_Ex",
        "Fluorescence_561_nm_Ex",
        "Fluorescence_638_nm_Ex",
        "Fluorescence_730_nm_Ex",
        "BF_LED_matrix_full",
    }): 22,

    frozenset({
        "Fluorescence_405_nm_Ex",
        "Fluorescence_445_nm_Ex",
        "Fluorescence_514_nm_Ex",
        "Fluorescence_561_nm_Ex",
        "Fluorescence_640_nm_Ex",
    }): 38,

    frozenset({
        "Fluorescence_405_nm_Ex",
        "Fluorescence_445_nm_Ex",
        "Fluorescence_514_nm_Ex",
        "Fluorescence_561_nm_Ex",
        "Fluorescence_640_nm_Ex",
        "BF_LED_matrix_full",
        "BF_LED_matrix_left_half",
        "BF_LED_matrix_right_half",
    }): 39,

    frozenset({
        "Fluorescence_405_nm_Ex",
        "Fluorescence_488_nm_Ex",
        "Fluorescence_561_nm_Ex",
        "Fluorescence_638_nm_Ex",
        "Fluorescence_730_nm_Ex",
        "BF_LED_matrix_full",
        "BF_LED_matrix_left_half",
        "BF_LED_matrix_right_half",
    }): 40,

}

@lru_cache(maxsize=2048)
def load_config_channel_names(dir_path: str):

    def _norm(name: str) -> str:
        return name.replace(" ", "_")

    config_path = os.path.join(dir_path, "config.json")

    if not os.path.isfile(config_path):
        return None  # gracefully handle missing file

    with open(config_path, "r") as f:
        cfg = json.load(f)

    # assume cfg["channels"] exists and is a list
    return tuple(
        _norm(ch["name"])
        for ch in cfg["channels"]
        if ch["enabled"]
    )

def parse_path_and_file(path):
    # If something errors (file not parsable with this parser, then exception and return None)
    try:
        match = re.search(__pattern_path_and_file, path)

        logging.debug(f'match: {match}')

        if match is None:
            return None

        # check if channel_names are in config.json, then it is new squid software
        dir_path = os.path.dirname(path)
        channel_names = load_config_channel_names(dir_path)
        if channel_names is None:
            logging.debug(f"No channels_names or config.json found in {dir_path}")
            return None

        logging.debug(f'match: {match.groups() }')

        tp = match.group(7)
        if tp:
            timepoint = tp[1:-1] # remove t and /
        else:
            timepoint = 0

        time_of_day = match.group(6).replace('.',':')
        date_iso = f"{match.group(3)}-{match.group(4)}-{match.group(5)}T{time_of_day}"

        row = match.group(8)
        col = match.group(9)
        well = f'{row}{col}'

        parsed_channel_name = match.group(14)
        # get channel pos from config file channel_names
        channel_pos = channel_names.index(parsed_channel_name) + 1

        # find channel map from constant
        channel_map_id = CHANNEL_MAP.get(frozenset(channel_names), 10)  # fallback to 10 if unknown

        site = int(match.group(10))
        site_x = int(match.group(11))
        site_y = int(match.group(12))

        z_val = match.group(13)
        if z_val:
            z = int(z_val[1:-1]) # remove leading z and trailing _
        else:
            z = 0

        metadata = {
            'path': path,
            'filename': os.path.basename(path),
            'date_iso': date_iso,
            'project': match.group(1),
            'magnification': '20x',
            'plate': match.group(2),
            'plate_acq_name': path,
            'well': well,
            'wellsample': site,
            'x': site_x,
            'y': site_y,
            'z': z,
            'channel': channel_pos,
            'channel_name': parsed_channel_name,
            'is_thumbnail': False,
            'guid': None,
            'extension': match.group(15),
            'timepoint': timepoint,
            'channel_map_id': channel_map_id,
            'microscope': "squid",
            'parser': os.path.basename(__file__)
        }

        return metadata

    except:
        logging.exception("exception")
        logging.debug("could not parse")
        return None


if __name__ == '__main__':
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)


    retval = parse_path_and_file(
        "/share/mikro3/squid/CLEO_5fp_Clones/clone5_clone6_2025-09-17_14.08.11/C17_s7_x1_y1_z0_Fluorescence_514_nm_Ex.tiff")
    print("\nretval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro3/squid/testsquidplus/testsiteindices_2025-08-25_12.16.04/G8_s1_x0_y0_z0_BF_LED_matrix_full.tiff")
    print("\nretval = " + str(retval))


    





