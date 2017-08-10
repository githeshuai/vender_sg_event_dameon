# -*- coding: utf-8 -*-
"""
Automatically change task status when some status changed of version.
"""
import os
import sys

libs_dir = os.path.abspath(os.path.join(__file__, "..", "..", "event_libs")).replace("\\", "/")
if libs_dir not in sys.path:
    sys.path.insert(0, libs_dir)

import conf_parser


def registerCallbacks(reg):
    matchEvents = {
        'Shotgun_Version_Change': ["sg_status_list"],
    }
    script_name = conf_parser.parse("shotgun_scripts", "script_name")
    key = conf_parser.parse("shotgun_scripts", "key")
    reg.registerCallback(script_name, key, synTaskStatus, matchEvents, None)


def synTaskStatus(sg, logger, event, args):
    if 'new_value' not in event['meta']:
        return
    enable_version_status = conf_parser.parse("enable_version_status", "status")
    version_new_status = event["meta"]["new_value"]
    if version_new_status not in enable_version_status:
        return
    # lookup the version
    filters = [['id', 'is', event['entity']['id']]]
    fields = ["sg_task"]
    version_info = sg.find_one("Version", filters, fields)
    # get the linked task
    task_info = version_info["sg_task"]
    if task_info is None:
        logger.info("Current version does not link any task.")
        return
    # change the task status
    task_id = task_info["id"]
    task_new_status = enable_version_status.get(version_new_status)
    sg.update("Task", task_id, {"sg_status_list": task_new_status})
    logger.info("Change task[id=%s] status: %s" % (task_id, task_new_status))


if __name__ == "__main__":
    print conf_parser.parse("enable_version_status", "status")
