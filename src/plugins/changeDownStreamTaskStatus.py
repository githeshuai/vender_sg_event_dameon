"""
Automatically  change the down stream task's status.
"""

import os
import sys

libs_dir = os.path.abspath(os.path.join(__file__, "..", "..", "event_libs")).replace("\\", "/")
if libs_dir not in sys.path:
    sys.path.insert(0, libs_dir)

import conf_parser


def registerCallbacks(reg):
    matchEvents = {
        'Shotgun_Task_Change': ["sg_status_list"],
    }
    script_name = conf_parser.parse("shotgun_scripts", "script_name")
    key = conf_parser.parse("shotgun_scripts", "key")
    
    reg.registerCallback(script_name, key, change_down_stream_task_status, matchEvents, None)


def change_down_stream_task_status(sg, logger, event, args):
    meta_data = event['meta']
    if meta_data["entity_type"] != "Task":
        return
    if meta_data["new_value"] != "cmpt":
        return
    # get the current task step
    task_id = meta_data["entity_id"]
    current_task_info = sg.find_one("Task", [["id", "is", task_id]], ["entity", "step.Step.short_name"])
    # get the down stream pipeline step through conf file
    entity = current_task_info["entity"]
    if not entity:
        return
    current_step = current_task_info["step.Step.short_name"]
    # if current step not in conf, warning
    down_stream_steps = get_down_stream_steps(current_step)
    if not down_stream_steps:
        return
    # get all the tasks of down stream step
    down_stream_tasks = get_task_of_step(sg, entity, down_stream_steps)
    # if task step is Omit, return
    for task in down_stream_tasks:
        task_status = task["sg_status_list"]
        if task_status in ["Omit"]:
            continue
        elif task_status in ["wtg"]:
            sg.update("Task", task["id"], {"sg_status_list": "rdy"})
            logger.info("Change task[%s] status to rdy" % task["id"])
        else:
            sg.update("Task", task["id"], {"sg_status_list": "rvs"})
            logger.info("Change task[%s] status to rev" % task["id"])


def get_down_stream_steps(current_step):
    down_stream_steps = conf_parser.parse("down_stream_step", current_step)
    return down_stream_steps


def get_task_of_step(sg, entity, steps):
    tasks = list()
    for step in steps:
        task = sg.find("Task", [["entity", "is", entity], ["step.Step.short_name", "is", step]], ["sg_status_list"])
        if not task:
            continue
        tasks.extend(task)
    return tasks
