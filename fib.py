from pytricia import PyTricia   # pylint:disable=no-name-in-module

from fib_route import FibRoute

class Fib:

    def __init__(self):
        self._routes = PyTricia()

    def put_route(self, prefix, nexthops):
        route = FibRoute(prefix, nexthops)
        self._routes[prefix] = route

    def del_route(self, prefix):
        if self._routes.has_key(prefix):
            del self._routes[prefix]

    def get_route(self, prefix):
        if self._routes.has_key(prefix):
            return self._routes[prefix]
        return None

    def __str__(self):
        repr_str = ""
        for prefix in self._routes:
            repr_str += f"{self._routes[prefix]}\n"
        return repr_str
