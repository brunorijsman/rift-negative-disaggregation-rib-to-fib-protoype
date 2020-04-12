
class RibRoute:

    def __init__(self, prefix, positive_nexthops, negative_nexthops):
        self._prefix = prefix
        self._positive_nexthops = set(positive_nexthops)
        self._negative_nexthops = set(negative_nexthops)
        self._computed_nexthops = None     # None means "not computed yet"

    @property
    def prefix(self):
        return self._prefix

    # TODO: unit test
    @property
    def positive_nexthops(self):
        return self._positive_nexthops

    # TODO: unit test
    @property
    def negative_nexthops(self):
        return self._negative_nexthops

    # TODO: unit test
    @property
    def computed_nexthops(self):
        return self._computed_nexthops

    # TODO: unit test
    def set_computed_nexthops(self, computed_nexthops):
        self._computed_nexthops = computed_nexthops

    # TODO: __repr__ -> __str__
    def __repr__(self):
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
