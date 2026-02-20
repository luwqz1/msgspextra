import ipaddress


class IPv4(ipaddress.IPv4Address):
    pass


class IPv6(ipaddress.IPv6Address):
    pass


__all__ = ("IPv4", "IPv6")
