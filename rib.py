from rib_route import RibRoute

from pytricia import PyTricia

class Rib:

    def __init__(self, fib):
        self._fib = fib
        # Since this prototype only support a single route per destination, we don't bother having
        # any Destination class.
        self._routes = PyTricia()

    def put_route(self, prefix, positive_nexthops, negative_nexthops=None):
        if negative_nexthops is None:
            negative_nexthops = []
        route = RibRoute(prefix, positive_nexthops, negative_nexthops)
        self._routes[prefix] = route

    def del_route(self, prefix):
        if self._routes.has_key(prefix):
            del self._routes[prefix]

    def get_route(self, prefix):
        if self._routes.has_key(prefix):
            return self._routes[prefix]
        else:
            return None

    def __repr__(self):
        str = ""
        for prefix in self._routes:
            str +=  f"{self._routes[prefix]}\n"
        return str
