from pytricia import PyTricia   # pylint:disable=no-name-in-module

from rib_route import RibRoute

class Rib:

    def __init__(self, fib):
        self._fib = fib
        # Since this prototype only support a single route per destination, we don't bother having
        # any Destination class.
        self._routes = PyTricia()

    def put_route(self, prefix, positive_nexthops, negative_nexthops=None):

        # Put the route in the RIB.
        if negative_nexthops is None:
            negative_nexthops = []
        route = RibRoute(prefix, positive_nexthops, negative_nexthops)
        self._routes[prefix] = route

        # Recompute the computed nexthops.
        computed_nexthops = self._recompute_nexthops(route)
        route.set_computed_nexthops(computed_nexthops)

        # Put the corresponding route with the computed effective nexthops in the FIB.
        self._fib.put_route(prefix, computed_nexthops)

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
        # If the route does not have any negative nexthops, there is no disaggregation to be done.
        if not route.negative_nexthops:
            return route.positive_nexthops
        # If the route does not have a parent route, there is no disaggregation to be done.
        parent_prefix = self._routes.parent(route.prefix)
        if parent_prefix is None:
            return route.positive_nexthops
        # Compute the complementary nexthops of the negative nexthops.
        parent_route = self._routes[parent_prefix]
        complementary_nexthops = parent_route.computed_nexthops.difference(route.negative_nexthops)
        # Combine the complementary nexthops with the positive nexthops.
        return route.positive_nexthops.union(complementary_nexthops)

    def _recompute_children_nexthops(self, child_prefixes):
        # Find all the child routes
        for child_prefix in child_prefixes:
            child_route = self._routes[child_prefix]
            # Recompute the computed nexthops for the child route.
            computed_nexthops = self._recompute_nexthops(child_route)
            child_route.set_computed_nexthops(computed_nexthops)
            # Update the child route in the FIB accordingly.
            self._fib.put_route(child_prefix, computed_nexthops)
            # Recursively visit all the child's children (i.e. grandchildren).
            grandchild_prefixes = self._routes.children(child_prefix)
            self._recompute_children_nexthops(grandchild_prefixes)
