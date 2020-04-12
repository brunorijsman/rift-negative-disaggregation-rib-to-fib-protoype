
class RibRoute:

    def __init__(self, prefix, positive_nexthops, negative_nexthops):
        self._prefix = prefix
        self._positive_nexthops = set(positive_nexthops)
        self._negative_nexthops = set(negative_nexthops)
        self._computed_nexthops = None     # None means "not computed yet"

    @property
    def prefix(self):
        return self._prefix

    @property
    def positive_nexthops(self):
        return self._positive_nexthops

    @property
    def negative_nexthops(self):
        return self._negative_nexthops

    @property
    def computed_nexthops(self):
        return self._computed_nexthops

    def set_computed_nexthops(self, computed_nexthops):
        self._computed_nexthops = set(computed_nexthops)

    def __str__(self):
        rep_str = f"{self._prefix} -> "
        all_nexthops = []
        for positive_nexthop in self._positive_nexthops:
            all_nexthops.append((positive_nexthop, True))
        for negative_nexthop in self._negative_nexthops:
            all_nexthops.append((negative_nexthop, False))
        all_nexthops.sort()
        first = True
        for (nexthops, is_positive) in all_nexthops:
            if first:
                first = False
            else:
                rep_str += ", "
            if is_positive:
                rep_str += nexthops
            else:
                rep_str += "~" + nexthops
        return rep_str
