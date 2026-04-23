import discord
from discord.ext import commands
from discord import app_commands
import random
from utils.db import get_player, save_player, add_exp, ENEMIES, FRUITS, WEAPONS
from utils.embeds import base_embed, error_embed, fruit_emoji

HUNT_COOLDOWNS = {}

class Hunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hunt", description="Düşman avla, EXP ve Beli kazan!")
    async def hunt(self, interaction: discord.Interaction):
        import time
        uid = interaction.user.id
        now = time.time()

        # 30 saniye cooldown
        if uid in HUNT_COOLDOWNS:
            elapsed = now - HUNT_COOLDOWNS[uid]
            if elapsed < 30:
                remaining = int(30 - elapsed)
                await interaction.response.send_message(
                    embed=error_embed(f"⏳ Hunt cooldown! `{remaining}s` bekle."),
                    ephemeral=True
                )
                return

        HUNT_COOLDOWNS[uid] = now
        player = get_player(uid)

        # Seviyeye göre düşman seç
        max_enemy_idx = min(player["level"] // 5, len(ENEMIES) - 1)
        enemy = random.choice(ENEMIES[:max_enemy_idx + 1])

        exp_gain = random.randint(enemy["min_exp"], enemy["max_exp"])
        beli_gain = random.randint(enemy["min_beli"], enemy["max_beli"])

        player["kills"] += 1
        player["beli"] += beli_gain
        player, level_msgs = add_exp(player, exp_gain)

        # Drop şansı
        drop_text = ""
        rolled = random.randint(1, 100)
        if rolled <= enemy["drop_chance"]:
            drop_type = random.choice(["fruit", "weapon"])
            if drop_type == "fruit":
                fruit = random.choice(FRUITS)
                if fruit not in player["fruits"]:
                    player["fruits"].append(fruit)
                    drop_text = f"\n🍎 **DROP:** {fruit_emoji(fruit)} `{fruit}` meyve aldın!"
                else:
                    beli_bonus = random.randint(100, 400)
                    player["beli"] += beli_bonus
                    drop_text = f"\n💰 **DROP:** Zaten var! Bunun yerine `{beli_bonus}` Beli aldın."
            else:
                weapon = random.choice(WEAPONS)
                if weapon not in player["weapons"]:
                    player["weapons"].append(weapon)
                    drop_text = f"\n⚔️ **DROP:** `{weapon}` silahı aldın!"
                else:
                    beli_bonus = random.randint(50, 200)
                    player["beli"] += beli_bonus
                    drop_text = f"\n💰 **DROP:** Zaten var! Bunun yerine `{beli_bonus}` Beli aldın."

        save_player(uid, player)

        embed = base_embed(
            title=f"⚔️ {enemy['name']} öldürüldü!",
            description=(
                f"**{interaction.user.display_name}** bir **{enemy['name']}** ile savaştı ve kazandı!\n\n"
                f"```\n"
                f"+ {exp_gain} EXP\n"
                f"+ {beli_gain} Beli\n"
                f"```"
                f"{drop_text}"
            )
        )
        embed.add_field(name="📊 Seviye", value=f"`{player['level']}`", inline=True)
        embed.add_field(name="💰 Toplam Beli", value=f"`{player['beli']:,}`", inline=True)
        embed.add_field(name="☠️ Toplam Kill", value=f"`{player['kills']}`", inline=True)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        if level_msgs:
            embed.add_field(name="🎉 Level Up!", value="\n".join(level_msgs), inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Hunt(bot))
