from amrita.plugins.perm.API.admin import is_lp_admin
from nonebot.adapters.onebot.v11 import Event


async def is_global_admin(event: Event) -> bool:
    return await is_lp_admin(event)
