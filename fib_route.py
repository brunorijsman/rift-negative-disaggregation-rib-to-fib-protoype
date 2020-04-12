class FibRoute:

    def __init__(self, prefix, nexthops):
        self._prefix = prefix
        self._nexthops = set(nexthops)

    @property
    def prefix(self):
        return self._prefix

    def __str__(self):
        rep_str = f"{self._prefix} -> "
        sorted_nexthops = sorted(self._nexthops)
        first = True
        for nexthops in sorted_nexthops:
            if first:
                first = False
            else:
                rep_str += ", "
            rep_str += nexthops
        return rep_str
