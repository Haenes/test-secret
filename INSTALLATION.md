# INSTALLATION

1) Clone repository: `git clone https://github.com/Haenes/test-secret.git`
2) Open reposiroty dir: `cd test-secret`
3) Create .env file with following env's:
```
POSTGRES_USER = 'test'
POSTGRES_PASSWORD = 'PpWurHzb75#'
POSTGRES_HOST = 'db'
POSTGRES_PORT = '5432'
POSTGRES_DB = 'secret'

REDIS_USER = 'test'
REDIS_PASSWORD = 'Testing'

ENCRYPTION_KEY = 'ra1Mz1L7r6b57Oc874_BGsjRtThCKvo-tgbdxQagCcg='
```
4) Start docker compose: `docker compose up`
5) Add basic actions and create trigger (for clean up of expired secrets) in db:
>Run one command at a time!
- `docker compose exec db psql -U test -d secret`

- `INSERT INTO action VALUES (1, 'Создание'), (2, 'Просмотр'), (3, 'Удаление');`

- `CREATE OR REPLACE FUNCTION secret_table_delete_expired_secrets() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
DELETE FROM secret WHERE created_at + make_interval(secs => ttl_seconds) < now();
RETURN NEW;
END;
$$;`

- `CREATE TRIGGER secret_table_delete_expired_secrets_trigger
AFTER INSERT ON secret
EXECUTE PROCEDURE secret_table_delete_expired_secrets();`

6) Go to [here](http://localhost:8000/docs) or [here](http://127.0.0.1:8000/docs).
