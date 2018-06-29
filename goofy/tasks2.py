#!/usr/bin/env python
# -*- coding: utf-8 -*-

import luigi
import os
from lxml import html
import pandas as pd

from . import configs
from . import yamlhandler


class CleanData(luigi.Task):
    """We iterate over each file in a folder and parse and extract data."""
    folder = f'{configs.datafolder}ebayapi/getitem/'

    def extractdata(self, file):
        response = yamlhandler.read(open(file))
        assert len(response) == 1
        response = response[0]
        itemspecifics = response['ItemSpecifics']['NameValueList']
        crunchspecifics = ''
        for feature in itemspecifics:
            crunchspecifics += '{} = {} ## '.format(
                feature['Name'], feature['Value'])

        descriptiontext = html.fromstring(response[
            'Description']).text_content()
        # we want to remove template text and html markup here later
        resultdict = {}
        resultdict['description'] = ' '.join(descriptiontext.split())
        resultdict['specifics'] = crunchspecifics[:-4]
        resultdict['title'] = response['Title']
        resultdict['itemid'] = response['ItemID']
        resultdict['date'] = file.split('_')[-1].replace('.yaml', '')
        resultdict['filename'] = file.split('/')[-1].replace('.yaml', '')
        return resultdict

    def output(self):
        return luigi.LocalTarget(
            f'{configs.datafolder}ebayapi/cleaned/getitem',
            format=luigi.format.Nop)

    def run(self):
        resultlist = []
        for _, _, files in os.walk(self.folder):
            for file in files:
                resultdict = self.extractdata(f'{self.folder}{file}')
                resultlist.append(resultdict)
        resultdf = pd.DataFrame(resultlist)
        with self.output().open('wb') as f:
            resultdf.to_msgpack(f)


if __name__ == '__main__':
    luigi.run()
