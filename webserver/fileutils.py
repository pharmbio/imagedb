import os

def create_merged_filepath(outdir, paths, suffix='.png', normalization=False, equalize=False):
    """
    Build the merged image cache path. Suffix will be adjusted to include
    filter flags (_norm / _eq) so different combinations don't collide.
    """
    # collect filter suffixes
    suffix_parts = []
    if normalization:
        suffix_parts.append('_norm')
    if equalize:
        suffix_parts.append('_eq')

    # final suffix: .png with extra markers
    _suffix = (''.join(suffix_parts) + '.png') if suffix_parts else suffix

    # create a filename from channel basenames
    filename = "-".join([os.path.basename(path) for path in paths])
    filename = filename + _suffix

    # create a subpath (strip leading slash)
    subpath = os.path.dirname(paths[0]).strip('/')
    merged_path = os.path.join(outdir, subpath)

    # add filename
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