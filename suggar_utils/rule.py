from nonebot import get_driver

from suggar_utils.config import config_manager
from suggar_utils.event import UserIDEvent

driver = get_driver()


async def is_global_admin(event: UserIDEvent) -> bool:
    return check_global_admin(event.user_id)


def check_global_admin(user_id: int) -> bool:
    return user_id in (
        {int(i) for i in driver.config.superusers}.union(
            set(config_manager.config.admins)
        ),
    )
