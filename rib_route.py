class RibRoute:

    def __init__(self, prefix, positive_nexthops, negative_nexthops):
        self._prefix = prefix
        self._positive_nexthops = positive_nexthops
        self._negative_nexthops = negative_nexthops
        self._computed_nexthops = None     # None means "not computed yet"  TODO: need it?

    @property
    def prefix(self):
        return self._prefix

    # TODO: unit test
    def set_computed_nexthops(self, computed_nexthops):
        self._computed_nexthops = computed_nexthops

    def __repr__(self):
        str = f"{self._prefix} -> "
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
                str += ", "
            if is_positive:
                str += nexthops
            else:
                str += "~" + nexthops
        return str
