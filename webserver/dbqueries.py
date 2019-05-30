#!/usr/bin/env python3
import pymongo as pymongo
import logging
import json
import settings as imgdb_settings

def get_default_collection():
    dbclient = pymongo.MongoClient(username=imgdb_settings.DB_USER,
                                   password=imgdb_settings.DB_PASS,
                                   # connectTimeoutMS=500,
                                   serverSelectionTimeoutMS=1000,
                                   host=imgdb_settings.DB_HOSTNAME,
                                   port=imgdb_settings.DB_PORT
                                   )

    img_db = dbclient["pharmbio_db"]
    img_collection = img_db["pharmbio_microimages"]

    return img_collection


def list_plate(plate):

    img_collection = get_default_collection()

    find_plate = plate

    query = {"plate": find_plate}

    return_fields = {"plate": 1,
                     "timepoint": 1,
                     "path": 1,
                     "metadata.well": 1,
                     "metadata.wellsample": 1,
                     "metadata.channel": 1,
                     "_id": 0}

    sorting = ([("metadata.well", 1),
                ("metadata.wellsample", 1),
                ("metadata.channel", 1)])

    logging.info("query" + str(query))

    result = img_collection.find(query, return_fields).sort(sorting)

    resultlist = list(result)

    # Before returning (to web) delete the for user hidden "root part" IMAGES_ROOT_FOLDER part, e.g. /share/mikro/IMX.....
    for image in resultlist:
        for key, value in image.items():
            if key == "path":
                new_value = str(value).replace( imgdb_settings.IMAGES_ROOT_FOLDER , "")
                image.update( {'path': new_value})

    plates_dict = {}
    for image in resultlist:
        plates_dict.setdefault(image['plate'], {}) \
            .setdefault(image['timepoint'], {}) \
            .setdefault(image['metadata']['well'], {}) \
            .setdefault(image['metadata']['wellsample'], {}) \
            .setdefault(image['metadata']['channel'], image['path'])


    #plateObj = {'plate_name:', plate,
    #            'timepoints:', platesdict['plate']
    #            }

    return {'plates': plates_dict}

def list_plates(DB_HOSTNAME="image-mongo"):

    logging.debug("list_plates")

    img_collection = get_default_collection()

    # Selects distinct and sort
    result = img_collection.aggregate(
        [

            {"$group": {"_id": {"plate": "$plate",
                                "project": "$project"
                                }
                        }
             },
            {"$sort": {"_id.project": 1,
                       "_id.plate":1
                       }
             }

        ]
    )


    resultlist = list(result)

    #logging.debug(json.dumps(resultlist, indent=2))

    return resultlist