import pytest

from prefix import Prefix

def test_constructor_ok():
    _prefix = Prefix("0.0.0.0/0")
    _prefix = Prefix("128.0.0.0/1")
    _prefix = Prefix("1.0.0.0/8")
    _prefix = Prefix("1.2.0.0/16")
    _prefix = Prefix("1.2.3.0/24")
    _prefix = Prefix("1.2.3.0/32")

def test_constructor_error():
    with pytest.raises(Exception):
        _prefix = Prefix("blah")
        _prefix = Prefix("1.2.3.4")
        _prefix = Prefix("1.2.3.4/99")
        _prefix = Prefix("1.2.3.4/16")

def test_repr():
    prefix = Prefix("1.2.0.0/16")
    assert str(prefix) == "1.2.0.0/16"
