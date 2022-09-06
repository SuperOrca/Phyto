import datetime
from enum import Enum
from typing import Any, Optional, Union, Iterable, Tuple

import discord
from typing_extensions import Self


# https://discord.com/branding
class EmbedColor(Enum):
    DEFAULT = discord.Color.from_rgb(9, 166, 246)
    SUCCESS = discord.Color.from_rgb(87, 242, 135)
    WARNING = discord.Color.from_rgb(254, 231, 92)
    ERROR = discord.Color.from_rgb(237, 66, 69)


class Embed(discord.Embed):
    def __init__(
        self,
        *,
        color: Union[EmbedColor, discord.Color, int] = None,
        timestamp: Optional[datetime.datetime] = None,
        fields: Iterable[Tuple[str, str]] = (),
        field_inline: bool = False,
        **kwargs: Any
    ):
        super().__init__(
            color=(color.value if isinstance(color, EmbedColor) else color),
            timestamp=timestamp or discord.utils.utcnow(),
            **kwargs
        )
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    @classmethod
    def default(cls: Self, **kwargs: Any) -> Self:
        return cls(color=EmbedColor.DEFAULT, **kwargs)

    @classmethod
    def error(cls: Self, **kwargs: Any) -> Self:
        return cls(color=EmbedColor.ERROR, **kwargs)
