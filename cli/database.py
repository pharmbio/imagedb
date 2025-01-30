from __future__ import annotations
import logging
import threading
from datetime import datetime
from typing import Any, List, Optional

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

import settings as imgdb_settings
from image import Image  # Make sure this import does not create a circular dependency

class Database:
    _instance: Optional[Database] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> Database:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.connection_pool = None  # Will be set during initialization
        return cls._instance

    @classmethod
    def get_instance(cls) -> Database:
        return cls()

    def initialize_connection_pool(self, **connection_info) -> None:
        if self.connection_pool is None:
            if connection_info:
                try:
                    self.connection_pool = pool.SimpleConnectionPool(
                        minconn=1,
                        maxconn=10,
                        **connection_info
                    )
                    self.initialized = True
                    logging.info("Database connection pool initialized.")
                except Exception as e:
                    logging.exception("Failed to initialize connection pool.")
                    raise e
            else:
                raise ValueError("Connection information must be provided to initialize the connection pool.")

    def get_connection(self):
        if self.connection_pool is None:
            raise Exception("Connection pool has not been initialized.")
        return self.connection_pool.getconn()

    def release_connection(self, conn) -> None:
        if self.connection_pool:
            self.connection_pool.putconn(conn)
        else:
            raise Exception("Connection pool has not been initialized.")

    # --------------------------------------------------------------------------
    # Query methods
    # --------------------------------------------------------------------------
    def insert_meta_into_table_images(self, img: Image, plate_acq_id: Any) -> Any:
        """
        Inserts a record into the 'images' table and returns the generated image id.
        """
        query = """
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
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    [
                        plate_acq_id,
                        img.get_plate_barcode(),
                        img.get_timepoint(),
                        img.get("well"),
                        img.get("wellsample"),
                        img.get("channel"),
                        img.get("channel_name"),
                        img.get("z", 0),
                        img.get_path()
                    ]
                )
                new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as err:
            logging.exception("Error inserting image metadata")
            conn.rollback()
            raise err
        finally:
            self.release_connection(conn)

    def insert_into_upload_table(self, img: Image, plate_acq_id: Any, img_id: Any) -> Any:
        """
        Inserts a record into 'upload_to_s3' with a default status of 'waiting',
        returning the generated upload record id.
        """
        query = """
            INSERT INTO upload_to_s3 (
                image_id,
                path,
                acq_id,
                project,
                status
            )
            VALUES (%s, %s, %s, %s, 'waiting')
            ON CONFLICT (path) DO NOTHING
            RETURNING id
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        img_id,
                        img.get_path(),
                        plate_acq_id,
                        img.get_project()
                    )
                )
                new_upload_id = cursor.fetchone()[0]
            conn.commit()
            return new_upload_id
        except Exception as err:
            logging.exception("Error inserting upload record")
            conn.rollback()
            raise err
        finally:
            self.release_connection(conn)

    def select_plate_acq_id(self, img: Image) -> Optional[Any]:
        """
        Selects an existing plate acquisition id based on the folder.
        Returns None if not found.
        """
        acq_folder = img.get_folder()
        query = "SELECT id FROM plate_acquisition WHERE folder = %s"
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (acq_folder,))
                result = cursor.fetchone()
                return result[0] if result is not None else None
        except Exception as err:
            logging.exception("Error selecting plate acquisition id")
            raise err
        finally:
            self.release_connection(conn)

    def insert_plate_acq(self, img: Image) -> Any:
        """
        Inserts a new plate acquisition record and returns its id.
        """
        query = """
            INSERT INTO plate_acquisition(
                plate_barcode,
                name,
                project,
                imaged,
                microscope,
                channel_map_id,
                timepoint,
                folder
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        img.get_plate_barcode(),
                        img.get_plate(),
                        img.get_project(),
                        img.get("imaged"),
                        img.get("microscope"),
                        img.get("channel_map_id"),
                        img.get_timepoint(),
                        img.get_folder()
                    )
                )
                plate_acq_id = cursor.fetchone()[0]
            conn.commit()
            return plate_acq_id
        except Exception as err:
            logging.exception("Error inserting plate acquisition")
            conn.rollback()
            raise err
        finally:
            self.release_connection(conn)

    def select_or_insert_plate_acq(self, img: Image) -> Any:
        """
        Returns an existing plate acquisition id or inserts a new record if none exists.
        """
        plate_acq_id = self.select_plate_acq_id(img)
        if plate_acq_id is None:
            plate_acq_id = self.insert_plate_acq(img)
        return plate_acq_id

    def image_exists_in_db(self, img: Image) -> bool:
        """
        Checks whether the image exists in the 'images' table based on its path.
        """
        query = "SELECT EXISTS (SELECT 1 FROM images WHERE path = %s)"
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, [img.get_path()])
                exists_flag = cursor.fetchone()[0]
            return exists_flag
        except Exception as err:
            logging.exception("Error checking if image exists in the database")
            raise err
        finally:
            self.release_connection(conn)

    def select_finished_plate_acq_folder(self) -> List[str]:
        """
        Returns a list of folders from plate_acquisition where finished is not null.
        """
        query = "SELECT folder FROM plate_acquisition WHERE finished IS NOT NULL"
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [row["folder"] for row in results]
        except Exception as err:
            logging.exception("Error selecting finished plate acquisition folders")
            raise err
        finally:
            self.release_connection(conn)

    def select_unfinished_plate_acq_folder(self) -> List[str]:
        """
        Returns a list of folders from plate_acquisition where finished is null.
        """
        query = "SELECT folder FROM plate_acquisition WHERE finished IS NULL"
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [row["folder"] for row in results]
        except Exception as err:
            logging.exception("Error selecting unfinished plate acquisition folders")
            raise err
        finally:
            self.release_connection(conn)

    def update_acquisition_finished(self, folder: str, timestamp: float) -> None:
        """
        Updates the 'finished' timestamp for a given folder in the plate_acquisition table.
        """
        query = """
            UPDATE plate_acquisition
            SET finished = %s
            WHERE folder = %s
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (datetime.utcfromtimestamp(timestamp), folder))
                if cursor.rowcount != 1:
                    raise Exception("Update did not affect exactly one row.")
            conn.commit()
        except Exception as err:
            logging.exception("Error updating acquisition finished timestamp")
            conn.rollback()
            raise err
        finally:
            self.release_connection(conn)

    def delete_image_meta_from_table_images(self, img: Image) -> None:
        """
        This method is for convenience when testing and deleting a test image
        """
        query = """
            DELETE FROM images
            WHERE path = %s
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, [img.get_path()])
            conn.commit()
        except Exception as err:
            logging.exception("Error deleting image metadata from images table.")
            conn.rollback()
            raise err
        finally:
            self.release_connection(conn)
