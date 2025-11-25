## Overview
- Centralize all database logic under `app/core/db` and expose a single unified async adapter.
- Switch runtime backend by `.env` (`DB_TYPE=sqlite|postgres|mssql|none`) without code changes.
- Support transactions, pooling, parameterized queries, optional caching, and a DB-disabled mode for dev/tests.
- Keep SQLAlchemy/Alembic for migrations only; runtime IO uses direct drivers.

## Directory & Files
- `app/core/db/__init__.py`
- `app/core/db/adapter.py` (unified interface, backend selection)
- `app/core/db/sqlite_impl.py` (aiosqlite)
- `app/core/db/postgres_impl.py` (asyncpg)
- `app/core/db/mssql_impl.py` (aioodbc + pyodbc fallback)
- `app/core/db/disabled_impl.py` (no-op adapter for `DB_TYPE=none`)
- `app/core/db/sqlalchemy_impl.py` (engine setup for migrations only)

## Environment (.env.example)
- Add:
  - `DB_TYPE=sqlite` (options: sqlite | postgres | mssql | none)
  - SQLite: `SQLITE_PATH=./data/bot.db`
  - Postgres: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASS`
  - MSSQL: `MSSQL_DSN`, `MSSQL_USE_AIOODBC`, `MSSQL_POOL_MIN`, `MSSQL_POOL_MAX`, `MSSQL_QUERY_TIMEOUT`
- Keep existing settings (admin IDs, required channels, etc.).

## Adapter API (adapter.py)
- Singleton `db_adapter` exposing:
  - `async def execute(query: str, params: Optional[Iterable] = None) -> int`
  - `async def fetchone(query: str, params: Optional[Iterable] = None) -> Optional[Tuple]`
  - `async def fetchall(query: str, params: Optional[Iterable] = None) -> list[Tuple]`
  - `async def transaction()`: async context manager
  - `async def init_db_adapter()` and `async def close_db_adapter()`
- On `DB_TYPE=none`, raise `DBDisabledError` or return safe no-ops.

## Backend Implementations
### SQLite (sqlite_impl.py)
- Driver: `aiosqlite`
- No connection pool; one async connection per adapter lifetime.
- Placeholders: `?`
- Methods conform to adapter API; transaction via `async with conn.execute("BEGIN")` / `COMMIT` / `ROLLBACK`.

### PostgreSQL (postgres_impl.py)
- Driver: `asyncpg`
- Connection pool with `min_size`/`max_size` (defaults sensible).
- Placeholders: `$1, $2, ...`
- Transactions via `async with pool.acquire() as conn: async with conn.transaction(): ...`

### MSSQL (mssql_impl.py)
- Primary: `aioodbc` pool; fallback: `pyodbc` via `run_in_executor`.
- Pool sizing via `MSSQL_POOL_MIN`/`MSSQL_POOL_MAX`; timeout via `MSSQL_QUERY_TIMEOUT`.
- Placeholders: `?`
- Transactions: `async with pool.acquire() as conn` + cursor; `commit`/`rollback` methods.

### Disabled (disabled_impl.py)
- Methods raise `DBDisabledError` or return empty results to allow bot to run without DB.

### SQLAlchemy for Migrations (sqlalchemy_impl.py)
- Build SQLAlchemy engine based on `DB_TYPE` for Alembic migrations only.
- No runtime queries through SQLAlchemy.

## Initialization Hooks
- Startup: call `await init_db_adapter()` where the bot/dispatcher is initialized (e.g., application bootstrap, before registering routers).
- Shutdown: call `await close_db_adapter()` in graceful shutdown handler.
- If current project uses `app/db/base.py` with `AsyncSessionLocal`, keep it for migrations and replace runtime DB calls in services/middleware with `db_adapter`.

## Integration Targets
- Middleware/services/plugins import `from app.core.db.adapter import db_adapter` only.
- Examples:
  - Admin check: `await db_adapter.fetchone("SELECT 1 FROM admins WHERE user_id=?", [uid])`
  - Ban check: `await db_adapter.fetchone("SELECT 1 FROM bans WHERE user_id=?", [uid])`
  - Referral write: `await db_adapter.execute("INSERT INTO referrals(referrer_id,new_user_id) VALUES(?,?)", [rid, uid])`
- Join check and admin middleware can use optional in-memory caches to reduce query frequency.

## Security & Parameters
- Always parameterize queries (`?` for SQLite/MSSQL; `$1..$n` for Postgres).
- Never interpolate user input into SQL strings.

## Optional Caching Layer
- In-memory TTL caches for hot paths (admin, ban, join) within service modules;
- Keep cache invalidation simple; consider Redis later if multi-process.

## Testing
- Unit tests under `tests/` for:
  - Adapter routing by `DB_TYPE`
  - `execute`/`fetchone`/`fetchall` across backends (use a small temp table)
  - Transactions (commit/rollback)
  - Disabled mode behavior

## Migration Strategy
- Keep Alembic configured; generate migrations via SQLAlchemy models or raw DDL.
- Migration commands documented for devs; runtime continues to use adapter.

## Rollout Steps
1. Implement backend files and adapter.
2. Update `.env.example` with new DB settings.
3. Wire `init_db_adapter`/`close_db_adapter` into app startup/shutdown.
4. Refactor services/middleware to import `db_adapter`.
5. Add tests and run under your `telbot` conda environment.
6. Validate with each `DB_TYPE` (sqlite default; others optional).