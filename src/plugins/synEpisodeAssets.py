"""
Automatically syn episode assets to sequences.
"""
import os
import sys

libs_dir = os.path.abspath(os.path.join(__file__, "..", "..", "event_libs")).replace("\\", "/")
if libs_dir not in sys.path:
    sys.path.insert(0, libs_dir)

import conf_parser
import union_list


def registerCallbacks(reg):
    matchEvents = {
        'Shotgun_Episode_Change': ["assets"],
    }
    script_name = conf_parser.parse("shotgun_scripts", "script_name")
    key = conf_parser.parse("shotgun_scripts", "key")
    reg.registerCallback(script_name, key, synEpisodeAssets, matchEvents, None)


def synEpisodeAssets(sg, logger, event, args):
    meta_data = event['meta']
    if not meta_data["added"]:
        return
    # get added assets
    added_assets = meta_data["added"]
    added_assets = [{"type": "Asset", "id": asset["id"], "name": asset["name"]} for asset in added_assets]
    # get current episode
    filters = [["id", "is", meta_data["entity_id"]]]
    fields = ["sequences"]
    current_episode = sg.find_one("Episode", filters, fields)
    # get sequences linked to this episode
    sequences = current_episode["sequences"]
    if not sequences:
        logger.warning("No sequence link to this episode")
        return
    # add assets to these sequences
    for sequence in sequences:
        sequence_info = sg.find_one("Sequence", [["id", "is", sequence["id"]]], ["assets"])
        assets_of_sequence = sequence_info["assets"]
        union_assets = union_list.union_list(assets_of_sequence, added_assets)
        sg.update("Sequence", sequence["id"], {"assets": union_assets})
        logger.info("Update sequence[id=%s] assets done." % sequence["id"])
