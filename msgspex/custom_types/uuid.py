import typing

if typing.TYPE_CHECKING:
    from uuid import UUID as UUID4

else:
    from uuid import UUID

    class UUID4(UUID): ...


__all__ = ("UUID4",)
