import logging
import sys
from filenames.filename_parser import parse_path_and_file
from database import Database
from image import Image
import settings as imgdb_settings
import image_monitor


def setup_logging():
    # Setup logging first
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG, INFO, etc. as desired
        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout  # or use filename='app.log' to write to a file
    )



setup_logging()
db = Database.get_instance()
db.initialize_connection_pool(
    user=imgdb_settings.DB_USER,
    password=imgdb_settings.DB_PASS,
    host=imgdb_settings.DB_HOSTNAME,
    port=imgdb_settings.DB_PORT,
    database=imgdb_settings.DB_NAME
)

def delete_and_upload_one_testimage():

    img_path = "/share/mikro2/squid/anders-test/Testplate_monitor_2023-04-18_14.16.04/A03_s1_x0_y0_BF_LED_matrix_full.tiff"
    img_meta = parse_path_and_file(img_path)
    img = Image.from_meta(img_meta)

    # First select plate acquisition id, or insert it if not there
    plate_acq_id = Database.get_instance().select_or_insert_plate_acq(img)

    # Delete image before inserting (in this test-case)
    Database.get_instance().delete_image_meta_from_table_images(img)

    # Insert into images table
    img_id = Database.get_instance().insert_meta_into_table_images(img, plate_acq_id)

    # Insert into upload_to_s3 table
    Database.get_instance().insert_into_upload_table(img, plate_acq_id, img_id)

def delete_and_upload_one_testdir():

    img_path = "/share/mikro2/squid/anders-test/Testplate_monitor_2023-04-18_14.16.04/"


def test_polling_loop():

    poll_dirs_margin_days = 5
    latest_file_change_margin = 7200
    sleep_time = 5
    proj_root_dirs = ["/share/mikro2/squid/anders-test/"]
    exhaustive_initial_poll = False
    continuous_polling = False

    image_monitor.polling_loop(poll_dirs_margin_days,
                               latest_file_change_margin,
                               sleep_time,
                               proj_root_dirs,
                               exhaustive_initial_poll,
                               continuous_polling
    )

def main():

    # delete_and_upload_one_testimage()
    test_polling_loop()


if __name__ == "__main__":
    main()