import os
from filenames.pharmbio_filename_v1 import parse_path_and_file as parse_path_and_file_v1
from filenames.pharmbio_filename_v2 import parse_path_and_file as parse_path_and_file_v2
from filenames.pharmbio_filename_v3 import parse_path_and_file as parse_path_and_file_v3
from filenames.pharmbio_filename_v4 import parse_path_and_file as parse_path_and_file_v4
from filenames.external_filename_v1 import parse_path_and_file as parse_path_and_file_v5
from filenames.external_filename_v2 import parse_path_and_file as parse_path_and_file_v6

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

    metadata = parse_path_and_file_v3(filename)
    if metadata is not None:
        return metadata
    
    metadata = parse_path_and_file_v4(filename)
    if metadata is not None:
        return metadata

    metadata = parse_path_and_file_v5(filename)
    if metadata is not None:
        return metadata
    
    metadata = parse_path_and_file_v6(filename)
    if metadata is not None:
        return metadata

    if metadata is None:
        raise Exception('Could not parse filename:' + str(filename))

    if not os.path.isdir(filename):
        raise Exception('Could not parse filename:' + str(filename))
