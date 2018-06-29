#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime as dt
import luigi

from .wrapper import ApiCallTemplate
from . import configs
from . import yamlhandler


class GetListingsBySeller(ApiCallTemplate):
    unnest_data = ['searchResult', 'item']
    foldername = 'listingsbyseller/'
    apiname = 'finding'
    api_query = ('findItemsIneBayStores', {'storeName': configs.configdata[
        'storeName']})


class GetSellerEvents(ApiCallTemplate):
    """
    https://developer.ebay.com/DevZone/guides/ebayfeatures/Development/Listings-ChangeTracking.html
    our timeinterval is 12 hours except it previously failed
    """
    foldername = 'sellerevents/'
    lastruntime = configs.getlastruntime(foldername)
    starttime = dt.datetime.utcnow()-dt.timedelta(hours=6, minutes=20)
    if lastruntime:  # False if never run before
        if lastruntime < starttime:
            starttime = lastruntime
    else:
        print('wow this task probably never run before')

    unnest_data = ['ItemArray', 'Item']
    apiname = 'trading'
    api_query = ('GetSellerEvents', {'ModTimeFrom': starttime})


class GetItem(ApiCallTemplate):
    # http://developer.ebay.com/devzone/xml/docs/reference/ebay/getitem.html
    itemid = luigi.Parameter()
    unnest_data = ['Item']
    foldername = f'getitem/{itemid}_'
    api_query = ('GetItem', {'ItemID': itemid,
                             'DetailLevel': 'ReturnAll',
                             'IncludeItemSpecifics': True})


class AllListings(luigi.WrapperTask):
    key = 'itemId'

    def requires(self):
        return GetListingsBySeller()

    def output(self):
        return None  # could make a marker file

    def run(self):
        itemidlist = []
        response = yamlhandler.read(self.input().path)
        for listing in response:
            itemidlist.append(listing[self.key])
        itemidlist = list(set(itemidlist))
        for item in itemidlist:
            yield GetItem(item)


class ChangedListings(luigi.WrapperTask):
    key = 'ItemID'

    def requires(self):
        return GetSellerEvents()

    def output(self):
        return None  # could make a marker file

    def run(self):
        itemidlist = []
        response = yamlhandler.read(open(self.input().path))
        for listing in response:
            itemidlist.append(listing[self.key])
        itemidlist = list(set(itemidlist))
        for item in itemidlist:
            yield GetItem(item)


if __name__ == '__main__':
    luigi.run()
