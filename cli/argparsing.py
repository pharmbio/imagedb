import logging
import traceback
import argparse

import settings as imgdb_settings

def polling_loop(poll_dirs_margin_days, latest_file_change_margin, sleep_time, proj_root_dirs, exhaustive_initial_poll, continuous_polling):

    logging.info("Inside polling loop")

#
#  Main entry for script
#

try:
    #
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    rootLogger = logging.getLogger()

    parser = argparse.ArgumentParser(description='Description of your program')

    parser.add_argument('-prd', '--proj-root-dirs', help='Description for xxx argument',
                        default=imgdb_settings.PROJ_ROOT_DIRS)
    parser.add_argument('-cp', '--continuous-polling', help='Description for xxx argument',
                        default=imgdb_settings.CONTINUOUS_POLLING)
    parser.add_argument('-pi', '--poll-interval', help='Description for xxx argument',
                        default=imgdb_settings.POLL_INTERVAL)
    parser.add_argument('-pdmd', '--poll-dirs-margin-days', help='Description for xxx argument',
                        default=imgdb_settings.POLL_DIRS_MARGIN_DAYS)
    parser.add_argument('-eip', '--exhaustive-initial-poll', help='Description for xxx argument',
                        default=imgdb_settings.EXHAUSTIVE_INITIAL_POLL)
    parser.add_argument('-lfcm', '--latest-file-change-margin', help='Description for xxx argument',
                        default=imgdb_settings.LATEST_FILE_CHANGE_MARGIN)

    args = parser.parse_args()

    print(args)

    polling_loop(args.poll_dirs_margin_days,
                 args.latest_file_change_margin,
                 args.poll_interval,
                 args.proj_root_dirs,
                 args.exhaustive_initial_poll,
                 args.continuous_polling)

except Exception as e:
    print(traceback.format_exc())
    logging.info("Exception out of script")