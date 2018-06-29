import requests

from . import configs


class EbayApi():
    def getnewusertoken():
        # this token is like 90mins valid
        url = "https://api.ebay.com/identity/v1/oauth2/token"
        response = requests.request(
            "POST", url,
            data=configs.payload.format(configs.unser_rf_token),
            headers=configs.headers)
        accesstoken = response.json()['access_token']
        return accesstoken

    def write_newusertoken(newtoken):
        configdata = configs.writetoconfig()
        configdata['api.ebay.com']['iaf_token'] = newtoken
        print(newtoken[-14:], configdata['api.ebay.com']['iaf_token'][
            -14:])
        configs.writetoconfig(configdata)
