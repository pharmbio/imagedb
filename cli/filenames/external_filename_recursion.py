import re
import os
import logging

def parse_path_and_file(path):
    # If something errors (file not parsable with this parser, then exception and return None)
    try:
        # Extract project, experiment, and plate from the path
        # Example path:
        # /share/data/external-datasets/recursion/rxrx3-core/compound-001/Plate1/AA15_s1_1.tiff
        match = re.search(
            r'.*/external-datasets/recursion/(?P<project>[^/]+)/(?P<experiment>[^/]+)/(?P<plate>Plate\d+)/.*', path
        )
        if match is None:
            logging.debug("No match for project, experiment, and plate")
            return None

        project = match.group('project')
        experiment = match.group('experiment')
        plate_dir = match.group('plate')  # e.g., Plate1

        plate = experiment

        # Extract timepoint from PlateX
        timepoint_match = re.search(r'Plate(\d+)', plate_dir)
        if timepoint_match is None:
            logging.debug(f"No numeric timepoint found in: {plate_dir}")
            return None
        timepoint = timepoint_match.group(1)

        logging.debug(f"project: {project}")
        logging.debug(f"experiment: {experiment}")
        logging.debug(f"plate_dir: {plate_dir}")
        logging.debug(f"plate: {plate}")
        logging.debug(f"timepoint: {timepoint}")

        # Extract well, site, channel, and extension from filename
        match = re.search(
            r'.*/'                       # any characters ending with a slash
            r'(?P<well>[A-Z]{1,2}\d+)'   # well (e.g., A1, AA1, AB2)
            r'_s(?P<site>\d+)'           # site number (e.g., s1)
            r'_(?P<channel>\d+)'         # channel number (e.g., _6)
            r'\.(?P<extension>.*)$',     # extension (e.g., .tif)
            path
        )

        if match is None:
            logging.debug("Filename pattern does not match")
            return None

        well = match.group('well')
        site = int(match.group('site'))
        channel = int(match.group('channel'))
        extension = match.group('extension')

        # Normalize double-letter wells to single alphabet if applicable
        if len(well) > 2 and well[0].isalpha() and well[1].isalpha():
            second_letter = well[1].upper()
            if 'A' <= second_letter <= 'Z':  # Check if it's a valid second letter
                normalized_well = chr(ord('a') + (ord(second_letter) - ord('A')))
                well = normalized_well + well[i2:]  # Replace the first part with normalized value

        # Return if wrong extension
        valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg")
        if extension.lower() not in valid_extensions:
            logging.debug("Invalid extension")
            return None

        # Derive the folder by removing the Plate directory and everything after it
        folder = re.sub(r'/Plate\d+/.*', '', path)

        # Assemble metadata dictionary
        metadata = {
            'path': path, # complete path for file
            'folder': folder, # root folder for acquisition, this is unique key for images belonging to an acquisition
            'filename': os.path.basename(path),
            'date_year': 2024,
            'date_month': 11,
            'date_day_of_month': 1,
            'project': project,
            'magnification': '?x',
            'plate': plate,
            'plate_acq_name': plate,
            'well': well,
            'wellsample': site,
            'x': 0,
            'y': 0,
            'z': 0,
            'channel': channel,
            'channel_name': str(channel),
            'is_thumbnail': False,
            'guid': None,
            'extension': extension,
            'timepoint': timepoint,
            'channel_map_id': 35,
            'microscope': "Unknown",
            'make_thumb': "False",
            'experiment': experiment,
            'parser': os.path.basename(__file__)
        }

        return metadata

    except Exception as e:
        logging.exception("Exception occurred during parsing")
        return None

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG
    )

    # Test parse
    test_paths = [
        "/share/data/external-datasets/recursion/rxrx3-core/compound-001/Plate1/A1_s1_6.tif",
        "/share/data/external-datasets/recursion/rxrx3-core/compound-001/Plate1/AA1_s1_6.tif",
        "/share/data/external-datasets/recursion/rxrx3-core/gene-002/Plate12/AB1_s1_6.tif"
    ]

    for test_path in test_paths:
        retval = parse_path_and_file(test_path)
        print(f"\nretval for {test_path} = {retval}")
