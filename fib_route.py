class FibRoute:

    def __init__(self, prefix, nexthops):
        self._prefix = prefix
        self._nexthops = nexthops

    @property
    def prefix(self):
        return self._prefix

    def __repr__(self):
        str = f"{self._prefix} -> "
        sorted_nexthops = sorted(self._nexthops)
        first = True
        for nexthops in sorted_nexthops:
            if first:
                first = False
            else:
                str += ", "
            str += nexthops
        return str