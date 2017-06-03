# -*- coding: utf-8 -*-
"""
Automatically syn sequence assets to shots.
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
        'Shotgun_Sequence_Change': ["assets"],
    }
    script_name = conf_parser.parse("shotgun_scripts", "script_name")
    key = conf_parser.parse("shotgun_scripts", "key")
    reg.registerCallback(script_name, key, synSequenceAssets, matchEvents, None)


def synSequenceAssets(sg, logger, event, args):
    meta_data = event['meta']
    if not meta_data["added"]:
        return
    # get added assets
    added_assets = meta_data["added"]
    added_assets = [{"type": "Asset", "id": asset["id"], "name": asset["name"]} for asset in added_assets]
    # get current episode
    filters = [["id", "is", meta_data["entity_id"]]]
    fields = ["shots"]
    current_sequence = sg.find_one("Sequence", filters, fields)
    # get sequences linked to this episode
    shots = current_sequence["shots"]
    if not shots:
        logger.info("No shot link to this sequence")
        return
    # add assets to these sequences
    for shot in shots:
        shot_info = sg.find_one("Shot", [["id", "is", shot["id"]]], ["assets"])
        assets_of_shot = shot_info["assets"]
        union_assets = union_list.union_list(assets_of_shot, added_assets)
        sg.update("Shot", shot["id"], {"assets": union_assets})
        logger.info("Update shot[id=%s] assets done." % shot["id"])
