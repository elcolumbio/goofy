from slackclient import SlackClient
import time
import logging

from .ebayalarm import EbayAlarm
from .slackdelete import SlackDelete
from . import configs

logger = logging.getLogger(__name__)


class Brain():
    def __init__(self, uservalues=None, channel=None):
        self.channel = channel
        self.uservalues = uservalues
        self.configdata = configs.readconfig()

    def messageformatting(self, item):
        hit = item['hit']
        livelisting = item['status']
        ebaylink = item['ebaylink']
        rundate = item['rundate']
        formatstring = f'''{livelisting}; \
        {hit}; {ebaylink} ; {rundate}'''
        return formatstring

    # those are the actions which are getting triggered

    def helpful(self):
        configs.readconfig()
        return self.configdata['helpmessage'].replace('\\n', '\n')

    def runy(self, profile='standard'):
        result = EbayAlarm(profile).run()
        if len(result) > 20:
            printtoslack = f'maximum 20 hits out of {len(result)} are shown\n'
        else:
            printtoslack = f'i found {len(result)} hits for you:\n'
            sublist = self.getsublist()
            whitelist = self.getwhitelist()
            printtoslack += f'subwords: {sublist}; whitelist: {whitelist}'
        for index, item in enumerate(result[:20]):
            item = self.messageformatting(item)
            printtoslack += f'*{index}*{item}\n\n'
            logger.debug(printtoslack)
        return printtoslack

    def subword(self):
        sublist = self.configdata['userconfig']['sublist']
        if not isinstance(sublist, list):
            sublist = list()
        sublist.append(self.uservalues)
        self.configdata['userconfig']['sublist'] = sublist
        configs.writetoconfig(self.configdata)
        return f'succesful added {self.uservalues} to your subs'

    def unsubword(self):
        sublist = self.configdata['userconfig']['sublist']
        try:
            sublist.remove(self.uservalues)
            response = f'succesful removed {self.uservalues} from your subs'
        except ValueError:   # we handle None userinput and wrong userinput
            response = f'unsuccesful {self.uservalues} not exists in your subs'
        self.configdata['userconfig']['sublist'] = sublist
        configs.writetoconfig(self.configdata)
        return response

    def addwhitelist(self):
        whitelist = self.configdata['userconfig']['whitelist']
        if not isinstance(whitelist, list):
            whitelist = list()
        whitelist.append(self.uservalues)
        self.configdata['userconfig']['whitelist'] = whitelist
        configs.writetoconfig(self.configdata)
        return f'succesful added {self.uservalues} to your whitelist'

    def remwhitelist(self):
        whitelist = self.configdata['userconfig']['whitelist']
        try:
            whitelist.remove(self.uservalues)
            response = f'succesful removed {self.uservalues} from whitelist'
        except ValueError:
            response = f'unsuccesful {self.uservalues} not exists in whitelist'
        self.configdata['userconfig']['whitelist'] = whitelist
        configs.writetoconfig(self.configdata)
        return response

    def getsublist(self):
        sublist = self.configdata['userconfig']['sublist']
        return f'{sublist}'

    def getwhitelist(self):
        whitelist = self.configdata['userconfig']['whitelist']
        return f'{whitelist}'

    def quickrun(self):
        subwords = list()
        subwords.append(self.uservalues)
        self.configdata['userconfig']['quickrun']['sublist'] = subwords
        configs.writetoconfig(self.configdata)
        result = EbayAlarm('quickrun').run()
        printtoslack = f'i found {len(result)} hits for word: \
        {self.uservalues}\n'
        for index, item in enumerate(result[:20]):
            item = self.messageformatting(item)
            printtoslack += f'*{index}*{item}\n\n'
        return printtoslack

    def delete(self):
        SlackDelete(self.channel)
        spam = f'deleted all messages,and i make a new one like this :)'
        sc.rtm_send_message(self.channel, spam)
        time.sleep(1)
        spam = f'i am sorry. Tough i am a bot sometimes i like to spam'
        return spam


class Listener():

    def check_userinput(nosecondargument, uservalues, pmessage):
        if uservalues == '' and not nosecondargument:
            message = 'did expect an additional keyword'
        elif uservalues != '' and nosecondargument:
            message = 'didnot expect the keyword you specified'
        else:
            message = pmessage
        return message

    def parseuserinput(argument, uservalues, channel):
        if argument == 'help' or argument == 'h':
            pmessage = Brain().helpful()
            return Listener.check_userinput(True, uservalues, pmessage)
        elif argument == 'run':
            pmessage = Brain().runy()
            return Listener.check_userinput(True, uservalues, pmessage)
        elif argument.startswith('subword'):
            pmessage = Brain(uservalues).subword()
            return Listener.check_userinput(False, uservalues, pmessage)
        elif argument.lower().startswith('unsubword'):
            pmessage = Brain(uservalues).unsubword()
            return Listener.check_userinput(False, uservalues, pmessage)
        elif argument.lower().startswith('addwhitelist'):
            pmessage = Brain(uservalues).addwhitelist()
            return Listener.check_userinput(False, uservalues, pmessage)
        elif argument.lower().startswith('remwhitelist'):
            pmessage = Brain(uservalues).remwhitelist()
            return Listener.check_userinput(False, uservalues, pmessage)
        elif argument.lower().startswith('getsublist'):
            pmessage = Brain().getsublist()
            return Listener.check_userinput(True, uservalues, pmessage)
        elif argument.lower().startswith('getwhitelist'):
            pmessage = Brain().getwhitelist()
            return Listener.check_userinput(True, uservalues, pmessage)
        elif argument.lower().startswith('quickrun'):
            pmessage = Brain(uservalues).quickrun()
            return Listener.check_userinput(False, uservalues, pmessage)
        elif argument.lower().startswith('delete'):
            pmessage = Brain(channel=channel).delete()
            return Listener.check_userinput(True, uservalues, pmessage)
        else:
            pmessage = 'goofy welcomes you. \nfor help type: goofy help'
            return Listener.check_userinput(True, uservalues, pmessage)

    def action1(listener):
        if len(listener) == 1:
            listener = listener[0]
            if listener.get('type', '') == 'message' and listener.get(
                    'subtype', '') == '':
                text = ' '.join(listener['text'].strip().lower().split())
                if text.startswith('goofy'):
                    channel = listener['channel']
                    argument = text[6:].split(' ')[0].strip()
                    try:
                        uservalues = ' '.join(text[6:].split(' ')[1:])
                    except IndexError:
                        uservalues = None  # no uservalues specified
                    return Listener.parseuserinput(
                        argument, uservalues, channel)

    def listening():
        if sc.rtm_connect():
            while sc.server.connected is True:
                listener = sc.rtm_read()
                response1 = Listener.action1(listener)
                if response1 is not None:
                    channel = listener[0]['channel']
                    sc.rtm_send_message(channel, response1)
                time.sleep(1)
        else:
            print("Connection Failed")


token = configs.readconfig()['slackcred']['bot_token']
channel = configs.readconfig()['slackcred']['bot_homechannel']
sc = SlackClient(token)

if __name__ == '__main__':
    Listener.listening()
