#!/usr/bin/env python3
import pymongo as pymongo
import logging
import json

DB_USER = "root"
DB_PASS = "example"
DB_PORT = 27017

def get_default_collection(DB_HOSTNAME="image-mongo"):
    dbclient = pymongo.MongoClient("mongodb://%s:%s@%s:%s/" % (DB_USER, DB_PASS, DB_HOSTNAME, DB_PORT))
    dbclient = pymongo.MongoClient(username=DB_USER,
                                   password=DB_PASS,
                                   # connectTimeoutMS=500,
                                   serverSelectionTimeoutMS=1000,
                                   host=DB_HOSTNAME,
                                   port=DB_PORT
                                   )

    img_db = dbclient["pharmbio_db"]
    img_collection = img_db["pharmbio_microimages"]

    return img_collection


def list_plate(plate):

    img_collection = get_default_collection()

    find_plate = plate

    result = img_collection.find({"plate": find_plate},
                                 # this is what to return
                                 {"plate": 1,
                                  "timepoint": 1,
                                  "path": 1,
                                  "metadata.well": 1,
                                  "metadata.wellsample": 1,
                                  "metadata.channel": 1,
                                  "_id": 0}) \
                            .sort([("metadata.well", 1),
                                   ("metadata.wellsample", 1),
                                   ("metadata.channel", 1)])
    resultlist = list(result)

    #logging.debug(json.dumps(resultlist, indent=2))

    # When returning to web rewrite path
    for image in resultlist:
        for key, value in image.items():
            if key == "path":
                new_value = str(value).replace("share/mikro/IMX/MDC Polina Georgiev/", "")
                image.update( {'path': new_value})

    platesdict = {}
    for image in resultlist:
        platesdict.setdefault(image['plate'], {}) \
            .setdefault(image['timepoint'], {}) \
            .setdefault(image['metadata']['well'], {}) \
            .setdefault(image['metadata']['wellsample'], {}) \
            .setdefault(image['metadata']['channel'], image['path'])

# .setdefault({'channel_index': image['metadata']['channel'],
#             'path':image['path']})



    #logging.debug(json.dumps(platesdict, indent=2))

    return {'plates': platesdict}

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