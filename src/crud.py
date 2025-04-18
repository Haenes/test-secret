import datetime
from uuid import UUID

from fastapi.exceptions import HTTPException

from sqlalchemy import select, insert, delete, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError
from asyncpg.exceptions import DataError

from schemas import SecretCreate
from models import Secret, Log
from utils.hasher import passphrase_hash


async def create_log_entry(
    action_id: int,
    secret_key: UUID,
    from_ip: str,
    session: AsyncSession
):
    create_log_entry_stmt = insert(Log).values({
        'action_id': action_id,
        'secret_key': secret_key,
        'from_ip': from_ip
    })
    await session.scalar(create_log_entry_stmt)


async def create_secret_in_db(
    secret: SecretCreate,
    from_ip: str,
    session: AsyncSession
):
    create_secret_stmt = (
        insert(Secret)
        .values(**secret.model_dump())
        .returning(Secret)
    )
    created_secret = await session.scalar(create_secret_stmt)

    await create_log_entry(1, created_secret.secret_key, from_ip, session)
    return created_secret


async def get_secret_from_db(secret_key: UUID, from_ip: str, session: AsyncSession):
    get_secret_query = select(Secret).where(Secret.secret_key == secret_key)
    secret = await handle_incorrect_secret_key(get_secret_query, session)

    if not secret:
        await get_secret_from_logs(secret_key, session)
    elif (
        secret.created_at + datetime.timedelta(seconds=secret.ttl_seconds)
        < datetime.datetime.now(datetime.UTC)
    ):
        await delete_secret_from_db(secret_key, from_ip, session, is_force_delete=True)
        raise HTTPException(400, 'Время жизни секрета истекло!')

    await create_log_entry(2, secret_key, from_ip, session)
    await delete_secret_from_db(secret_key, from_ip, session, is_force_delete=True)
    return secret


async def delete_secret_from_db(
    secret_key: UUID,
    from_ip: str,
    session: AsyncSession,
    passphrase: str | None = None,
    is_force_delete: bool | None = False
):
    delete_secret_stmt = (
        delete(Secret)
        .where(Secret.secret_key == secret_key)
        .returning(Secret.secret_key)
    )
    secret_to_delete_query = select(Secret).where(Secret.secret_key == secret_key)
    secret_to_delete = await handle_incorrect_secret_key(
        secret_to_delete_query,
        session
    )

    if not secret_to_delete:
        await get_secret_from_logs(secret_key, session)
    elif secret_to_delete.passphrase and not is_force_delete and not passphrase:
        raise HTTPException(
            status_code=400,
            detail='Для удаления этого секрета нужна заданная фраза-пароль!'
        )
    elif (
        not is_force_delete and not
        passphrase_hash.verify(passphrase, secret_to_delete.passphrase)
    ):
        raise HTTPException(400, 'Неверная фраза-пароль!')

    await session.scalar(delete_secret_stmt)
    await create_log_entry(3, secret_key, from_ip, session)


async def handle_incorrect_secret_key(query: Select, session: AsyncSession):
    """Обрабатывает случай, когда secret_key передаётся в неверном формате.

    Если возникает какая-то другая ошибка - поднимает 500-ю ошибку.
    """
    try:
        secret = await session.scalar(query)
    except DBAPIError as e:
        if e.orig.__context__.__class__ is DataError:
            raise HTTPException(400, 'Некорректный ключ!')
        raise HTTPException(500, 'Непредвиденная ошибка!')
    return secret


async def get_secret_from_logs(secret_key: UUID, session: AsyncSession):
    secret_in_logs_query = (
        select(Log)
        .where(Log.secret_key == secret_key)
        .order_by(Log.created_at.desc(), Log.action_id.desc())
    )
    secret_in_logs = await session.scalars(secret_in_logs_query)

    match secret_in_logs.first().action_id:
        case 3:
            raise HTTPException(400, 'Секрет был удалён/его время жизни истекло!')
        case 2:
            raise HTTPException(400, 'Секрет уже был просмотрен!')
        case _:
            raise HTTPException(404, 'Секрет не найден!')
