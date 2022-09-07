import re

YOUTUBE_REGEX = re.compile(
    r"https?://((?:www|m|music)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
)

HEX_REGEX = re.compile(r"^#?([a-f\d]{3,4}|[a-f\d]{6}|[a-f\d]{8})$")
RGB_REGEX = re.compile(
    r"^(rgb)?\(?([01]?\d\d?|2[0-4]\d|25[0-5])(\W+)([01]?\d\d?|2[0-4]\d|25[0-5])\W+(([01]?\d\d?|2[0-4]\d|25[0-5])\)?)$"
)
