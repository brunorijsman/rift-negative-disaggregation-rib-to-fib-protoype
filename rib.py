from pytricia import PyTricia   # pylint:disable=no-name-in-module

from rib_route import RibRoute

class Rib:

    def __init__(self, fib):
        self._fib = fib
        # 1. The real production code for the RIB (but not the FIB) needs Destination objects and
        # Route objects to support multiple routes to the same destination (prefix): one per owner
        # (e.g. south-SPF and north-SPF). This prototype only supports a single route per
        # destination (prefix) to keep things simple and avoid distracting attention from the
        # negative disaggregation algorithm.
        # 2. The PyTricia code takes prefixes as strings. Not sure if this is the best choice
        # for production code. I suspect it is better to accept prefixes as Prefix objects that
        # have an internal binary representation.
        self._routes = PyTricia()

    def put_route(self, prefix, positive_nexthops, negative_nexthops=None):

        # Put the route in the RIB.
        if negative_nexthops is None:
            negative_nexthops = []
        route = RibRoute(prefix, positive_nexthops, negative_nexthops)
        self._routes[prefix] = route

        # Gather the entire subtree of prefixes (children, grandchildren, ...) below the given
        # prefix (including the prefix itself). We rely on the fact that PyTricia.children always
        # returns parent aggregate routes before child more specific routes (although the PyTricia
        # documentation doesn't guarantee this).
        subtree_prefixes = [prefix] + self._routes.children(prefix)

        # Recompute the computed nexthops of child routes in the subtree and update the FIB
        # accordingly.
        self._recompute_subtree_nexthops(subtree_prefixes)

    def del_route(self, prefix):

        # If the route is not present in the RIB (this is legal), we have nothing to do.
        if not self._routes.has_key(prefix):
            return

        # Gather the entire subtree of prefixes (children, grandchildren, ...) below the given
        # prefix (excluding the prefix itself). We rely on the fact that PyTricia.children always
        # returns parent aggregate routes before child more specific routes (although the PyTricia
        # documentation doesn't guarantee this).
        subtree_prefixes = self._routes.children(prefix)

        # Delete the route from the RIB.
        del self._routes[prefix]

        # Delete corresponding route from the FIB.
        self._fib.del_route(prefix)

        # Recompute the computed nexthops of child routes in the subtree and update the FIB
        # accordingly.
        self._recompute_subtree_nexthops(subtree_prefixes)

    def get_route(self, prefix):
        if self._routes.has_key(prefix):
            return self._routes[prefix]
        return None

    def __str__(self):
        rep_str = ""
        for prefix in self._routes:
            rep_str += f"{self._routes[prefix]}\n"
        return rep_str

    def _recompute_subtree_nexthops(self, subtree_prefixes):
        for prefix in subtree_prefixes:
            route = self._routes[prefix]
            self._recompute_route_nexthops(route)
            self._fib.put_route(prefix, route.computed_nexthops)

    def _recompute_route_nexthops(self, route):

        # If the route does not have any negative nexthops, there is no disaggregation to be done.
        if not route.negative_nexthops:
            route.set_computed_nexthops(route.positive_nexthops)
            return

        # If the route does not have a parent route, there is no disaggregation to be done.
        parent_prefix = self._routes.parent(route.prefix)
        if parent_prefix is None:
            route.set_computed_nexthops(route.positive_nexthops)
            return

        # Compute the complementary nexthops of the negative nexthops.
        parent_route = self._routes[parent_prefix]
        complementary_nexthops = parent_route.computed_nexthops.difference(route.negative_nexthops)

        # Combine the complementary nexthops with the positive nexthops.
        computed_nexthops = route.positive_nexthops.union(complementary_nexthops)

        # Store the computed nexthops in the route
        route.set_computed_nexthops(computed_nexthops)
