import typing

if typing.TYPE_CHECKING:
    from kungfu.library.monad.option import Option
else:
    from kungfu.library import Nothing, Some
    from msgspec import UnsetType

    class OptionMeta(type):
        def __instancecheck__(cls, __instance):
            return isinstance(__instance, Some | Nothing | UnsetType)

    class Option[Value](metaclass=OptionMeta):
        pass


__all__ = ("Option",)
