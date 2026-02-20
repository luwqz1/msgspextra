from msgspextra.custom_types.uri import IRI, URI, IRIReference, URIReference
from msgspextra.encoder import encoder


@encoder.add_enc_hook(IRIReference)
@encoder.add_enc_hook(IRI)
@encoder.add_enc_hook(URIReference)
@encoder.add_enc_hook(URI)
def uri_enc_hook(obj: URI | URIReference | IRI | IRIReference, /) -> str:
    return str(obj)


__all__ = ("uri_enc_hook",)
