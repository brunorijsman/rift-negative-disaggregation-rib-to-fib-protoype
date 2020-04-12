from rib import Rib

def test_constructor():
    rib = Rib()

def test_put_route():
    rib = Rib()
    rib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    rib.put_route("3.3.0.0/16", ["nh1", "nh3"], ["nh4", "nh2"])
    rib.put_route("4.1.1.0/24", [], ["nh1"])
    rib.put_route("4.0.0.0/8", ["nh1", "nh3"])
    assert rib.__repr__() == ("3.3.0.0/16 -> nh1, ~nh2, nh3, ~nh4\n"
                              "4.0.0.0/8 -> nh1, nh3\n"
                              "4.1.1.0/24 -> ~nh1\n")

def test_del_route():
    rib = Rib()
    rib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    rib.del_route("4.0.0.0/8")
    rib.del_route("3.0.0.0/8")
    assert rib.__repr__() == ("")

def test_get_route():
    rib = Rib()
    rib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    assert rib.get_route("4.0.0.0/8").__repr__() == "4.0.0.0/8 -> nh1, nh2"
    assert rib.get_route("3.0.0.0/8") is None

def test_get_repr():
    rib = Rib()
    rib.put_route("2.0.0.0/8", ["nh1", "nh2"])
    rib.put_route("2.2.2.0/24", ["nh1", "nh3"], ["nh4", "nh2"])
    rib.put_route("1.1.1.1/32", [], ["nh1"])
    rib.put_route("2.2.1.0/24", ["nh1", "nh3"])
    assert rib.__repr__() == ("1.1.1.1/32 -> ~nh1\n"
                              "2.0.0.0/8 -> nh1, nh2\n"
                              "2.2.1.0/24 -> nh1, nh3\n"
                              "2.2.2.0/24 -> nh1, ~nh2, nh3, ~nh4\n")
