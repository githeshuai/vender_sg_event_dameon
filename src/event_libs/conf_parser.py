# -*- coding: utf-8 -*-
import os
import yaml


def get_conf_dir():
    conf_dir = os.path.abspath(os.path.join(__file__, "..", "..", "conf"))
    conf_dir = conf_dir.replace("\\", "/")
    return conf_dir


def parse(conf_file_name, key):
    conf_dir = get_conf_dir()
    conf_file = os.path.normpath(os.path.join(conf_dir, "%s.yml" % conf_file_name))
    if not os.path.isfile(conf_file):
        print "%s is not an exist file." % conf_file
        return
    with open(conf_file, "r") as f:
        conf_data = yaml.load(f)
    if not conf_data.__contains__(key):
        print "KeyError key[%s] not in the config file: %s." % (key, conf_file)
        return
    value = conf_data[key]
    return value


if __name__ == "__main__":
    print parse("shotgun_scripts", "script_name")
