import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = "YOUR_BOT_TOKEN_HERE"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

COGS = [
    "profile",
    "hunt",
    "inventory",
    "daily",
    "shop",
    "duel",
]

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

if __name__ == "__main__":
    bot.run(TOKEN)
