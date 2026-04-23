import discord
import datetime

BLOX_COLOR = discord.Color.from_rgb(255, 165, 0)  # Turuncu - Blox Fruits teması
ERROR_COLOR = discord.Color.red()
SUCCESS_COLOR = discord.Color.green()
INFO_COLOR = discord.Color.blue()

def base_embed(title: str, description: str = "", color=BLOX_COLOR) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="⚔️ Blox Fruits Bot")
    return embed

def error_embed(msg: str) -> discord.Embed:
    return base_embed("❌ Hata", msg, ERROR_COLOR)

def success_embed(title: str, msg: str) -> discord.Embed:
    return base_embed(f"✅ {title}", msg, SUCCESS_COLOR)

def fruit_emoji(fruit_name: str) -> str:
    mythicals = ["Uo Uo", "Juku Juku", "Mochi Mochi", "Soru Soru (Mythical)"]
    legendaries = ["Yami Yami", "Gura Gura", "Ope Ope", "Ito Ito"]
    if fruit_name in mythicals:
        return "🐉"
    elif fruit_name in legendaries:
        return "💎"
    else:
        return "🍎"
