class RibRoute:

    def __init__(self, prefix, positive_next_hops, negative_next_hops):
        self._prefix = prefix
        self._positive_next_hops = positive_next_hops
        self._negative_next_hops = negative_next_hops
        self._computed_next_hops = None     # None means "not computed yet"

    @property
    def prefix(self):
        return self._prefix

    def __repr__(self):
        str = f"{self._prefix} -> "
        all_next_hops = []
        for positive_next_hop in self._positive_next_hops:
            all_next_hops.append((positive_next_hop, True))
        for negative_next_hop in self._negative_next_hops:
            all_next_hops.append((negative_next_hop, False))
        all_next_hops.sort()
        first = True
        for (next_hops, is_positive) in all_next_hops:
            if first:
                first = False
            else:
                str += ", "
            if is_positive:
                str += next_hops
            else:
                str += "~" + next_hops
        return str
