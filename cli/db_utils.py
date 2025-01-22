import psycopg2
from psycopg2 import pool
from datetime import datetime

import logging

import settings as imgdb_settings
from image import Image

__connection_pool = None

def get_connection():

    global __connection_pool
    if __connection_pool is None:
        __connection_pool = pool.SimpleConnectionPool(1, 2, user=imgdb_settings.DB_USER,
                                                               password=imgdb_settings.DB_PASS,
                                                               host=imgdb_settings.DB_HOSTNAME,
                                                               port=imgdb_settings.DB_PORT,
                                                               database=imgdb_settings.DB_NAME)
    return __connection_pool.getconn()


def put_connection(pooled_connection):

    global __connection_pool
    if __connection_pool:
        __connection_pool.putconn(pooled_connection)


def insert_meta_into_table_images(img: Image, plate_acq_id):

    conn = None
    try:

        insert_query = insert_query = """
            INSERT INTO images(
                plate_acquisition_id,
                plate_barcode,
                timepoint,
                well,
                site,
                channel,
                channel_name,
                z,
                path
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        conn = get_connection()
        insert_cursor = conn.cursor()
        insert_cursor.execute(
            insert_query,
            [
                plate_acq_id,
                img.get_plate_barcode(),
                img.get_timepoint(),
                img.get_well(),
                img.get_wellsample(),
                img.get_channel(),
                img.get_channel_name(),
                img.get_z(),
                img.get_path()
            ]
        )

        new_id = insert_cursor.fetchone()[0]
        insert_cursor.close()
        conn.commit()

        return new_id

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)


def insert_into_upload_table(img: Image, plate_acq_id, img_id):
    """
    Insert a record into the 'upload_to_s3' table to queue a file for upload.

    :param img_meta: dictionary with metadata (e.g. path, project, etc.)
    :param plate_acq_id: acquisition ID associated with this image
    :param img_id: the primary key of the image in the 'images' table
    :return: the primary key ID of the newly inserted row in 'upload_to_s3'
    """
    conn = None
    insert_cursor = None

    try:
        # Example schema (adjust as needed):
        #   id (PK), image_id, path, acq_id, project, status, retry_count, ...
        #
        # Here we set status = 'waiting' by default.
        insert_query = """
            INSERT INTO upload_to_s3 (
                image_id,
                path,
                acq_id,
                project,
                status
            )
            VALUES (%s, %s, %s, %s, 'waiting')
            RETURNING id
        """

        conn = get_connection()
        insert_cursor = conn.cursor()
        insert_cursor.execute(
            insert_query,
            (
                img_id,
                img.get_path(),
                plate_acq_id,
                img.get_project()
            )
        )

        new_upload_id = insert_cursor.fetchone()[0]
        conn.commit()

        return new_upload_id

    except Exception as err:
        logging.exception("Error inserting into upload_to_s3")
        raise err

    finally:
        if insert_cursor is not None:
            insert_cursor.close()
        put_connection(conn)

def select_or_insert_plate_acq(img):

    # First select to see if plate_acq already exists
    plate_acq_id = select_plate_acq_id(img)

    if plate_acq_id is None:
        plate_acq_id = insert_plate_acq(img)

    return plate_acq_id


def select_plate_acq_id(img):

    conn = None

    acq_folder = img.get_folder()

    try:

        query = ("SELECT id "
                 "FROM plate_acquisition "
                 "WHERE folder = %s ")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, [acq_folder])
        plate_acq_id = cursor.fetchone()
        cursor.close()

        return plate_acq_id

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)

# def getChannelMapIDFromMapping(project, plate_acq_name):
#     conn = None

#     try:

#         query = (
#                  "SELECT channel_map "
#                  "FROM channel_map_mapping "
#                  "WHERE project = %s "
#                  "AND "
#                  "( plate_acquisition_name = %s OR plate_acquisition_name = '*')"
#                  )

#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute(query, (project, plate_acq_name))
#         result = cursor.fetchone()
#         cursor.close()

#         # set default if nothing speciffic for this plate or plate_acquisition
#         if result:
#             channel_map_id = result[0]
#         else:
#             channel_map_id = None

#         logging.info(f"channel_map_id = {channel_map_id}")

#         return channel_map_id

#     except Exception as err:
#         logging.exception("Message")
#         raise err
#     finally:
#         put_connection(conn)


def insert_plate_acq(img):

    conn = None
    try:

        query = "INSERT INTO plate_acquisition(plate_barcode, name, project, imaged, microscope, channel_map_id, timepoint, folder) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, [img.get_plate_barcode(),
                               img.get_plate(),
                               img.get_project(),
                               img.get_imaged(),
                               img.get_microscope(),
                               img.get_channel_map_id(),
                               img.get_timepoint(),
                               img.get_folder()
                               ])

        plate_acq_id = cursor.fetchone()[0]
        cursor.close()

        conn.commit()

        return plate_acq_id

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)


def image_exists_in_db(img: Image) -> bool:
    """
    Checks whether the image (based on its path) already exists in the database.

    :param img: An Image instance (or any object with a get_path() method)
    :return: True if the image exists in the DB, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            exists_path_query = "SELECT EXISTS (SELECT 1 FROM images WHERE path = %s)"
            cursor.execute(exists_path_query, [img.get_path()])
            path_exists = cursor.fetchone()[0]
        return path_exists

    except Exception as err:
        logging.exception("Error checking if image exists in db")
        raise err
    finally:
        if conn:
            put_connection(conn)

def select_finished_plate_acq_folder():

    conn = None
    try:
        query = ("SELECT folder "
                 "FROM plate_acquisition "
                 "WHERE finished IS NOT NULL")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        # get result as list instead of tuples
        result = [r[0] for r in cursor.fetchall()]

        cursor.close()

        return result

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)

def select_unfinished_plate_acq_folder():

    conn = None
    try:
        query = ("SELECT folder "
                 "FROM plate_acquisition "
                 "WHERE finished IS NULL")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        # get result as list instead of tuples
        result = [r[0] for r in cursor.fetchall()]

        cursor.close()

        return result

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)

def update_acquisition_finished(folder: str, timestamp: float):

    logging.info("inside update_acquisition_finished, folder: " + folder)

    conn = None
    try:

        query = (" UPDATE plate_acquisition "
                 " SET finished = %s "
                 " WHERE folder = %s")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (datetime.utcfromtimestamp(timestamp), folder) )
        assert cursor.rowcount == 1, "rowcount should always be 1 for this update query"
        cursor.close()
        conn.commit()
    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)
