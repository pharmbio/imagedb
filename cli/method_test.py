import logging
import sys
from filenames.filename_parser import parse_path_and_file
from database import Database
from image import Image
import settings as imgdb_settings


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

def main():

    delete_and_upload_one_testimage()


if __name__ == "__main__":
    main()