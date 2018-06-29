import datetime as dt
import luigi
import requests

import ebaysdk.finding
import ebaysdk.trading
import ebaysdk.exception

from . import configs
from . import yamlhandler


class UpdateToken():
    """Get new iaftoken, a type of accesstoken and dump it in a yamlfile."""

    def get_iaf_token():
        """Token is like 90mins valid."""
        url = "https://api.ebay.com/identity/v1/oauth2/token"
        response = requests.request(
            "POST", url,
            data=configs.payload.format(configs.unser_rf_token),
            headers=configs.headers)
        accesstoken = response.json()['access_token']
        return accesstoken

    def dump_token(newtoken, ttype='iaf_token'):
        configdata = configs.readconfig()
        configdata['api.ebay.com'][ttype] = newtoken
        configs.writetoconfig(configdata)

    dump_token(get_iaf_token())


class ApiCallTemplate(luigi.Task):
    """
    Make the api call and stores the data from all pages.

    automatically updates every 90 mins accesstoken in /home/flo/ebay.yaml
    removes metadata
    """
    unnest_data = []

    def output(self):
        today = dt.datetime.today().strftime('%Y-%m-%d')
        return luigi.LocalTarget(
            f'{configs.datafolder}ebayapi/{self.foldername}{today}.yaml')

    def run(self):
        resultlist = []

        def set_con(apiname):
            if self.apiname == 'finding':
                api = ebaysdk.finding.Connection(
                    siteid='EBAY-DE', config_file=configs.path_to_config)
            elif self.apiname == 'trading':
                api = ebaysdk.trading.Connection(
                    config_file=configs.path_to_config)
            return api

        def unnest_dict(dataDict, mapList):
            for k in mapList:
                dataDict = dataDict[k]
            return dataDict

        try:
            api = set_con(self.apiname)
            response = api.execute(*self.api_query)
        except ebaysdk.exception.ConnectionError as e:
            print('|||| did set new iaft token')
            UpdateToken()
            api = set_con(self.apiname)
            response = api.execute(*self.api_query)
        ebaytime = response.get('Timestamp', None)

        while True:
            try:
                response = api.next_page().dict()
                result = unnest_dict(response, self.unnest_data)
                if isinstance(result, list):
                    resultlist += result
                else:
                    resultlist.append(result)
            except (ebaysdk.exception.PaginationLimit, AttributeError):
                break

        yamlhandler.write(self.output().path, resultlist)
        configs.update_task_history(self.foldername, ebaytime)  # lastrun
