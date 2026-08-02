import inspect
from types import FunctionType


def namespace(cls):
    cls.__new__ = staticmethod(
        lambda *_, **__: (_ for _ in ()).throw(
            TypeError(f"{cls.__name__} cannot be instantiated.")
        )
    )

    for name, value in vars(cls).items():
        if name.startswith("__"):
            continue

        if isinstance(value, staticmethod):
            func = value.__func__

            params = tuple(inspect.signature(func).parameters)

            if params and params[0] in ("self", "cls"):
                raise TypeError(
                    f"{cls.__name__}.{name}: static methods cannot declare "
                    f"'{params[0]}' as the first parameter."
                )

            continue

        if isinstance(value, classmethod):
            raise TypeError(f"{cls.__name__}.{name}: classmethod is forbidden.")

        if isinstance(value, FunctionType):
            raise TypeError(
                f"{cls.__name__}.{name}: missing @staticmethod."
            )

    return cls