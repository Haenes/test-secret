from typing import AsyncGenerator, Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Request

from cryptography.fernet import Fernet

from crud import (
    create_secret_in_db,
    get_secret_from_db,
    delete_secret_from_db
)
from schemas import SecretCreate, SecretRead, SecretPassphrase
from settings import settings
from utils.cache import (
    get_redis_client,
    create_secret_in_cache,
    get_secret_from_cache,
    delete_secret_from_cache
)
from utils.db import get_async_session
from utils.hasher import passphrase_hash


app = FastAPI()
fernet = Fernet(bytes(settings.ENCRYPTION_KEY, 'utf-8'))
get_db_session = Annotated[AsyncGenerator, Depends(get_async_session)]
get_cache_client = Annotated[AsyncGenerator, Depends(get_redis_client)]


@app.post('/secret', status_code=201)
async def create_secret(
    secret: SecretCreate,
    db_session: get_db_session,
    cache_client: get_cache_client,
    request: Request
) -> dict[str, UUID]:
    secret.secret = fernet.encrypt(bytes(secret.secret, 'utf-8'))

    if secret.passphrase:
        secret.passphrase = passphrase_hash.hash(secret.passphrase)

    secret = await create_secret_in_db(secret, request.client.host, db_session)
    await create_secret_in_cache(cache_client, secret.secret_key, secret)

    return {"secret_key": secret.secret_key}


@app.get('/secret/{secret_key}')
async def get_secret(
    secret_key: UUID,
    db_session: get_db_session,
    cache_client: get_cache_client,
    request: Request
) -> SecretRead:
    if secret := await get_secret_from_cache(cache_client, secret_key):
        secret['secret'] = fernet.decrypt(secret['secret'])
        secret['is_accessed'] = True
        return secret

    secret = await get_secret_from_db(secret_key, request.client.host, db_session)
    secret.secret = fernet.decrypt(secret.secret)
    secret.is_accessed = True
    return secret


@app.delete('/secret/{secret_key}')
async def delete_secret(
    secret_key: UUID,
    db_session: get_db_session,
    cache_client: get_cache_client,
    request: Request,
    passphrase: SecretPassphrase,
) -> dict[str, str]:
    await delete_secret_from_db(
        secret_key,
        request.client.host,
        db_session,
        passphrase.passphrase
    )
    await delete_secret_from_cache(cache_client, secret_key)
    return {'result': 'Секрет удалён!'}
