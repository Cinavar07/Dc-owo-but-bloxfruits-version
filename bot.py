"""
Blox Fruits Discord Botu
========================
Komutlar:
  /profile  → Profil görüntüle
  /hunt     → Düşman avla (30s cooldown)
  /inventory → Envanter & kuşan
  /equip    → Meyve/silah kuşan
  /daily    → Günlük ödül
  /shop     → Dükkân
  /duel     → Oyuncuya meydan oku
"""

import discord
from discord.ext import commands
from discord import app_commands
import os
import json

# ─── CONFIG ───────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN_HERE")
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

# ─── BOT KURULUMU ─────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─── COGS ─────────────────────────────────────────────────
COGS = [
    "cogs.profile",
    "cogs.hunt",
    "cogs.inventory",
    "cogs.daily",
    "cogs.shop",
    "cogs.duel",
]

# ─── OLAYLAR ──────────────────────────────────────────────
@bot.event
async def on_ready():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"  ✅ {cog} yüklendi")
        except Exception as e:
            print(f"  ❌ {cog} yüklenemedi: {e}")

    await bot.tree.sync()
    print(f"\n🍎 Blox Fruits Bot hazır!")
    print(f"👤 Bot: {bot.user} ({bot.user.id})")
    print(f"🌐 {len(bot.guilds)} sunucuda aktif")
    print(f"📋 Slash komutlar senkronize edildi\n")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="Blox Fruits 🍎"
        )
    )

@bot.event
async def on_guild_join(guild):
    print(f"➕ Yeni sunucu: {guild.name} ({guild.id})")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bu komutu kullanmak için yetkin yok!", ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏳ Cooldown! `{error.retry_after:.1f}s` bekle.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(f"❌ Bir hata oluştu: `{error}`", ephemeral=True)
        print(f"[HATA] {error}")

# ─── BAŞLAT ───────────────────────────────────────────────
if __name__ == "__main__":
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️  DISCORD_TOKEN ortam değişkenini ayarla!")
        print("    Linux/Mac: export DISCORD_TOKEN=token_buraya")
        print("    Windows:   set DISCORD_TOKEN=token_buraya")
        print("    .env ile:  DISCORD_TOKEN=token_buraya")
    else:
        bot.run(TOKEN)
