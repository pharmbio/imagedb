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
    ^.*/squid/                                      # Match start and any characters until "/squid/"
    (?P<project>.*?)/                               # Project name
    (?P<plate>.+)_                                  # Plate (allow underscores)
    (?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})_  # Date (yyyy-mm-dd)
    (?P<time_info>.*?)/                             # Time or additional info until the next slash
    (?P<timepoint_dir>t[0-9]+/)?                    # Optional timepoint dir (e.g., "t1/")
    (?P<row>[A-Z])(?P<col>[0-9]+)_                  # Well position (letter + numbers)
    s(?P<site>[0-9]+)_                              # Site index
    x(?P<x>[0-9]+)_                                 # Site x coordinate
    y(?P<y>[0-9]+)_                                 # Site y coordinate
    (?P<z_dir>z[0-9]+_)?                            # Optional z coordinate
    (?P<channel_name>.*?)                           # Channel name (e.g., Fluorescence..., BF...)
    (?P<extension>\..*)                             # File extension
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

        frozenset({
        "Fluorescence_405_nm_Ex",
        "Fluorescence_445x609",
        "Fluorescence_445x700",
        "Fluorescence_561_nm_Ex",
        "BF_LED_matrix_full",
    }): 43,

}

@lru_cache(maxsize=2048)
def load_config_channel_names(dir_path: str):

    def _norm(name: str) -> str:
        return name.replace(" ", "_")

    # Look for config.json in the given directory only.
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

        dir_path = os.path.dirname(path)

        tp_dir = match.group('timepoint_dir')
        if tp_dir:
            timepoint = tp_dir[1:-1] # remove t and /
            # Images live in .../plate/.../tN/, config.json is in the plate dir one level up.
            config_dir = os.path.dirname(dir_path)
        else:
            timepoint = 0
            config_dir = dir_path

        # check if channel_names are in config.json, then it is new squid software
        channel_names = load_config_channel_names(config_dir)
        if channel_names is None:
            logging.debug(f"No channels_names or config.json found in {config_dir}")
            return None

        logging.debug(f'match groups: {match.groupdict() }')

        time_of_day = match.group('time_info').replace('.',':')
        date_iso = (
            f"{match.group('year')}-"
            f"{match.group('month')}-"
            f"{match.group('day')}T{time_of_day}"
        )

        row = match.group('row')
        col = match.group('col')
        well = f'{row}{col}'

        parsed_channel_name = match.group('channel_name')
        # get channel pos from config file channel_names
        channel_pos = channel_names.index(parsed_channel_name) + 1

        # find channel map from constant
        channel_map_id = CHANNEL_MAP.get(frozenset(channel_names), 10)  # fallback to 10 if unknown

        site = int(match.group('site'))
        site_x = int(match.group('x'))
        site_y = int(match.group('y'))

        z_val = match.group('z_dir')
        if z_val:
            z = int(z_val[1:-1]) # remove leading z and trailing _
        else:
            z = 0

        metadata = {
            'path': path,
            'filename': os.path.basename(path),
            'date_iso': date_iso,
            'project': match.group('project'),
            'magnification': '20x',
            'plate': match.group('plate'),
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
            'extension': match.group('extension'),
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

    retval = parse_path_and_file(
        "/share/mikro4/squid/cp-duo-test13/cp-duo-test13_2025-11-19_09.42.13/t1/O22_s4_x1_y1_z0_Fluorescence_445x700.tiff")
    print("\nretval = " + str(retval))





