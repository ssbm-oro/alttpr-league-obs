from typing import Any, List, TypeVar, Callable, Type, cast
from datetime import datetime, timedelta
import dateutil.parser


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_timedelta(x: Any) -> timedelta:
    if x is None:
        return
    return timedelta(
        hours=float(x[4:6]), minutes=float(x[7:9]), seconds=float(x[10:-1])
    )


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except Any:
            pass
    assert False
