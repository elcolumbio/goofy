from slackclient import SlackClient
from time import sleep
import datetime as dt

from . import configs


class SlackDelete():
    """Delete all messages in a channel."""

    def __init__(self, channel, latestday=dt.datetime.now()):
        self.legacy_token = configs.confdata['slackcred']['legacy_token']
        self.channel = channel
        self.latestday = latestday
        self.main()

    def main(self):
        timeback = dt.timedelta(days=0)
        #  timeback optional only delete older messages
        latest_ts = dt.datetime.timestamp(self.latestday-timeback)

        while True:
            sc = SlackClient(self.legacy_token)
            response = sc.api_call(
                'channels.history', channel=self.channel, count=1000,
                latest=latest_ts)
            allmsgs = [item['ts'] for item in response['messages']]
            print(len(allmsgs))
            for msg in allmsgs:
                sc.api_call('chat.delete', channel=self.channel, ts=msg)
                sleep(1)
            if not response['has_more']:
                break
