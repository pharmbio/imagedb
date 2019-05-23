import os

def create_merged_filepath(outdir, paths, suffix='.png'):

    # create a filename
    for path in paths:
      filename = "" + os.path.basename(path) + "-"

    filename = filename + suffix

    # create a subpath
    # strip / from beginning if there is one since this should be a subpath, otherwise os.path.join will fail
    subpath = os.path.dirname(paths[0]).strip('/')

    # strip / from original path - otherwise os.path.join will fail
    merged_path = os.path.join(outdir, subpath)

    # add filename to path
    merged_path = os.path.join(merged_path, filename)

    return merged_path

def create_pngconverted_filepath(outdir, path, suffix='.png'):

    # create a filename
    filename = "" + os.path.basename(path)
    filename = filename + suffix

    # create a subpath
    # strip / from beginning if there is one since this should be a subpath, otherwise os.path.join will fail
    subpath = os.path.dirname(path).strip('/')

    # strip / from original path - otherwise os.path.join will fail
    converted_path = os.path.join(outdir, subpath)

    # add filename to path
    converted_path = os.path.join(converted_path, filename)

    return converted_path