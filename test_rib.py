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
    assert str(rib) == ("3.3.0.0/16 -> nh1, ~nh2, nh3, ~nh4\n"
                        "4.0.0.0/8 -> nh1, nh3\n"
                        "4.1.1.0/24 -> ~nh1\n")

def test_del_route():
    fib = Fib()
    rib = Rib(fib)
    rib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    rib.put_route("5.5.0.0/16", ["nh3", "nh4"])
    rib.del_route("4.0.0.0/8")
    rib.del_route("3.0.0.0/8")
    assert str(rib) == ("5.5.0.0/16 -> nh3, nh4\n")

def test_get_route():
    fib = Fib()
    rib = Rib(fib)
    rib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    assert str(rib.get_route("4.0.0.0/8")) == "4.0.0.0/8 -> nh1, nh2"
    assert rib.get_route("3.0.0.0/8") is None

def test_get_repr():
    fib = Fib()
    rib = Rib(fib)
    rib.put_route("2.0.0.0/8", ["nh1", "nh2"])
    rib.put_route("2.2.2.0/24", ["nh1", "nh3"], ["nh4", "nh2"])
    rib.put_route("1.1.1.1/32", [], ["nh1"])
    rib.put_route("2.2.1.0/24", ["nh1", "nh3"])
    assert str(rib) == ("1.1.1.1/32 -> ~nh1\n"
                        "2.0.0.0/8 -> nh1, nh2\n"
                        "2.2.1.0/24 -> nh1, nh3\n"
                        "2.2.2.0/24 -> nh1, ~nh2, nh3, ~nh4\n")

# The "prop" test cases test the propagation of routes from the RIB to the FIB, translating
# negative nexthops in parent routes into complementary positive nexthops in child routes.

def test_prop_one_route_pos():

    # Add a single route with only positive next-hops

    fib = Fib()
    rib = Rib(fib)

    # Install one route into the RIB:
    rib.put_route("1.2.3.0/24", ["nh1", "nh2"])     # A single route, positive nexthops

    # The RIB must contain the following route:
    assert str(rib) == ("1.2.3.0/24 -> nh1, nh2\n")

    # The FIB must contain the following route:
    assert str(fib) == ("1.2.3.0/24 -> nh1, nh2\n")

    # Delete the route from the RIB.
    rib.del_route("1.2.3.0/24")

    # The RIB must be empty.
    assert str(rib) == ("")

    # The FIB must be empty.
    assert str(fib) == ("")

def test_prop_parent_pos_child_pos():

    # Add a parent aggregate rioute and a child more specific route, each with only positive
    # next-hops.

    fib = Fib()
    rib = Rib(fib)

    # Install two routes into the RIB:
    rib.put_route("1.2.0.0/16", ["nh1", "nh2"])     # Parent aggregate route, positive nexthops
    rib.put_route("1.2.3.0/24", ["nh3", "nh4"])     # Child more specific route, positive nexthops

    # The RIB must contain the following routes:
    assert str(rib) == ("1.2.0.0/16 -> nh1, nh2\n"
                        "1.2.3.0/24 -> nh3, nh4\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("1.2.0.0/16 -> nh1, nh2\n"
                        "1.2.3.0/24 -> nh3, nh4\n")

    # Delete the parent route from the RIB.
    rib.del_route("1.2.0.0/16")
    assert str(rib) == "1.2.3.0/24 -> nh3, nh4\n"

    # The corresponding route should be deleted from the FIB.
    assert str(fib) == "1.2.3.0/24 -> nh3, nh4\n"

    # Delete the child route from the RIB.
    rib.del_route("1.2.3.0/24")

    # The RIB must be empty.
    assert str(rib) == ""

    # The FIB must be empty.
    assert str(fib) == ""

def test_prop_one_child():

    # Test slide 56 in Pascal's "negative disaggregation" presentation:
    # Add a parent aggregate with positive nexthops and one child with a negative nexthop.

    fib = Fib()
    rib = Rib(fib)

    # Install two routes into the RIB: one parent aggregate with four ECMP positive nexthops, and
    # one child more specific with one negative nexthop.
    rib.put_route("0.0.0.0/0", ["nh1", "nh2", "nh3", "nh4"])    # Parent default route
    rib.put_route("10.0.0.0/16", [], ["nh1"])                   # Child route with negative nexthop

    # The RIB must contain the following routes:
    assert str(rib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4\n"
                        "10.0.0.0/16 -> ~nh1\n")

    # The RIB must contain the following routes:
    assert str(fib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4\n"     # Parent route, same as RIB
                        "10.0.0.0/16 -> nh2, nh3, nh4\n")       # Child route, complementary nhs

    # Delete the parent route from the RIB.
    rib.del_route("0.0.0.0/0")

    # The RIB must contain the following routes:
    assert str(rib) == "10.0.0.0/16 -> ~nh1\n"

    # The FIB must contain the following routes:
    assert str(fib) == "10.0.0.0/16 -> \n"

    # Delete the child route from the RIB.
    rib.del_route("10.0.0.0/16")

    # The RIB must be empty.
    assert str(rib) == ""

    # The FIB must be empty.
    assert str(fib) == ""

def test_prop_two_children():

    # Test slide 57 in Pascal's "negative disaggregation" presentation:
    # Add a parent aggregate with positive nexthops and two children with negative nexthops.

    fib = Fib()
    rib = Rib(fib)

    # Install the following routes into the RIB:
    rib.put_route("0.0.0.0/0", ["nh1", "nh2", "nh3", "nh4"])    # Parent default route
    rib.put_route("10.0.0.0/16", [], ["nh1"])                   # First child route, negative nh
    rib.put_route("10.1.0.0/16", [], ["nh4"])                   # Second child route, negative nh

    # The RIB must contain the following routes:
    assert str(rib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4\n"
                        "10.0.0.0/16 -> ~nh1\n"
                        "10.1.0.0/16 -> ~nh4\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4\n"
                        "10.0.0.0/16 -> nh2, nh3, nh4\n"
                        "10.1.0.0/16 -> nh1, nh2, nh3\n")

    # Delete the parent route from the RIB.
    rib.del_route("0.0.0.0/0")

    # The RIB must contain the following routes:
    assert str(rib) == ("10.0.0.0/16 -> ~nh1\n"
                        "10.1.0.0/16 -> ~nh4\n")

    # The FIB must contain the following routes (note: no nexthops, so discard routes):
    assert str(fib) == ("10.0.0.0/16 -> \n"
                        "10.1.0.0/16 -> \n")

    # Delete both remaining child routes from the RIB.
    rib.del_route("10.0.0.0/16")
    rib.del_route("10.1.0.0/16")

    # The RIB must be empty.
    assert str(rib) == ""

    # The FIB must be empty.
    assert str(fib) == ""

def test_prop_delete_nexthop_one_level():

    # Test slide 58 in Pascal's "negative disaggregation" presentation.
    # Delete a nexthop from a parent route, and check that the computed complementary nexthops in
    # the child routes are properly updated.

    fib = Fib()
    rib = Rib(fib)

    # Install the following three routes into the RIB:
    rib.put_route("0.0.0.0/0", ["nh1", "nh2", "nh3", "nh4"])    # Parent default route
    rib.put_route("10.0.0.0/16", [], ["nh1"])                   # First child, negative nexthop
    rib.put_route("10.1.0.0/16", [], ["nh4"])                   # Second child, negative nexthop

    # The RIB must contain the following routes:
    assert str(rib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4\n"
                        "10.0.0.0/16 -> ~nh1\n"
                        "10.1.0.0/16 -> ~nh4\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4\n"
                        "10.0.0.0/16 -> nh2, nh3, nh4\n"
                        "10.1.0.0/16 -> nh1, nh2, nh3\n")

    # Delete nexthop nh2 from the parent route 0.0.0.0/0 (by replacing the route with a new one
    # that has the reduced set of nexthops).
    rib.put_route("0.0.0.0/0", ["nh1", "nh3", "nh4"])

    # The RIB must contain the following routes:
    assert str(rib) == ("0.0.0.0/0 -> nh1, nh3, nh4\n"      # nh2 is gone
                        "10.0.0.0/16 -> ~nh1\n"
                        "10.1.0.0/16 -> ~nh4\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("0.0.0.0/0 -> nh1, nh3, nh4\n"      # nh2 is gone
                        "10.0.0.0/16 -> nh3, nh4\n"         # computed nh2 is gone
                        "10.1.0.0/16 -> nh1, nh3\n")        # computed nh2 is gone

    # Delete all routes from the RIB.
    rib.del_route("0.0.0.0/0")
    rib.del_route("10.0.0.0/16")
    rib.del_route("10.1.0.0/16")

    # The RIB must be empty.
    assert str(rib) == ""

    # The FIB must be empty.
    assert str(fib) == ""

def test_prop_delete_nexthop_two_levels():

    # Test slides 59 and 60 in Pascal's "negative disaggregation" presentation.
    # Delete a nexthop from a parent route, and check that the computed complementary nexthops in
    # the child route and the grandchild route.

    fib = Fib()
    rib = Rib(fib)

    # Install the following three routes into the RIB:
    rib.put_route("0.0.0.0/0", ["nh1", "nh2", "nh3", "nh4"])    # Parent default route
    rib.put_route("10.0.0.0/16", [], ["nh1"])                   # Child, negative nexthop
    rib.put_route("10.0.10.0/24", [], ["nh2"])                  # Grandchild, negative nexthop

    # The RIB must contain the following routes:
    assert str(rib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4\n"
                        "10.0.0.0/16 -> ~nh1\n"
                        "10.0.10.0/24 -> ~nh2\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4\n"
                        "10.0.0.0/16 -> nh2, nh3, nh4\n"
                        "10.0.10.0/24 -> nh3, nh4\n")

    # Delete nexthop nh3 from the parent route 0.0.0.0/0 (by replacing the route with a new one
    # that has the reduced set of nexthops).
    rib.put_route("0.0.0.0/0", ["nh1", "nh2", "nh4"])

    # The RIB must contain the following routes:
    assert str(rib) == ("0.0.0.0/0 -> nh1, nh2, nh4\n"      # nh3 is gone
                        "10.0.0.0/16 -> ~nh1\n"
                        "10.0.10.0/24 -> ~nh2\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("0.0.0.0/0 -> nh1, nh2, nh4\n"      # nh3 is gone
                        "10.0.0.0/16 -> nh2, nh4\n"         # computed nh3 is gone
                        "10.0.10.0/24 -> nh4\n")            # computed nh3 is gone

    # Delete all routes from the RIB.
    rib.del_route("0.0.0.0/0")
    rib.del_route("10.0.0.0/16")
    rib.del_route("10.0.10.0/24")

    # The RIB must be empty.
    assert str(rib) == ""

    # The FIB must be empty.
    assert str(fib) == ""

def test_prop_multiple_negative():

    # Child routes have multiple negative nexthops.

    fib = Fib()
    rib = Rib(fib)

    # Install the following three routes into the RIB:
    rib.put_route("1.0.0.0/8", ["nh1", "nh2", "nh3", "nh4"])  # Parent aggregate route
    rib.put_route("1.1.0.0/16", [], ["nh1", "nh2"])           # Child, 2 negative nexthops
    rib.put_route("1.1.1.0/24", [], ["nh2", "nh3"])           # Grandchild, 2 negative nexthops

    # The RIB must contain the following routes:
    assert str(rib) == ("1.0.0.0/8 -> nh1, nh2, nh3, nh4\n"
                        "1.1.0.0/16 -> ~nh1, ~nh2\n"
                        "1.1.1.0/24 -> ~nh2, ~nh3\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("1.0.0.0/8 -> nh1, nh2, nh3, nh4\n"
                        "1.1.0.0/16 -> nh3, nh4\n"
                        "1.1.1.0/24 -> nh4\n")

    # Delete nexthop nh3 from the parent route 1.0.0.0/8 (by replacing the route with a new one
    # that has the reduced set of nexthops).
    rib.put_route("1.0.0.0/8", ["nh1", "nh2", "nh4"])

    # The RIB must contain the following routes:
    assert str(rib) == ("1.0.0.0/8 -> nh1, nh2, nh4\n"      # nh3 is gone
                        "1.1.0.0/16 -> ~nh1, ~nh2\n"
                        "1.1.1.0/24 -> ~nh2, ~nh3\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("1.0.0.0/8 -> nh1, nh2, nh4\n"      # nh3 is gone
                        "1.1.0.0/16 -> nh4\n"               # computed nh3 is gone
                        "1.1.1.0/24 -> nh4\n")              # nothing changed (did not have nh3)

    # Delete all routes from the RIB.
    rib.del_route("1.0.0.0/8")
    rib.del_route("1.1.0.0/16")
    rib.del_route("1.1.1.0/24")

    # The RIB must be empty.
    assert str(rib) == ""

    # The FIB must be empty.
    assert str(fib) == ""

def test_prop_mix_positive_negative():

    # Child routes have mixture of positive and negative nexthops

    fib = Fib()
    rib = Rib(fib)

    # Install the following three routes into the RIB:
    rib.put_route("1.0.0.0/8", ["nh1", "nh2", "nh3"])    # Parent aggregate route
    rib.put_route("1.1.0.0/16", ["nh4"], ["nh1"])        # Child, positive and negative nexthop
    rib.put_route("1.1.1.0/24", ["nh5"], ["nh2"])        # Grandchild, positive and negative nexthop

    # The RIB must contain the following routes:
    assert str(rib) == ("1.0.0.0/8 -> nh1, nh2, nh3\n"
                        "1.1.0.0/16 -> ~nh1, nh4\n"
                        "1.1.1.0/24 -> ~nh2, nh5\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("1.0.0.0/8 -> nh1, nh2, nh3\n"
                        "1.1.0.0/16 -> nh2, nh3, nh4\n"
                        "1.1.1.0/24 -> nh3, nh4, nh5\n")

    # Delete nexthop nh3 from the parent route 1.0.0.0/8 (by replacing the route with a new one
    # that has the reduced set of nexthops).
    rib.put_route("1.0.0.0/8", ["nh1", "nh2"])

    # The RIB must contain the following routes:
    assert str(rib) == ("1.0.0.0/8 -> nh1, nh2\n"           # nh3 is gone
                        "1.1.0.0/16 -> ~nh1, nh4\n"
                        "1.1.1.0/24 -> ~nh2, nh5\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("1.0.0.0/8 -> nh1, nh2\n"           # nh3 is gone
                        "1.1.0.0/16 -> nh2, nh4\n"          # computed nh3 is gone
                        "1.1.1.0/24 -> nh4, nh5\n")         # computed nh3 is gone

    # Delete all routes from the RIB.
    rib.del_route("1.0.0.0/8")
    rib.del_route("1.1.0.0/16")
    rib.del_route("1.1.1.0/24")

    # The RIB must be empty.
    assert str(rib) == ""

    # The FIB must be empty.
    assert str(fib) == ""

def test_prop_deep_nesting():

    # Deep nesting of more specific routes: parent, child, grand child, grand-grand child, ...

    fib = Fib()
    rib = Rib(fib)

    # Install the following three routes into the RIB:
    rib.put_route("0.0.0.0/0", ["nh1", "nh2", "nh3", "nh4", "nh5"]) # Parent
    rib.put_route("1.0.0.0/8", [], ["nh1"])                         # Child
    rib.put_route("1.128.0.0/9", [], ["nh2"])                       # Grand child
    rib.put_route("1.192.0.0/10", [], ["nh3"])                      # Grand-grand child
    rib.put_route("1.224.0.0/11", [], ["nh4"])                      # Grand-grand-grand child
    rib.put_route("1.240.0.0/12", [], ["nh5"])                      # Grand-grand-grand-grand child

    # The RIB must contain the following routes:
    assert str(rib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4, nh5\n"
                        "1.0.0.0/8 -> ~nh1\n"
                        "1.128.0.0/9 -> ~nh2\n"
                        "1.192.0.0/10 -> ~nh3\n"
                        "1.224.0.0/11 -> ~nh4\n"
                        "1.240.0.0/12 -> ~nh5\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("0.0.0.0/0 -> nh1, nh2, nh3, nh4, nh5\n"
                        "1.0.0.0/8 -> nh2, nh3, nh4, nh5\n"
                        "1.128.0.0/9 -> nh3, nh4, nh5\n"
                        "1.192.0.0/10 -> nh4, nh5\n"
                        "1.224.0.0/11 -> nh5\n"
                        "1.240.0.0/12 -> \n")

    # Delete nexthop nh3 from the parent route 0.0.0.0/0.
    rib.put_route("0.0.0.0/0", ["nh1", "nh2", "nh4", "nh5"])

    # The RIB must contain the following routes:
    assert str(rib) == ("0.0.0.0/0 -> nh1, nh2, nh4, nh5\n"
                        "1.0.0.0/8 -> ~nh1\n"
                        "1.128.0.0/9 -> ~nh2\n"
                        "1.192.0.0/10 -> ~nh3\n"
                        "1.224.0.0/11 -> ~nh4\n"
                        "1.240.0.0/12 -> ~nh5\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("0.0.0.0/0 -> nh1, nh2, nh4, nh5\n"
                        "1.0.0.0/8 -> nh2, nh4, nh5\n"
                        "1.128.0.0/9 -> nh4, nh5\n"
                        "1.192.0.0/10 -> nh4, nh5\n"
                        "1.224.0.0/11 -> nh5\n"
                        "1.240.0.0/12 -> \n")

    # Delete all routes from the RIB.
    rib.del_route("0.0.0.0/0")
    rib.del_route("1.0.0.0/8")
    rib.del_route("1.128.0.0/9")
    rib.del_route("1.192.0.0/10")
    rib.del_route("1.224.0.0/11")
    rib.del_route("1.240.0.0/12")

    # The RIB must be empty.
    assert str(rib) == ""

    # The FIB must be empty.
    assert str(fib) == ""

def test_prop_nesting_with_siblings():

    # Deep nesting of more specific routes using the following tree:
    #
    #   1.0.0.0/8 -> nh1, nh2, nh3, nh4, nh5, nh6, nh7
    #    |
    #    +--- 1.1.0.0/16 -> ~nh1
    #    |     |
    #    |     +--- 1.1.1.0/24 -> ~nh2
    #    |     |
    #    |     +--- 1.1.2.0/24 -> ~nh3
    #    |
    #    +--- 1.2.0.0/16 -> ~nh4
    #          |
    #          +--- 1.2.1.0/24 -> ~nh5
    #          |
    #          +--- 1.2.2.0/24 -> ~nh6
    #
    # Note: we add the routes in a random order

    fib = Fib()
    rib = Rib(fib)

    # Install the following three routes into the RIB:
    rib.put_route("1.2.1.0/24", [], ["nh5"])
    rib.put_route("1.1.2.0/24", [], ["nh3"])
    rib.put_route("1.1.0.0/16", [], ["nh1"])
    rib.put_route("1.1.1.0/24", [], ["nh2"])
    rib.put_route("1.2.0.0/16", [], ["nh4"])
    rib.put_route("1.0.0.0/8", ["nh1", "nh2", "nh3", "nh4", "nh5", "nh6", "nh7"])
    rib.put_route("1.2.2.0/24", [], ["nh6"])

    # The RIB must contain the following routes:
    assert str(rib) == ("1.0.0.0/8 -> nh1, nh2, nh3, nh4, nh5, nh6, nh7\n"
                        "1.1.0.0/16 -> ~nh1\n"
                        "1.1.1.0/24 -> ~nh2\n"
                        "1.1.2.0/24 -> ~nh3\n"
                        "1.2.0.0/16 -> ~nh4\n"
                        "1.2.1.0/24 -> ~nh5\n"
                        "1.2.2.0/24 -> ~nh6\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("1.0.0.0/8 -> nh1, nh2, nh3, nh4, nh5, nh6, nh7\n"
                        "1.1.0.0/16 -> nh2, nh3, nh4, nh5, nh6, nh7\n"
                        "1.1.1.0/24 -> nh3, nh4, nh5, nh6, nh7\n"
                        "1.1.2.0/24 -> nh2, nh4, nh5, nh6, nh7\n"
                        "1.2.0.0/16 -> nh1, nh2, nh3, nh5, nh6, nh7\n"
                        "1.2.1.0/24 -> nh1, nh2, nh3, nh6, nh7\n"
                        "1.2.2.0/24 -> nh1, nh2, nh3, nh5, nh7\n")

    # Delete nexthop nh3 from the parent route 0.0.0.0/0.
    rib.put_route("1.0.0.0/8", ["nh1", "nh2", "nh4", "nh5", "nh6", "nh7"])

    # The RIB must contain the following routes:
    assert str(rib) == ("1.0.0.0/8 -> nh1, nh2, nh4, nh5, nh6, nh7\n"
                        "1.1.0.0/16 -> ~nh1\n"
                        "1.1.1.0/24 -> ~nh2\n"
                        "1.1.2.0/24 -> ~nh3\n"
                        "1.2.0.0/16 -> ~nh4\n"
                        "1.2.1.0/24 -> ~nh5\n"
                        "1.2.2.0/24 -> ~nh6\n")

    # The FIB must contain the following routes:
    assert str(fib) == ("1.0.0.0/8 -> nh1, nh2, nh4, nh5, nh6, nh7\n"
                        "1.1.0.0/16 -> nh2, nh4, nh5, nh6, nh7\n"
                        "1.1.1.0/24 -> nh4, nh5, nh6, nh7\n"
                        "1.1.2.0/24 -> nh2, nh4, nh5, nh6, nh7\n"
                        "1.2.0.0/16 -> nh1, nh2, nh5, nh6, nh7\n"
                        "1.2.1.0/24 -> nh1, nh2, nh6, nh7\n"
                        "1.2.2.0/24 -> nh1, nh2, nh5, nh7\n")

    # Delete all routes from the RIB.
    rib.del_route("1.0.0.0/8")
    rib.del_route("1.1.0.0/16")
    rib.del_route("1.1.1.0/24")
    rib.del_route("1.1.2.0/24")
    rib.del_route("1.2.0.0/16")
    rib.del_route("1.2.1.0/24")
    rib.del_route("1.2.2.0/24")

    # The RIB must be empty.
    assert str(rib) == ""

    # The FIB must be empty.
    assert str(fib) == ""
