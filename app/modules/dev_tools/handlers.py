import io
import csv
from aiogram.types.input_file import BufferedInputFile
from aiogram.types import Message
from app.utils.decorators import dev_only
from app.core.db import adapter as adp
from app.core.db.orm.base_model import BaseModel
from app.modules.dev_tools.confirmations import create_token, validate_token, consume_token
from app.config import settings
from app.utils.router_utils import get_router_commands

@dev_only
async def show_tables(message: Message, **kwargs):
    """List all database tables"""
    tables = await adp.list_tables()
    if not tables:
        await message.answer("No tables found.")
        return
    md = "| table |\n|---|\n"
    for t in tables:
        md += f"| {t} |\n"
    await message.answer(md)

@dev_only
async def show_table(message: Message, **kwargs):
    """Show schema and first 10 rows of a table"""
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Usage: /show_table <table>")
        return
    table = parts[1]
    tables = await adp.list_tables()
    if table not in tables:
        await message.answer("Table not found.")
        return
    schema = await adp.get_table_schema(table)
    md = "| column | type |\n|---|---|\n"
    for c, t in schema.items():
        md += f"| {c} | {t} |\n"
    await message.answer(md)
    rows = await adp.fetchall(f"SELECT * FROM {table} LIMIT :n", {"n": 10})
    if rows:
        header = "| " + " | ".join(rows[0].keys()) + " |\n"
        sep = "| " + " | ".join("---" for _ in rows[0].keys()) + " |\n"
        body = ""
        for r in rows:
            body += "| " + " | ".join(str(r[k]) for k in r.keys()) + " |\n"
        await message.answer(header + sep + body)

@dev_only
async def drop_tables(message: Message, **kwargs):
    """Drop all tables (requires confirmation)"""
    token = create_token(message.from_user.id, "drop_tables", {}, int(getattr(settings, "DEV_CONFIRM_TIMEOUT", 60)))
    await message.answer(f"WARNING: This will DROP ALL TABLES. To confirm, reply: CONFIRM DROP {token}")

@dev_only
async def clear_tables(message: Message, **kwargs):
    """Clear all tables (requires confirmation)"""
    token = create_token(message.from_user.id, "clear_tables", {}, int(getattr(settings, "DEV_CONFIRM_TIMEOUT", 60)))
    await message.answer(f"WARNING: This will CLEAR ALL TABLES. To confirm, reply: CONFIRM CLEAR {token}")

@dev_only
async def sql_exec(message: Message, **kwargs):
    """Execute raw SQL (select/update/delete)"""
    text = message.text or ""
    sql = text.partition(" ")[2].strip()
    if not sql:
        await message.answer("Usage: /sql <SQL>")
        return
    if ";" in sql:
        await message.answer("Multiple statements are not allowed.")
        return
    try:
        low = sql.strip().lower()
        if low.startswith("select") or low.startswith("with"):
            rows = await adp.fetchall(sql, {})
            n = len(rows)
            if n == 0:
                await message.answer("No rows returned.")
                return
            lim = int(getattr(settings, "DEV_SQL_MAX_ROWS", 200))
            if n > lim:
                bio = io.StringIO()
                writer = csv.DictWriter(bio, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
                data = bio.getvalue().encode()
                file = BufferedInputFile(data=data, filename="result.csv")
                await message.answer_document(file)
                return
            header = "| " + " | ".join(rows[0].keys()) + " |\n"
            sep = "| " + " | ".join("---" for _ in rows[0].keys()) + " |\n"
            body = ""
            for r in rows:
                body += "| " + " | ".join(str(r[k]) for k in r.keys()) + " |\n"
            await message.answer(header + sep + body)
        else:
            affected = await adp.execute(sql, {})
            await message.answer(f"Affected rows: {affected}")
    except Exception as e:
        msg = str(e)
        if len(msg) > 200:
            msg = msg[:200] + "..."
        await message.answer(f"Execution error: {msg}")

@dev_only
async def confirm_handler(message: Message, **kwargs):
    """Handle confirmation actions"""
    txt = (message.text or "").strip()
    if not txt.startswith("CONFIRM"):
        return
    parts = txt.split()
    if len(parts) != 3:
        await message.answer("Invalid confirmation format.")
        return
    _, action_word, token = parts
    action = "drop_tables" if action_word.upper() == "DROP" else ("clear_tables" if action_word.upper() == "CLEAR" else None)
    if action is None:
        await message.answer("Unknown confirmation action.")
        return
    info = validate_token(message.from_user.id, action, token)
    if not info:
        await message.answer("Invalid or expired token.")
        return
    try:
        async with adp.db_adapter.transaction():
            if action == "drop_tables":
                await adp.drop_all_tables()
            else:
                await adp.clear_all_tables()
        await message.answer("Done.")
    except Exception as e:
        msg = str(e)
        if len(msg) > 200:
            msg = msg[:200] + "..."
        await message.answer(f"Execution error: {msg}")
    finally:
        consume_token(token)

@dev_only
async def dev_commands_list(message: Message, **kwargs):
    """List available dev commands"""
    from .router import router
    commands = get_router_commands(router)
    text = f"🛠 <b>Dev Tools Commands</b>\n\n{commands}"
    await message.answer(text, parse_mode="HTML")
