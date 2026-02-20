import typing

from msgspextra.custom_types.uri import IRI, URI, IRIReference, URIReference
from msgspextra.decoder import decoder


@decoder.add_dec_hook(IRIReference)
@decoder.add_dec_hook(IRI)
@decoder.add_dec_hook(URIReference)
@decoder.add_dec_hook(URI)
def uri_dec_hook(tp: typing.Any, obj: typing.Any, /) -> typing.Any:
    return obj if isinstance(obj, tp) else tp(obj)


__all__ = ("uri_dec_hook",)
