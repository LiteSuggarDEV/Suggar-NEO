from nonebot import CommandGroup
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg

from src.plugins.menu.models import CategoryEnum, CommandParam, MatcherData, ParamType
from suggar_utils.blacklist.black import bl_manager
from suggar_utils.rule import is_global_admin

ban = CommandGroup("ban", permission=is_global_admin)

ban_group = ban.command(
    "group",
    state=MatcherData(
        name="封禁群",
        usage="/ban.group",
        description="封禁聊群",
        params=[
            CommandParam(
                name="group-id", description="群号", param_type=ParamType.REQUIRED
            ),
            CommandParam(
                name="原因",
                description="封禁原因",
                param_type=ParamType.OPTIONAL,
            ),
        ],
        examples=[
            "/ban.group 114514 违反使用规则",
            "/ban.group 114514",
        ],
        category=CategoryEnum.MANAGE,
    ).model_dump(),
)
ban_user = ban.command(
    "user",
    state=MatcherData(
        name="封禁用户",
        description="用于封禁用户",
        usage="/ban.user <user-id> [原因]",
        category=CategoryEnum.MANAGE,
        params=[
            CommandParam(
                name="user-id",
                description="用户ID",
                param_type=ParamType.REQUIRED,
            ),
            CommandParam(
                name="reason",
                default="无",
                description="封禁原因",
                param_type=ParamType.OPTIONAL,
            ),
        ],
        examples=[
            "/ban 123456789 封禁此用户",
            "/ban 123456789",
        ],
    ).model_dump(),
)


@ban_group.handle()
async def _(args: Message = CommandArg()):
    arg_list = args.extract_plain_text().strip().split(maxsplit=1)
    if not arg_list and len(arg_list) <= 2:
        await ban_group.finish("请提供要封禁的群ID！")
    if await bl_manager.is_group_black(arg_list[0]):
        await ban_group.finish("该群已被封禁！")
    else:
        await bl_manager.group_append(arg_list[0], arg_list[1]) if len(
            arg_list
        ) > 1 else await bl_manager.group_append(arg_list[0])
        await ban_group.finish(f"封禁群{arg_list[0]}成功！")


@ban_user.handle()
async def ban_user_handle(args: Message = CommandArg()):
    arg_list = args.extract_plain_text().strip().split(maxsplit=1)
    if not arg_list and len(arg_list) <= 2:
        await ban_group.finish("请提供要封禁的用户ID！")
    if await bl_manager.is_private_black(arg_list[0]):
        await ban_user.finish("该用户已被封禁！")
    else:
        await bl_manager.private_append(arg_list[0], arg_list[1]) if len(
            arg_list
        ) > 1 else await bl_manager.private_append(arg_list[0])
        await ban_user.finish(f"封禁用户{arg_list[0]}成功！")
