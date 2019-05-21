import os
from filenames.pharmbio_filename_v1 import parse_path_and_file as parse_path_and_file_v1
from filenames.pharmbio_filename_v2 import parse_path_and_file as parse_path_and_file_v2

#def parse_path_and_file(filename):
#    for func in [parse_path_and_file_v1, parse_path_and_file_v2]:
#        metadata = func(filename)
#        if metadata is not None:
#            return metadata

def parse_path_and_file(filename):

    metadata = parse_path_and_file_v1(filename)
    if metadata is not None:
        return metadata

    metadata = parse_path_and_file_v2(filename)
    if metadata is not None:
        return metadata

    if not os.path.isdir(filename):
        raise Exception('Could not parse filename:' + str(filename))
