#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime as dt
from lxml import html
import re
import logging

from . import configs
from . import yamlhandler

logger = logging.getLogger(__name__)

getitemfolder = f'{configs.datafolder}ebayapi/getitem/'
active_listing = f'{configs.datafolder}ebayapi/listingsbyseller'


class EbayAlarm():
    def __init__(self, profile='standard'):
        self.profile = profile
        self.userconfigs = configs.configdata['userconfig']

    def run(self):
        def stripx(filename):
            """Strip filename to date."""
            return dt.datetime.strptime(
                filename.replace('.yaml', ''), '%Y-%m-%d')

        def get_recent(folder):
            # get freshest date per folder
            freshest = max(
                [stripx(filename) for filename in os.listdir(folder)])
            return freshest.strftime('%Y-%m-%d')+'.yaml'

        def get_freshest_data(getitemfolder):
            # get freshest date per folder
            freshfilesdict = dict()
            for filex in os.listdir(getitemfolder):
                itemid = filex.split('_')[0]
                rundate = dt.datetime.strptime(filex.split('_')[1].replace(
                    '.yaml', ''), '%Y-%m-%d')
                freshest = freshfilesdict.get(itemid, False)
                if freshest:
                    if rundate > freshest:
                        freshfilesdict[itemid] = rundate
                else:
                    freshfilesdict[itemid] = rundate
            return freshfilesdict

        def active_itemid_list(filex):
            aktiv = yamlhandler.read(filex)
            return [item['itemId'] for item in aktiv]

        def getitem_cleaner(file, response):
            assert len(response) == 1
            response = response[0]
            itemspecifics = response['ItemSpecifics']['NameValueList']
            crunchspecifics = ''
            for feature in itemspecifics:
                crunchspecifics += '{} = {} ## '.format(
                    feature['Name'], feature['Value'])

            descriptiontext = html.fromstring(response[
                'Description']).text_content()
            resultdict = {}
            resultdict['description'] = ' '.join(descriptiontext.split())
            resultdict['specifics'] = crunchspecifics[:-4]
            resultdict['title'] = response['Title']
            resultdict['itemid'] = response['ItemID']
            resultdict['date'] = file.split('_')[-1].replace('.yaml', '')
            resultdict['filename'] = file.split('/')[-1].replace('.yaml', '')
            return resultdict

        def whitelistcheck(trefferdict):
            whitelist = self.configdict['whitelist']
            kontext = trefferdict['hit'].lower().strip()
            whitelisted = False
            for whitelisting in whitelist:
                if kontext == whitelisting.lower().strip():
                    whitelisted = True
            return whitelisted

        def getitem_throwalert(file, cleaned, trefferliste, active_list):
            if self.profile == 'standard':
                subwords = self.configdict['sublist']
            else:
                subwords = self.configdict['quickrun']['sublist']
            prepattern = ''
            assert isinstance(subwords, list)
            if len(subwords) > 1:
                for subword in subwords[:-1]:
                    prepattern += '.{0,20}'+subword+'.{0,20} |'
            prepattern += '.{0,20}'+subwords[-1]+'.{0,20}'

            pattern = re.compile(prepattern, re.I)
            matches = pattern.finditer(str(cleaned))

            itemid = file.split('_')[0]
            for match in matches:
                title = cleaned['title']
                ebaylink = f' https://www.ebay.de/itm/{itemid}'
                hit = match.group(0)
                status = bool(itemid in active_list)
                if status:
                    sangebot = 'Angebot aktiv'
                else:
                    sangebot = 'Angebot inaktiv'

                trefferdict = dict()
                trefferdict['rundate'] = cleaned['date']
                trefferdict['hit'] = hit
                trefferdict['status'] = sangebot
                trefferdict['ebaylink'] = ebaylink
                trefferdict['title'] = title

                cond1 = not whitelistcheck(trefferdict)
                cond2 = self.profile == 'quickrun'
                if cond1 or cond2:
                    trefferliste.append(trefferdict)
            return trefferliste

        def main(self):
            recentfile = f'{active_listing}/{get_recent(active_listing)}'
            live_listings = list(set(active_itemid_list(recentfile)))
            freshfilesdict = get_freshest_data(getitemfolder)

            filelist = [
                f"{key}_{value.strftime('%Y-%m-%d')}.yaml"
                for key, value in freshfilesdict.items()]

            trefferliste = []
            for filex in os.listdir(getitemfolder):
                if filex in filelist:
                    response = yamlhandler.read(getitemfolder + filex)
                    cleaned = getitem_cleaner(filex, response)
                    trefferliste = getitem_throwalert(
                        filex, cleaned, trefferliste, live_listings)
            return trefferliste

        return main()
