from rib import Rib
from fib import Fib

def test_constructor():
    fib = Fib()
    _rib = Rib(fib)

def test_put_route():
    fib = Fib()
    rib = Rib(fib)
    rib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    rib.put_route("3.3.0.0/16", ["nh1", "nh3"], ["nh4", "nh2"])
    rib.put_route("4.1.1.0/24", [], ["nh1"])
    rib.put_route("4.0.0.0/8", ["nh1", "nh3"])
    assert rib.__repr__() == ("3.3.0.0/16 -> nh1, ~nh2, nh3, ~nh4\n"
                              "4.0.0.0/8 -> nh1, nh3\n"
                              "4.1.1.0/24 -> ~nh1\n")

def test_del_route():
    fib = Fib()
    rib = Rib(fib)
    rib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    rib.put_route("5.5.0.0/16", ["nh3", "nh4"])
    rib.del_route("4.0.0.0/8")
    rib.del_route("3.0.0.0/8")
    assert rib.__repr__() == ("5.5.0.0/16 -> nh3, nh4\n")

def test_get_route():
    fib = Fib()
    rib = Rib(fib)
    rib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    assert rib.get_route("4.0.0.0/8").__repr__() == "4.0.0.0/8 -> nh1, nh2"
    assert rib.get_route("3.0.0.0/8") is None

def test_get_repr():
    fib = Fib()
    rib = Rib(fib)
    rib.put_route("2.0.0.0/8", ["nh1", "nh2"])
    rib.put_route("2.2.2.0/24", ["nh1", "nh3"], ["nh4", "nh2"])
    rib.put_route("1.1.1.1/32", [], ["nh1"])
    rib.put_route("2.2.1.0/24", ["nh1", "nh3"])
    assert rib.__repr__() == ("1.1.1.1/32 -> ~nh1\n"
                              "2.0.0.0/8 -> nh1, nh2\n"
                              "2.2.1.0/24 -> nh1, nh3\n"
                              "2.2.2.0/24 -> nh1, ~nh2, nh3, ~nh4\n")

# The "prop" test cases test the propagation of routes from the RIB to the FIB, translating
# negative nexthops in parent routes into complementary positive nexthops in child routes.

def test_prop_one_route_positive():

    fib = Fib()
    rib = Rib(fib)

    # Install a single route with only positive nexthops in the RIB:
    # 1.2.3.0/24 -> nh1, nh2
    rib.put_route("1.2.3.0/24", ["nh1", "nh2"])
    assert rib.__repr__() == ("1.2.3.0/24 -> nh1, nh2\n")

    # There should be a corresponding same route in the FIB:
    # 1.2.3.0/24 -> nh1, nh2
    assert fib.__repr__() == ("1.2.3.0/24 -> nh1, nh2\n")

    # Delete the route from the RIB.
    rib.del_route("1.2.3.0/24")
    assert rib.__repr__() == ("")

    # The corresponding route should be deleted from the FIB.
    assert fib.__repr__() == ("")

def test_prop_parent_child_routes_positive():

    fib = Fib()
    rib = Rib(fib)

    # Install two routes into the RIB: one parent aggregate and a child more specific route that
    # points to a different nexthop. We are only using positive nexthops.
    # 1.2.0.0/16 -> nh1, nh2
    # 1.2.3.0/24 -> nh3, nh4
    rib.put_route("1.2.0.0/16", ["nh1", "nh2"])
    rib.put_route("1.2.3.0/24", ["nh3", "nh4"])
    assert rib.__repr__() == ("1.2.0.0/16 -> nh1, nh2\n"
                              "1.2.3.0/24 -> nh3, nh4\n")

    # There should be the corresponding same routes in the FIB:
    # 1.2.0.0/16 -> nh1, nh2
    # 1.2.3.0/24 -> nh3, nh4
    assert fib.__repr__() == ("1.2.0.0/16 -> nh1, nh2\n"
                              "1.2.3.0/24 -> nh3, nh4\n")

    # Delete the parent route from the RIB.
    rib.del_route("1.2.0.0/16")
    assert rib.__repr__() == "1.2.3.0/24 -> nh3, nh4\n"

    # The corresponding route should be deleted from the FIB.
    assert fib.__repr__() == "1.2.3.0/24 -> nh3, nh4\n"

    # Delete the child route from the RIB.
    rib.del_route("1.2.3.0/24")
    assert rib.__repr__() == ""

    # The corresponding route should be deleted from the FIB.
    assert fib.__repr__() == ""
