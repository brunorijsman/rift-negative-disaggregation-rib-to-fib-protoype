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

        # Recompute the computed nexthops.
        self._recompute_nexthops(route)

        # Put the corresponding route with the computed effective nexthops in the FIB.
        self._fib.put_route(prefix, route.computed_nexthops)

    def del_route(self, prefix):

        # If the route is not present in the RIB (this is legal), we have nothing to do.
        if not self._routes.has_key(prefix):
            return

        # Gather the prefixes of the child routes before deleting the route from the RIB.
        child_prefixes = self._routes.children(prefix)

        # Delete the route from the RIB.
        del self._routes[prefix]

        # Delete corresponding route from the FIB.
        self._fib.del_route(prefix)

        # Recompute the computed nexthops of all child routes (if any) and update the FIB
        # accordingly.
        self._recompute_children_nexthops(child_prefixes)

    def get_route(self, prefix):
        if self._routes.has_key(prefix):
            return self._routes[prefix]
        return None

    def __str__(self):
        rep_str = ""
        for prefix in self._routes:
            rep_str += f"{self._routes[prefix]}\n"
        return rep_str

    def _recompute_nexthops(self, route):

        if not route.negative_nexthops:

            # The route does not have any negative nexthops; there is no disaggregation to be done.
            computed_nexthops = route.positive_nexthops

        else:

            parent_prefix = self._routes.parent(route.prefix)
            if parent_prefix is None:

                # The route does not have a parent route, there is no disaggregation to be done.
                computed_nexthops = route.positive_nexthops

            else:

                # Compute the complementary nexthops of the negative nexthops.
                parent_route = self._routes[parent_prefix]
                complementary_nexthops = \
                    parent_route.computed_nexthops.difference(route.negative_nexthops)

                # Combine the complementary nexthops with the positive nexthops.
                computed_nexthops = route.positive_nexthops.union(complementary_nexthops)

        # Store the computed nexthops in the route
        route.set_computed_nexthops(computed_nexthops)

        # If the route has any children, they must recursively also remcompute their nexthops.
        child_prefixes = self._routes.children(route.prefix)
        self._recompute_children_nexthops(child_prefixes)

    def _recompute_children_nexthops(self, child_prefixes):

        # Find all the child routes
        for child_prefix in child_prefixes:
            child_route = self._routes[child_prefix]

            # Recompute the computed nexthops for the child route.
            self._recompute_nexthops(child_route)

            # Update the child route in the FIB accordingly.
            self._fib.put_route(child_prefix, child_route.computed_nexthops)

            # Recursively visit all the child's children (i.e. grandchildren).
            grandchild_prefixes = self._routes.children(child_prefix)
            self._recompute_children_nexthops(grandchild_prefixes)
