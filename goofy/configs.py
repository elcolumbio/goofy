#!/usr/bin/env python
"""
Mainly we set up the file environment.

We use two config files.
One were we put all credientals and userconfigs, thats confdata.
One were we track the last runtime of varios tasks, the path is taskinfo.
Since we overwrite the values, we have to care for the most recent data.
"""

import os
import datetime as dt

from . import yamlhandler

homedir = os.path.expanduser('~')

datafolder = yamlhandler.read(
    f'{homedir}/.config/ebayslack/configs.yaml')  # thats meta
path_to_config = f'{datafolder}/yaml/ebayslack.yaml'

if path_to_config is None:
    raise ValueError('path_to_config canot be empty')


confdata = yamlhandler.read(path_to_config)
taskinfo = f'{datafolder}/yaml/taskinfo.yaml'


def readconfig():
    """We always call this because we need to write the complete config."""
    return yamlhandler.read(path_to_config)


def writetoconfig(data):
    """We always call this because we need to write the complete config."""
    return yamlhandler.write(path_to_config, data)


def read_task_history():
    return yamlhandler.read(taskinfo)


def update_task_history(key, value):
    task_history = read_task_history()
    task_history[key] = value
    yamlhandler.write(taskinfo, task_history)


def getlastruntime(key):
    x = read_task_history().get(key, False)
    if x:
        return dt.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ")


# eBayAPI oauth2 credientals
unser_rf_token = confdata['oauth2']['unser_rf_token']
payload = confdata['oauth2']['payload']
headers = confdata['oauth2']['headers']

# SlackAPI credientals
slackcred = confdata['slackcred']

# Settings from the user
userconfigs = confdata['userconfigs']
