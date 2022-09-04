import asyncio
import functools
from typing import Optional, Callable, TypeVar, ParamSpec, Awaitable

T = TypeVar("T")
P = ParamSpec("P")


def in_executor(
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> Callable[[Callable[P, T]], Callable[P, Awaitable[T]]]:
    def inner_function(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        def function(*args: P.args, **kwargs: P.kwargs) -> Awaitable[T]:
            loop_ = loop or asyncio.get_event_loop()
            partial = functools.partial(func, *args, **kwargs)
            return loop_.run_in_executor(None, partial)

        return function

    return inner_function
