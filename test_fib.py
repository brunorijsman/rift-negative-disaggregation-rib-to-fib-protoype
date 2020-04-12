from fib import Fib

def test_constructor():
    fib = Fib()

def test_put_route():
    fib = Fib()
    fib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    fib.put_route("4.1.0.0/16", ["nh3"])
    fib.put_route("4.0.0.0/8", ["nh1", "nh4"])
    assert fib.__repr__() == ("4.0.0.0/8 -> nh1, nh4\n"
                              "4.1.0.0/16 -> nh3\n")

def test_del_route():
    fib = Fib()
    fib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    fib.del_route("4.0.0.0/8")
    fib.del_route("3.0.0.0/8")
    assert fib.__repr__() == ("")

def test_get_route():
    fib = Fib()
    fib.put_route("4.0.0.0/8", ["nh1", "nh2"])
    assert fib.get_route("4.0.0.0/8").__repr__() == "4.0.0.0/8 -> nh1, nh2"
    assert fib.get_route("3.0.0.0/8") is None

def test_get_repr():
    fib = Fib()
    fib.put_route("2.0.0.0/8", ["nh1", "nh2"])
    fib.put_route("1.1.1.1/32", ["nh1"])
    fib.put_route("2.2.1.0/24", ["nh1", "nh3"])
    assert fib.__repr__() == ("1.1.1.1/32 -> nh1\n"
                              "2.0.0.0/8 -> nh1, nh2\n"
                              "2.2.1.0/24 -> nh1, nh3\n")
