from __future__ import annotations

from .constants import HEX_REGEX, RGB_REGEX


class Color:
    def __init__(self, color: tuple) -> None:
        self.color = color

    @classmethod
    def parse(cls: Color, color: str) -> Color:
        color = color.lower().strip(" ")

        if HEX_REGEX.match(color):
            color = color.strip("#")

            if len(color) == 3:
                color = f"{color[0] * 2}{color[1] * 2}{color[2] * 2}"

            return cls((int(color[:2], 16), int(color[2:4], 16), int(color[4:6], 16)))

        if match := RGB_REGEX.match(color):
            color = match[0].split(",")
            return cls((int(color[0]), int(color[1]), int(color[2])))

        return None

    def to_rgb(self) -> tuple:
        return self.color

    def to_hex(self) -> str:
        return "%02x%02x%02x" % self.color
