import ipaddress

class Prefix:

    def __init__(self, prefix_str):
        ipv4_network = ipaddress.IPv4Network(prefix_str)
        self._address = ipv4_network.network_address
        self._prefix_len = ipv4_network.prefixlen

    def __str__(self):
        return str(self._address) + '/' + str(self._prefix_len)
        