import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from utils.db import get_player, save_player, add_exp
from utils.embeds import base_embed, error_embed, fruit_emoji

DUEL_PENDING = {}

class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="duel", description="Başka bir oyuncuya düello meydan oku!")
    @app_commands.describe(rakip="Düello yapmak istediğin oyuncu", bahis="Bahis miktarı (Beli)")
    async def duel(self, interaction: discord.Interaction, rakip: discord.Member, bahis: int = 0):
        challenger = interaction.user

        if rakip.bot:
            await interaction.response.send_message(embed=error_embed("Botlarla düello yapamazsın!"), ephemeral=True)
            return
        if rakip.id == challenger.id:
            await interaction.response.send_message(embed=error_embed("Kendinle düello yapamazsın!"), ephemeral=True)
            return
        if challenger.id in DUEL_PENDING:
            await interaction.response.send_message(embed=error_embed("Zaten bekleyen bir düellonun var!"), ephemeral=True)
            return

        challenger_data = get_player(challenger.id)
        rakip_data = get_player(rakip.id)

        if bahis > 0:
            if challenger_data["beli"] < bahis:
                await interaction.response.send_message(
                    embed=error_embed(f"Yeterli Beliniz yok! Gerekli: `{bahis:,}`"),
                    ephemeral=True
                )
                return
            if rakip_data["beli"] < bahis:
                await interaction.response.send_message(
                    embed=error_embed(f"{rakip.display_name} yeterli Beliye sahip değil!"),
                    ephemeral=True
                )
                return

        DUEL_PENDING[challenger.id] = {
            "rakip": rakip.id,
            "bahis": bahis
        }

        embed = base_embed(
            title="⚔️ Düello Daveti!",
            description=(
                f"**{challenger.display_name}** seni düelloya davet etti, {rakip.mention}!\n\n"
                f"💰 Bahis: `{bahis:,}` Beli\n\n"
                f"Kabul etmek için **Kabul Et** butonuna bas!\n"
                f"_(60 saniye içinde kabul edilmezse iptal olur)_"
            )
        )
        embed.set_thumbnail(url=challenger.display_avatar.url)

        view = DuelAcceptView(challenger, rakip, bahis, self.bot)
        msg = await interaction.response.send_message(
            content=rakip.mention,
            embed=embed,
            view=view
        )

        # 60 saniye timeout
        await asyncio.sleep(60)
        if challenger.id in DUEL_PENDING:
            DUEL_PENDING.pop(challenger.id, None)

class DuelAcceptView(discord.ui.View):
    def __init__(self, challenger, rakip, bahis, bot):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.rakip = rakip
        self.bahis = bahis
        self.bot = bot
        self.done = False

    @discord.ui.button(label="✅ Kabul Et", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.rakip.id:
            await interaction.response.send_message("Bu sana yönelik değil!", ephemeral=True)
            return
        if self.done:
            return
        self.done = True
        DUEL_PENDING.pop(self.challenger.id, None)
        self.stop()
        await run_duel(interaction, self.challenger, self.rakip, self.bahis)

    @discord.ui.button(label="❌ Reddet", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.rakip.id, self.challenger.id]:
            await interaction.response.send_message("Bu sana yönelik değil!", ephemeral=True)
            return
        if self.done:
            return
        self.done = True
        DUEL_PENDING.pop(self.challenger.id, None)
        self.stop()
        embed = error_embed(f"❌ {self.rakip.display_name} düelloyu reddetti.")
        await interaction.response.edit_message(embed=embed, view=None)

async def run_duel(interaction: discord.Interaction, challenger: discord.Member, rakip: discord.Member, bahis: int):
    c_data = get_player(challenger.id)
    r_data = get_player(rakip.id)

    # Güç hesabı: seviye + meyve/silah bonusu + rastgelelik
    def calc_power(player):
        base = player["level"] * 10
        fruit_bonus = 15 if player.get("equipped_fruit") else 0
        weapon_bonus = 10 if player.get("equipped_weapon") else 0
        return base + fruit_bonus + weapon_bonus + random.randint(1, 30)

    c_power = calc_power(c_data)
    r_power = calc_power(r_data)

    if c_power >= r_power:
        winner, loser = challenger, rakip
        w_data, l_data = c_data, r_data
    else:
        winner, loser = rakip, challenger
        w_data, l_data = r_data, c_data

    exp_gain = 40 + (loser == rakip and challenger.id == winner.id) * 10
    w_data, level_msgs = add_exp(w_data, exp_gain)
    w_data["wins"] = w_data.get("wins", 0) + 1
    l_data["losses"] = l_data.get("losses", 0) + 1

    beli_text = ""
    if bahis > 0:
        w_data["beli"] += bahis
        l_data["beli"] -= bahis
        beli_text = f"\n💰 **{winner.display_name}** `{bahis:,}` Beli kazandı!"

    save_player(winner.id, w_data)
    save_player(loser.id, l_data)

    c_fruit = fruit_emoji(c_data.get("equipped_fruit", "")) + f" {c_data.get('equipped_fruit', 'Yok')}" if c_data.get("equipped_fruit") else "❌ Yok"
    r_fruit = fruit_emoji(r_data.get("equipped_fruit", "")) + f" {r_data.get('equipped_fruit', 'Yok')}" if r_data.get("equipped_fruit") else "❌ Yok"

    embed = base_embed(
        title="⚔️ Düello Sonucu!",
        description=(
            f"🏆 **Kazanan: {winner.mention}**\n\n"
            f"```\n"
            f"{challenger.display_name}: {c_power} güç\n"
            f"{rakip.display_name}: {r_power} güç\n"
            f"```"
            f"+ `{exp_gain}` EXP kazanıldı!{beli_text}"
        )
    )
    embed.add_field(name=f"{challenger.display_name}", value=f"Meyve: {c_fruit}\nSeviye: {c_data['level']}", inline=True)
    embed.add_field(name="VS", value="⚔️", inline=True)
    embed.add_field(name=f"{rakip.display_name}", value=f"Meyve: {r_fruit}\nSeviye: {r_data['level']}", inline=True)

    if level_msgs:
        embed.add_field(name="🎉 Level Up!", value="\n".join(level_msgs), inline=False)

    await interaction.response.edit_message(embed=embed, view=None)

async def setup(bot):
    await bot.add_cog(Duel(bot))
