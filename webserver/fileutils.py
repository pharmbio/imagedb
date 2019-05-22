import os

def create_merged_filepath(outdir, file1, file2, file3, suffix='.png'):

    # create a filename
    filename = "" + os.path.basename(file1) + "-" + os.path.basename(file2) + "-" + os.path.basename(file3)
    filename = filename + suffix

    # create a subpath
    # strip / from beginning if there is one since this should be a subpath, otherwise os.path.join will fail
    subpath = os.path.dirname(file1).strip('/')

    # strip / from original path - otherwise os.path.join will fail
    merged_path = os.path.join(outdir, subpath)

    # add filename to path
    merged_path = os.path.join(merged_path, filename)

    return merged_path

def create_pngconverted_filepath(outdir, file1, suffix='.png'):

    # create a filename
    filename = "" + os.path.basename(file1)
    filename = filename + suffix

    # create a subpath
    # strip / from beginning if there is one since this should be a subpath, otherwise os.path.join will fail
    subpath = os.path.dirname(file1).strip('/')

    # strip / from original path - otherwise os.path.join will fail
    converted_path = os.path.join(outdir, subpath)

    # add filename to path
    converted_path = os.path.join(converted_path, filename)

    return converted_path