import os
import logging
from filenames import pharmbio_squid_filename_test
from filenames import pharmbio_squid_filename_v1
from filenames import pharmbio_IMX_filename_standard
from filenames import pharmbio_IMX_filename_older
from filenames import pharmbio_IMX_filename_relaxed
from filenames import external_filename_christa
from filenames import external_filename_cpjump
from filenames import external_filename_david
from filenames import external_filename_IMX
from filenames import external_filename_gbm_IMX
from filenames import external_filename_opera_rXcXfXpX_chXskXfkXflX

parsers = []
parsers.append(pharmbio_squid_filename_test)
parsers.append(pharmbio_squid_filename_v1)
parsers.append(pharmbio_IMX_filename_standard)
parsers.append(pharmbio_IMX_filename_older)
parsers.append(pharmbio_IMX_filename_relaxed)
parsers.append(external_filename_christa)
parsers.append(external_filename_gbm_IMX)
parsers.append(external_filename_IMX)
parsers.append(external_filename_cpjump)
parsers.append(external_filename_david)
parsers.append(external_filename_opera_rXcXfXpX_chXskXfkXflX)

def parse_path_and_file(filename):

    metadata = None

    for parser in parsers:
        metadata = parser.parse_path_and_file(filename)
        if metadata is not None:
            return metadata

    if metadata is None:
        raise Exception('Could not parse filename:' + str(filename))

    if not os.path.isdir(filename):
        raise Exception('Could not parse filename:' + str(filename))


if __name__ == '__main__':
    
    # python3.10 -m filenames.filename_parser

    #
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    # Testparse
    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/PolinaG-U2OS/181212-U2OS-20X-BpA-HD-DB-high/2018-12-12/1/181212-U2OS-20X-BpA-HD-DB-high_E02_s7_w3_thumbCFB5B241-4E5B-4AB4-8861-A9B6E8F9FE00.tif")
    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/kinase378-v1/kinase378-v1-FA-P015232-A549-48h-P1-L3-r1/2022-01-31/906/kinase378-v1-FA-P015232-A549-48h-P1-L3-r1_B02_s3_w5F56592B1-3477-465C-B118-87465E0163A1.tif")
    print("\nretval = " + str(retval))

    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/kinase378-v1/kinase378-v1-FA-P015240-HOG-48h-P2-L5-r1/2022-03-11/965/kinase378-v1-FA-P015240-HOG-48h-P2-L5-r1_B02_s8_w3_thumb3DF2C4AE-602A-46F6-84B2-9B31D1981B60.tif")
    print("\nretval = " + str(retval))

    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/kinase378-v1/kinase378-v1-FA-P015240-HOG-48h-P2-L5-r1/2022-03-11/965/kinase378-v1-FA-P015240-HOG-48h-P2-L5-r1_B02_s8_w3_thumb3DF2C4AE-602A-46F6-84B2-9B31D1981B60.tif")
    print("\nretval = " + str(retval))

    retval = parse_path_and_file("/share/data//external-datasets/gbm/gbm120/Plate_11173_220802/TimePoint_1/20220802 IF9 8xC1-24 R1 3013 P1_K01_s10_w1.TIF")
    print("\nretval = " + str(retval))

    retval = parse_path_and_file("/share/data/external-datasets/gbm/gbm-120/20220921 IF15 8x25-48/P9-3013-R2/2022-09-24/11288/TimePoint_1/20220921 IF15 8x25-48_O24_s9_w5B8BD893C-A366-45E3-B67F-7D5A3C32DCE3.tif")
    print("\nretval = " + str(retval))
    
    retval = parse_path_and_file("/share/data/external-datasets/compoundcenter/specs1K-v2/P101022-col2-and-3/TimePoint_1/P101022 col 2 and 3_I02_s8_w5.TIF")
    print("\nretval = " + str(retval))
    
    retval = parse_path_and_file("share/data/external-datasets/compoundcenter/specs1K-v2/YML2_1_3__2022-11-02T10_35_46-Measurement 1/Images/r02c02f04p01-ch4sk1fk1fl1.tiff")
    print("\nretval = " + str(retval))
    
    retval = parse_path_and_file("/share/data/external-datasets/compoundcenter/specs1K-v2/P101022_col2-and-3/TimePoint_1/P101022 col 2 and 3_I02_s8_w5.TIF")
    print("\nretval = " + str(retval))
    
    retval = parse_path_and_file("/share/mikro/squid/squid-testplates/RMS-e04-v1-FA-P1-48h-P1-L1_2022-11-30_15-41-14.542994/0/O9_2_2_0_Fluorescence_561_nm_Ex.tiff")
    print("\nretval = " + str(retval))