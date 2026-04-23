import discord
from discord.ext import commands
from discord import app_commands
from utils.db import get_player, exp_to_next_level
from utils.embeds import base_embed, fruit_emoji

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Blox Fruits profilini görüntüle")
    @app_commands.describe(kullanici="Başka birinin profilini görüntüle (opsiyonel)")
    async def profile(self, interaction: discord.Interaction, kullanici: discord.Member = None):
        target = kullanici or interaction.user
        player = get_player(target.id)

        level = player["level"]
        exp = player["exp"]
        next_exp = exp_to_next_level(level)
        exp_bar_len = 10
        filled = int((exp / next_exp) * exp_bar_len)
        exp_bar = "█" * filled + "░" * (exp_bar_len - filled)

        fruit = player.get("equipped_fruit")
        fruit_display = f"{fruit_emoji(fruit)} {fruit}" if fruit else "❌ Yok"
        weapon = player.get("equipped_weapon", "Yok")

        embed = base_embed(
            title=f"⚔️ {target.display_name} — Blox Fruits Profili"
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="📊 Seviye", value=f"`{level}`", inline=True)
        embed.add_field(name="💰 Beli", value=f"`{player['beli']:,}`", inline=True)
        embed.add_field(name="☠️ Kill", value=f"`{player['kills']}`", inline=True)
        embed.add_field(
            name=f"📈 EXP [{exp_bar}]",
            value=f"`{exp} / {next_exp}`",
            inline=False
        )
        embed.add_field(name="🍎 Meyve", value=fruit_display, inline=True)
        embed.add_field(name="🗡️ Silah", value=f"⚔️ {weapon}", inline=True)
        embed.add_field(
            name="🏆 Düello",
            value=f"✅ {player['wins']}W / ❌ {player['losses']}L",
            inline=True
        )
        embed.add_field(
            name="🎒 Envanter",
            value=f"`{len(player['fruits'])}` meyve, `{len(player['weapons'])}` silah",
            inline=True
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
