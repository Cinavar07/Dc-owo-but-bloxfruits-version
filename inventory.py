import discord
from discord.ext import commands
from discord import app_commands
from utils.db import get_player, save_player
from utils.embeds import base_embed, error_embed, success_embed, fruit_emoji

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="Meyve ve silah envanterini görüntüle")
    async def inventory(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)

        fruits = player["fruits"]
        weapons = player["weapons"]
        equipped_fruit = player.get("equipped_fruit")
        equipped_weapon = player.get("equipped_weapon")

        fruit_list = "\n".join(
            [f"{fruit_emoji(f)} `{f}`{'  ✅ **Equipped**' if f == equipped_fruit else ''}" for f in fruits]
        ) or "❌ Hiç meyven yok"

        weapon_list = "\n".join(
            [f"⚔️ `{w}`{'  ✅ **Equipped**' if w == equipped_weapon else ''}" for w in weapons]
        ) or "❌ Hiç silahın yok"

        embed = base_embed(
            title=f"🎒 {interaction.user.display_name} — Envanter"
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name=f"🍎 Meyveler ({len(fruits)})", value=fruit_list, inline=False)
        embed.add_field(name=f"⚔️ Silahlar ({len(weapons)})", value=weapon_list, inline=False)

        # Equip butonları
        view = InventoryView(player, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="equip", description="Meyve veya silah kuşan")
    @app_commands.describe(tip="fruit veya weapon", isim="Kuşanılacak item adı")
    @app_commands.choices(tip=[
        app_commands.Choice(name="Meyve", value="fruit"),
        app_commands.Choice(name="Silah", value="weapon"),
    ])
    async def equip(self, interaction: discord.Interaction, tip: str, isim: str):
        player = get_player(interaction.user.id)

        if tip == "fruit":
            if isim not in player["fruits"]:
                await interaction.response.send_message(
                    embed=error_embed(f"Bu meyveye sahip değilsin: `{isim}`"),
                    ephemeral=True
                )
                return
            player["equipped_fruit"] = isim
            save_player(interaction.user.id, player)
            await interaction.response.send_message(
                embed=success_embed("Meyve Kuşanıldı", f"{fruit_emoji(isim)} `{isim}` kuşanıldı!")
            )
        else:
            if isim not in player["weapons"]:
                await interaction.response.send_message(
                    embed=error_embed(f"Bu silaha sahip değilsin: `{isim}`"),
                    ephemeral=True
                )
                return
            player["equipped_weapon"] = isim
            save_player(interaction.user.id, player)
            await interaction.response.send_message(
                embed=success_embed("Silah Kuşanıldı", f"⚔️ `{isim}` kuşanıldı!")
            )

class InventoryView(discord.ui.View):
    def __init__(self, player, user_id):
        super().__init__(timeout=60)
        self.player = player
        self.user_id = user_id

    @discord.ui.button(label="🍎 Meyve Kuşan", style=discord.ButtonStyle.primary)
    async def equip_fruit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Bu senin envantern değil!", ephemeral=True)
            return
        if not self.player["fruits"]:
            await interaction.response.send_message(embed=error_embed("Hiç meyven yok!"), ephemeral=True)
            return
        select = FruitSelect(self.player, self.user_id)
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message("Hangi meyveyi kuşanmak istiyorsun?", view=view, ephemeral=True)

    @discord.ui.button(label="⚔️ Silah Kuşan", style=discord.ButtonStyle.secondary)
    async def equip_weapon(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Bu senin envantern değil!", ephemeral=True)
            return
        select = WeaponSelect(self.player, self.user_id)
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message("Hangi silahı kuşanmak istiyorsun?", view=view, ephemeral=True)

class FruitSelect(discord.ui.Select):
    def __init__(self, player, user_id):
        self.user_id = user_id
        options = [
            discord.SelectOption(label=f[:25], value=f, emoji="🍎")
            for f in player["fruits"][:25]
        ]
        super().__init__(placeholder="Meyve seç...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Bu senin envantern değil!", ephemeral=True)
            return
        player = get_player(interaction.user.id)
        player["equipped_fruit"] = self.values[0]
        save_player(interaction.user.id, player)
        await interaction.response.send_message(
            embed=success_embed("Meyve Kuşanıldı", f"{fruit_emoji(self.values[0])} `{self.values[0]}` kuşanıldı!"),
            ephemeral=True
        )

class WeaponSelect(discord.ui.Select):
    def __init__(self, player, user_id):
        self.user_id = user_id
        options = [
            discord.SelectOption(label=w[:25], value=w, emoji="⚔️")
            for w in player["weapons"][:25]
        ]
        super().__init__(placeholder="Silah seç...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Bu senin envantern değil!", ephemeral=True)
            return
        player = get_player(interaction.user.id)
        player["equipped_weapon"] = self.values[0]
        save_player(interaction.user.id, player)
        await interaction.response.send_message(
            embed=success_embed("Silah Kuşanıldı", f"⚔️ `{self.values[0]}` kuşanıldı!"),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Inventory(bot))
