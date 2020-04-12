from rib_route import RibRoute

from pytricia import PyTricia

class Rib:

    def __init__(self):
        # Since this prototype only support a single route per destination, we don't bother having
        # any Destination class.
        self._routes = PyTricia()

    def put_route(prefix, positive_nexthops, negative_nexthops):
        route = RibRoute(prefix, positive_next_hops, negative_next_hops)
        pytricia[prefix] = Route

    def del_route(prefix, positive_nexthops, negative_nexthops):
        route = RibRoute(prefix, positive_next_hops, negative_next_hops)
        pytricia[prefix] = Route

    def get_route(prefix)

    def dump(self):
        for prefix in self._routes:
            printf
