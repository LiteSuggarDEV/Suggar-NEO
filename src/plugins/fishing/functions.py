from collections.abc import Sequence

from nonebot_plugin_orm import AsyncSession, get_session
from nonebot_plugin_value.uuid_lib import to_uuid
from sqlalchemy import insert, select

from .models import FishMeta, FishRecord, QualityMetaData, UserFishMetaData
from .pyd_models import Fish, QualityMeta, UserData
from .pyd_models import FishMeta as F_Meta


async def create_fish(fish: FishMeta):
    async with get_session() as session:
        session.add(fish)
        await session.commit()


async def get_or_create_user_model(
    user_id: int, session: AsyncSession
) -> UserFishMetaData:
    uid = to_uuid(str(user_id))
    async with session:
        stmt = select(UserFishMetaData).where(UserFishMetaData.user_id == uid)
        if user_model := (await session.execute(stmt)).scalar_one_or_none():
            return user_model
        user_model = UserFishMetaData(user_id=uid)
        session.add(user_model)
        await session.commit()
    return user_model


async def get_user_fish(user_id: int, session: AsyncSession) -> Sequence[FishRecord]:
    uid = to_uuid(str(user_id))
    async with session:
        stmt = select(FishRecord).where(FishRecord.user_id == uid)
        return (await session.execute(stmt)).scalars().all()


async def get_or_create_quilty(
    meta: QualityMeta, session: AsyncSession
) -> QualityMetaData:
    async with session:
        stmt = select(QualityMetaData).where(QualityMetaData.name == meta.name)
        result = await session.execute(stmt)
        if (data := result.scalar_one_or_none()) is not None:
            return data
        else:
            quality = QualityMetaData(
                name=meta.name,
                length_range_start=meta.length_range_start,
                length_range_end=meta.length_range_end,
                price_per_length=meta.price_per_length,
                probability=meta.probability,
            )
            session.add(quality)
            await session.commit()
            return quality


async def get_quailty(name: str, session: AsyncSession) -> QualityMetaData:
    async with session:
        stmt = select(QualityMetaData).where(QualityMetaData.name == name)
        result = await session.execute(stmt)
        return result.scalar_one()


async def get_or_create_fish(data: F_Meta, session: AsyncSession):
    async with session:
        if (fish := await get_fish_meta_or_none(data.name, session)) is not None:
            return fish
        else:
            stmt = select(QualityMetaData).where(QualityMetaData.name == data.quality)
            result = await session.execute(stmt)
            quality = result.scalar_one_or_none()
            if quality is None:
                raise ValueError(f"Invalid quality: {data.quality}")
            stmt = insert(FishMeta).values(
                name=data.name,
                price_per_length=quality.price_per_length,
                quality=data.quality,
            )
            await session.execute(stmt)
            fish = await get_fish_meta(data.name, session)
            assert fish is not None, "ERROR:FishMeta is None!"
            return fish


async def get_fish_meta(name: str, session: AsyncSession) -> FishMeta:
    async with session:
        stmt = select(FishMeta).where(FishMeta.name == name)
        return (await session.execute(stmt)).scalars().one()


async def get_fish_meta_or_none(name: str, session: AsyncSession) -> FishMeta | None:
    async with session:
        stmt = select(FishMeta).where(FishMeta.name == name)
        return (await session.execute(stmt)).scalar_one_or_none()


async def get_fish_meta_pyd(name: str) -> F_Meta:
    async with get_session() as session:
        meta = await get_fish_meta(name, session)
        return F_Meta(
            name=meta.name,
            quality=meta.quality,
            quality_data=QualityMeta.model_validate(
                await get_quailty(meta.quality, session), from_attributes=True
            ),
        )


async def get_all_fish_meta(session: AsyncSession) -> Sequence[FishMeta]:
    async with get_session() as session:
        stmt = select(FishMeta)
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_all_fish_meta_pyd() -> list[F_Meta]:
    async with get_session() as session:
        data = await get_all_fish_meta(session)
        quailty_cache: dict[str, QualityMeta] = {}
        result = []
        for meta in data:
            quailty = quailty_cache.get(meta.quality)
            if quailty is None:
                quailty = QualityMeta.model_validate(
                    await get_quailty(meta.quality, session)
                )
            result.append(
                F_Meta(
                    name=meta.name,
                    quality=meta.quality,
                    quality_data=quailty,
                )
            )
        return result


async def get_user_data_pyd(user_id: int) -> UserData:
    async with get_session() as session:
        fishes = await get_user_fish(user_id, session)
        meta_cache: dict[str, F_Meta] = {}
        fish_list = []
        for fish in fishes:
            fish_meta = meta_cache.get(fish.fish_name)
            if fish_meta is None:
                fish_meta = await get_fish_meta_pyd(fish.fish_name)
                meta_cache[fish.fish_name] = fish_meta
            fish_list.append(
                Fish(
                    user_id=fish.user_id,
                    length=fish.length,
                    time=fish.time,
                    metadata=fish_meta,
                )
            )
        return UserData(user_id=user_id, fishes=fish_list)


async def add_fish_record(user_id: int, fish: Fish):
    async with get_session() as session:
        await get_or_create_user_model(user_id, session)
        fish_meta = fish.metadata
        await get_or_create_fish(fish_meta, session)
        record = FishRecord(
            fish_name=fish_meta.name,
            length=fish.length,
            time=fish.time,
            user_id=to_uuid(str(user_id)),
        )
        session.add(record)
        await session.commit()
