from prefix import Prefix

import pytest

def test_constructor_ok():
    prefix = Prefix("0.0.0.0/0")
    prefix = Prefix("128.0.0.0/1")
    prefix = Prefix("1.0.0.0/8")
    prefix = Prefix("1.2.0.0/16")
    prefix = Prefix("1.2.3.0/24")
    prefix = Prefix("1.2.3.0/32")

def test_constructor_error():
    with pytest.raises(Exception):
        prefix = Prefix("blah")
        prefix = Prefix("1.2.3.4")
        prefix = Prefix("1.2.3.4/99")
        prefix = Prefix("1.2.3.4/16")

def test_repr():
    prefix = Prefix("1.2.0.0/16")
    assert prefix.__repr__() == "1.2.0.0/16"
