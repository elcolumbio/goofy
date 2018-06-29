#!/usr/bin/env python

"""Just for convenience we put the yaml reader and writer here."""

from ruamel.yaml import YAML

yaml = YAML(typ='safe')
yaml.default_flow_style = False


def read(filepath):
    with open(filepath, 'r') as f:
        configs = yaml.load(f)
    return configs


def write(filepath, data):
    with open(filepath, 'w') as f:
        yaml.dump(data, f)
