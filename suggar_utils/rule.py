from suggar_utils.config import ConfigManager
from suggar_utils.event import UserIDEvent


async def is_global_admin(event: UserIDEvent) -> bool:
    return await check_global_admin(event.user_id)


async def check_global_admin(user_id: int) -> bool:
    return user_id in ConfigManager.instance().config.admins

