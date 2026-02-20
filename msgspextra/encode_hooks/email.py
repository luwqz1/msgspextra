from msgspextra.custom_types.email import Email, IDNEmail
from msgspextra.encoder import encoder


@encoder.add_enc_hook(IDNEmail)
@encoder.add_enc_hook(Email)
def email_enc_hook(obj: Email | IDNEmail, /) -> str:
    return str(obj)


__all__ = ("email_enc_hook",)
