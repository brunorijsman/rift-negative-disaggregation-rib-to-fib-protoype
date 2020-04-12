from fib_route import FibRoute

from pytricia import PyTricia

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
        else:
            return None

    def __repr__(self):
        str = ""
        for prefix in self._routes:
            str +=  f"{self._routes[prefix]}\n"
        return str
