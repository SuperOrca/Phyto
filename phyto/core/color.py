import re

from typing_extensions import Self

HEX_REGEX = r"^#?([a-f\d]{3,4}|[a-f\d]{6}|[a-f\d]{8})$"
RGB_REGEX = r"^(rgb)?\(?([01]?\d\d?|2[0-4]\d|25[0-5])(\W+)([01]?\d\d?|2[0-4]\d|25[0-5])\W+(([01]?\d\d?|2[0-4]\d|25[0-5])\)?)$"


class Color:
    def __init__(self, color: tuple) -> None:
        self.color = color

    @classmethod
    def parse(cls: Self, color: str) -> Self:
        color = color.lower().strip(" ")

        if re.match(HEX_REGEX, color):
            color = color.strip("#")

            if len(color) == 3:
                color = f"{color[0] * 2}{color[1] * 2}{color[2] * 2}"

            return cls((int(color[:2], 16), int(color[2:4], 16), int(color[4:6], 16)))

        if match := re.match(RGB_REGEX, color):
            color = match[0].split(",")
            return cls((int(color[0]), int(color[1]), int(color[2])))

        return None

    def to_rgb(self) -> tuple:
        return self.color

    def to_hex(self) -> str:
        return "%02x%02x%02x" % self.color
