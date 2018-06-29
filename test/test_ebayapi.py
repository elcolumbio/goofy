import pytest

from . import wrapper


class TestEbayAPI():
    def test_getaccess_token():
        # this is expansive since it actually calls for an accesstoken
        access_token = wrapper.UpdateToken().getnewusertoken()
        assert len(access_token) == 1916
        assert access_token.startswith('v^1.1#i^1#I^3#')
        assert isinstance(access_token, str)
