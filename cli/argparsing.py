import logging
import argparse

#
#  Main entry for script
#

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.debug("Hello in debug")

print("Hello!")

parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('-prd','--proj_root_dirs', help='Description for xxx argument', required=True)

parser.add_argument('-cp','--continous_polling', help='Description for xxx argument', required=True)

parser.add_argument('-pi','--poll_interval', help='Description for xxx argument', required=True)

parser.add_argument('-pdmd','--poll_dirs_margin_days', help='Description for xxx argument', required=True)

parser.add_argument('-pdmd','--exhaustive_initial_poll', help='Description for xxx argument', required=True)

args = vars(parser.parse_args())