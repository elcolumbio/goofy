import pytest

from goofy import wrapper


def test_getaccess_token():
    # this is expansive since it actually calls for an accesstoken
    access_token = wrapper.UpdateToken.get_iaf_token()
    # assert len(access_token) == 1916
    assert access_token.startswith('v^1.1#i^1#I^3#')
    assert isinstance(access_token, str)
