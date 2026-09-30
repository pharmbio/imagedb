"""
Resolve a channel_map_id from a set of microscope channel names, using the
channel_map table as the source of truth.

Adding a channel map then means inserting rows into channel_map -- no editing a
hard-coded dict and no rebuilding the container image.

The lookup is read once and kept for the life of the process. Channel maps
change rarely, and re-reading on a timer means a map inserted (or half inserted)
while a poll is running could change the answer mid-import. Restart to pick up
newly inserted channel maps.
"""

import logging
import threading


class ChannelMapUnavailable(Exception):
    """
    The channel_map table could not be read.

    Raised rather than falling back to a guess: no image can be imported without
    the database anyway, and a guessed channel_map_id is written to
    plate_acquisition on insert and never corrected afterwards.
    """


__lock = threading.Lock()
__cache = None          # {frozenset(channel_name, ...): map_id}


def __build_lookup(rows):
    """rows: [(map_id, [channel_name, ...]), ...] -> {frozenset(names): map_id}"""
    lookup = {}
    for map_id, names in sorted(rows):
        if not names:
            continue

        # A single missing channel_name makes the whole map unidentifiable: the
        # remaining names would match a config.json that has an extra channel.
        # The query filters these out already; enforced here too so the rule
        # does not depend on the SQL.
        if any(name is None for name in names):
            logging.warning(
                "channel_map %s has %s channel(s) without a channel_name; "
                "skipping it in the channel-name lookup",
                map_id, sum(1 for n in names if n is None))
            continue

        key = frozenset(names)

        # A map whose channel names repeat cannot be identified by its name set,
        # because the set is smaller than the channel list it came from.
        if len(key) != len(names):
            logging.warning(
                "channel_map %s has duplicate channel_name values %s; "
                "skipping it in the channel-name lookup", map_id, sorted(names))
            continue

        # Two maps sharing a channel-name set are indistinguishable from a
        # config.json. Keep the lowest map_id so the result is at least stable.
        if key in lookup:
            logging.warning(
                "channel_map %s has the same channel names as channel_map %s; "
                "using %s. Give them distinct channel names to disambiguate.",
                map_id, lookup[key], lookup[key])
            continue

        lookup[key] = map_id

    return lookup


def __load():
    """Read channel_map from the database. Raises ChannelMapUnavailable."""
    try:
        # Imported lazily: the filename parsers must stay importable (and unit
        # testable) without settings.py or a database being present.
        from database import Database

        rows = Database.get_instance().select_channel_map_channel_names()
    except Exception as err:
        raise ChannelMapUnavailable(
            "could not read channel_map from the database") from err

    return __build_lookup(rows)


def get_lookup(force_refresh=False):
    """
    The {frozenset(channel_names): map_id} lookup.

    Held for the life of the process once loaded; restart to pick up channel
    maps inserted since. Raises ChannelMapUnavailable if it cannot be read.
    """
    global __cache

    with __lock:
        if __cache is None or force_refresh:
            __cache = __load()
            logging.info(
                "channel_map lookup loaded from database: %s maps "
                "(kept until restart)", len(__cache))

        return __cache


def get_channel_map_id(channel_names):
    """
    map_id for these channel names, or None if no map in the database matches.

    Raises ChannelMapUnavailable if the channel_map table cannot be read.
    """
    return get_lookup().get(frozenset(channel_names))
