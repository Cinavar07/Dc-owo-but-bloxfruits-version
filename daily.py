import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime
from utils.db import get_player, save_player, add_exp, FRUITS
from utils.embeds import base_embed, error_embed, fruit_emoji

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily", description="Günlük ödülünü al!")
    async def daily(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        now = datetime.datetime.utcnow()

        last_daily = player.get("last_daily")
        if last_daily:
            last_dt = datetime.datetime.fromisoformat(last_daily)
            diff = now - last_dt
            if diff.total_seconds() < 86400:
                remaining = 86400 - diff.total_seconds()
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                await interaction.response.send_message(
                    embed=error_embed(
                        f"⏳ Günlük ödülünü zaten aldın!\n"
                        f"Tekrar için: **{hours}s {minutes}dk** bekle."
                    ),
                    ephemeral=True
                )
                return

        # Ödüller
        beli_reward = random.randint(200, 600)
        exp_reward = random.randint(50, 120)
        player["beli"] += beli_reward
        player, level_msgs = add_exp(player, exp_reward)
        player["last_daily"] = now.isoformat()

        # %15 şansla random meyve
        fruit_reward = None
        if random.randint(1, 100) <= 15:
            fruit_reward = random.choice(FRUITS)
            if fruit_reward not in player["fruits"]:
                player["fruits"].append(fruit_reward)
            else:
                player["beli"] += 200
                fruit_reward = None

        save_player(interaction.user.id, player)

        desc = (
            f"🎁 Günlük ödülün hazır, **{interaction.user.display_name}**!\n\n"
            f"```\n"
            f"+ {beli_reward} Beli\n"
            f"+ {exp_reward} EXP\n"
            f"```"
        )
        if fruit_reward:
            desc += f"\n🍀 **Şans ödülü:** {fruit_emoji(fruit_reward)} `{fruit_reward}` meyve!"

        embed = base_embed(title="🎁 Günlük Ödül", description=desc)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="💰 Beli", value=f"`{player['beli']:,}`", inline=True)
        embed.add_field(name="📊 Seviye", value=f"`{player['level']}`", inline=True)

        if level_msgs:
            embed.add_field(name="🎉 Level Up!", value="\n".join(level_msgs), inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Daily(bot))
