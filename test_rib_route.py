from rib_route import RibRoute

def test_constructor():
    _route = RibRoute("1.0.0.0/8", ["nh1", "nh2"], ["nh3", "nh4"])

def test_property_prefix():
    route = RibRoute("1.0.0.0/8", ["nh1", "nh2"], ["nh3", "nh4"])
    assert route.prefix == "1.0.0.0/8"

def test_property_positive_nexthops():
    route = RibRoute("1.0.0.0/8", ["nh1", "nh2"], ["nh3", "nh4"])
    assert route.positive_nexthops == set(["nh1", "nh2"])

def test_property_negative_nexthops():
    route = RibRoute("1.0.0.0/8", ["nh1", "nh2"], ["nh3", "nh4"])
    assert route.positive_nexthops == set(["nh1", "nh2"])

def test_property_computed_nexthops():
    route = RibRoute("1.0.0.0/8", ["nh1", "nh2"], ["nh3", "nh4"])
    assert route.computed_nexthops is None

def test_set_computed_nexthops():
    route = RibRoute("1.0.0.0/8", ["nh1", "nh2"], ["nh3", "nh4"])
    assert route.computed_nexthops is None
    route.set_computed_nexthops(["n1", "nh2", "nh5", "nh6"])
    assert route.computed_nexthops == set(["n1", "nh2", "nh5", "nh6"])

def test_str():
    route = RibRoute("1.0.0.0/8", ["nh1", "nh2"], ["nh3", "nh4"])
    assert str(route) == "1.0.0.0/8 -> nh1, nh2, ~nh3, ~nh4"
    route = RibRoute("1.2.0.0/16", ["nh3", "nh1"], ["nh4", "nh2"])
    assert str(route) == "1.2.0.0/16 -> nh1, ~nh2, nh3, ~nh4"
    route = RibRoute("1.2.3.0/24", ["nh1"], [])
    assert str(route) == "1.2.3.0/24 -> nh1"
    route = RibRoute("1.2.3.4/32", [], ["nh1"])
    assert str(route) == "1.2.3.4/32 -> ~nh1"
    route = RibRoute("0.0.0.0/0", [], [])
    assert str(route) == "0.0.0.0/0 -> "
