from fib_route import FibRoute

def test_constructor():
    _route = FibRoute("1.0.0.0/8", ["nh1", "nh2"])

def test_property_prefix():
    route = FibRoute("1.0.0.0/8", ["nh1", "nh2"])
    assert route.prefix == "1.0.0.0/8"

def test_str():
    route = FibRoute("1.0.0.0/8", ["nh2", "nh1"])
    assert str(route) == "1.0.0.0/8 -> nh1, nh2"
    route = FibRoute("0.0.0.0/0", [])
    assert str(route) == "0.0.0.0/0 -> "
