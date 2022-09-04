import discord


def get_asset_url(asset: discord.Asset) -> str:
    if asset.is_animated():
        return asset.with_format("gif").url
    else:
        return asset.with_format("png").url


def get_permissions(permissions: discord.Permissions) -> str:
    permissions = [name for name, value in permissions if value]

    if not permissions:
        return "`No permissions.`"
    elif "administrator" in permissions:
        return "`Administrator`"
    else:
        return ", ".join(
            f"`{name.replace('_', ' ').replace('guild', 'server').title()}`"
            for name in permissions
        )


def cleanup_code(content: str) -> str:
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])

    return content.strip("` \n")


def chunks(xs: list, n: int) -> list:
    n = max(1, n)
    return [xs[i : i + n] for i in range(0, len(xs), n)]
