import unittest
import ast

from . import slackbot


class TestSlackBot(unittest.TestCase):
    def setUp(self):
        self.tomany = 'didnot expect the keyword you specified'
        self.tofew = 'did expect an additional keyword'
        self.maxDiff = None
        self.ignore1 = [{'type': 'hello'}]
        self.ignore2 = [{
            'type': 'user_typing', 'channel': 'CA098203C',
            'user': 'U6H990GGL'}]
        self.ignore3 = {
            'ok': True, 'reply_to': 0, 'ts': '1523551582.000468',
            'text': 'i am just a testbot'}
        self.notignore = {
            'type': 'message', 'user': 'U689KGGL', 'text': 'Goofy',
            'client_msg_id': '189c4422-699c-8989-bcac-4b6389898982',
            'team': 'T6H78988A', 'channel': 'CA898903C',
            'event_ts': '1523551582.000320', 'ts': '1523551582.000320'}

    def fakedict(self, text):
        """
        We are manipulating the text of a typical api dict.
        its like someone wrote a message with keywords.
        """
        self.notignore['text'] = text
        return slackbot.Listener.action1([self.notignore])

    def fakeignoredict(self, text):
        self.ignore3['text'] = text
        return slackbot.Listener.action1([self.ignore3])

    def ignore(self):
        self.assertEqual(slackbot.Listener.action1(self.ignore1), None)
        self.assertEqual(slackbot.Listener.action1(self.ignore2), None)

    def test_welcomemessage(self):
        expected_welcome = 'goofy welcomes you. \nfor help type: goofy help'
        self.assertEqual(self.fakedict('goofy'), expected_welcome)
        self.assertEqual(self.fakedict('   Goofy  '), expected_welcome)
        self.assertEqual(self.fakedict('GOofy  eLp fghd'), self.tomany)
        self.assertEqual(self.fakeignoredict('goofy'), None)

    def test_helpmessage(self):
        expected_help = slackbot.Brain().helpful()
        self.assertEqual(self.fakedict('goofy help'), expected_help)
        self.assertEqual(self.fakedict('GOofy    heLp'), expected_help)
        self.assertEqual(self.fakedict('GOofy heLp fghd'), self.tomany)
        self.assertEqual(self.fakeignoredict('goofy help'), None)

    def test_run(self):
        expected_help = slackbot.Brain().runy()
        self.assertEqual(self.fakedict('GOofy    RUn'), expected_help)
        self.assertEqual(self.fakedict('GOofy  Run fghd'), self.tomany)
        self.assertEqual(self.fakeignoredict('goofy help'), None)

    def test_word(self):
        start_words = ast.literal_eval(slackbot.Brain().getsublist())
        expected_subword = slackbot.Brain('golddigger').subword()
        expected_unsubword = slackbot.Brain('golddigger').unsubword()
        expected_failed_unsubword = slackbot.Brain('golddigger').unsubword()
        self.assertNotEqual(expected_unsubword, expected_failed_unsubword)
        self.assertEqual(self.fakedict(
            'goofy getsublist wowwdva'), self.tomany)

        self.assertEqual(self.fakedict(
            'goofy subword golddigger'), expected_subword)
        self.assertEqual(self.fakedict(
            'goofy UnsubwoRd GoLddigger'), expected_unsubword)
        self.assertEqual(self.fakedict(
            'GOofy    SUbword gOLddigger'), expected_subword)
        self.assertEqual(self.fakedict(
            'GOofy    unsubword GoLddigger'), expected_unsubword)
        self.assertEqual(self.fakedict(
            'GOofy    Subword'), self.tofew)
        self.assertEqual(self.fakedict(
            'GOofy    unsubword'), self.tofew)
        self.assertEqual(self.fakedict(
            'GOofy    unsubword GoLddigger'), expected_failed_unsubword)
        self.assertEqual(self.fakeignoredict('goofy subword'), None)
        end_words = ast.literal_eval(slackbot.Brain().getsublist())
        self.assertEqual(start_words, end_words)

    def test_whitelist(self):
        start_sentences = ast.literal_eval(slackbot.Brain().getwhitelist())
        expected_addwhitelist = slackbot.Brain(
            'klabauteeerrunde').addwhitelist()
        expected_remwhitelist = slackbot.Brain(
            'klabauteeerrunde').remwhitelist()
        expected_failed_remwhitelist = slackbot.Brain(
            'klabauteeerrunde').remwhitelist()
        self.assertEqual(self.fakedict(
            'goofy gewhitelist wowwdva'), self.tomany)

        self.assertEqual(self.fakedict(
            'goofy REmwhitelist   klABauteeerRunde'),
            expected_failed_remwhitelist)
        self.assertEqual(self.fakedict(
            'goofy addwhitelist klABauteeerrunde'), expected_addwhitelist)
        self.assertEqual(self.fakedict(
            ' goofy   REmwhitelist klABauteeerrunde '), expected_remwhitelist)
        self.assertEqual(self.fakedict(
            'GOofy    addWhitelist klabauteeerrundE'), expected_addwhitelist)
        self.assertEqual(self.fakedict(
            'goofy REmwhitelist   klABauteeerRunde'), expected_remwhitelist)
        self.assertEqual(self.fakedict(
            'GOofy    addwhitelist'), self.tofew)
        self.assertEqual(self.fakedict(
            'GOofy    remwhitelist'), self.tofew)
        end_sentences = ast.literal_eval(slackbot.Brain().getwhitelist())
        self.assertEqual(start_sentences, end_sentences)

    def test_quickrun(self):
        expected_help = slackbot.Brain('xyz').quickrun()
        self.assertEqual(self.fakedict(
            'goofy   quickrun Xyz'), expected_help)
        self.assertEqual(self.fakedict(
            'GOofy    QUICKRUN'), self.tofew)


if __name__ == '__main__':
    unittest.main()
