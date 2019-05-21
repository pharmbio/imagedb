import os
import hashlib


def hash_string(input):
    hashval = hashlib.md5(input.encode('utf-8'))
    return hashval.hexdigest()

def create_merged_filepath(outdir, file1, file2, file3):

    # create a subpath
    basename = os.path.basename(file1)
    new_subpath = basename.replace('_', '/')
    # strip / from beginning if there is one since this should be a subpath
    new_subpath = new_subpath.strip('/')

    # create a filename
    filename = "" + os.path.basename(file1) + os.path.basename(file2) + os.path.basename(file2)
    filename = filename + '.png'

    # strip / from original path - otherwise os.path.join will fail
    merged_path = os.path.join(outdir, new_subpath)
    merged_path = os.path.join(merged_path, filename)

    return merged_path