import discord
from discord.ext import commands
from discord import app_commands
from utils.db import get_player, save_player, SHOP_ITEMS
from utils.embeds import base_embed, error_embed, success_embed, fruit_emoji

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shop", description="Meyve ve silah dükkânı")
    async def shop(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)

        embed = base_embed(
            title="🏪 Blox Fruits Dükkânı",
            description=f"💰 Beliniz: `{player['beli']:,}`\n\nBir item seçmek için aşağıdaki menüyü kullan!"
        )

        fruits_in_shop = {k: v for k, v in SHOP_ITEMS.items() if k in [
            "Gomu Gomu", "Mera Mera", "Hie Hie", "Quake Quake", "Pika Pika"
        ]}
        weapons_in_shop = {k: v for k, v in SHOP_ITEMS.items() if k in [
            "Cutlass", "Iron Mace", "Saber", "Dual Katana"
        ]}

        fruit_text = "\n".join([f"{fruit_emoji(k)} `{k}` — **{v:,}** Beli" for k, v in fruits_in_shop.items()])
        weapon_text = "\n".join([f"⚔️ `{k}` — **{v:,}** Beli" for k, v in weapons_in_shop.items()])

        embed.add_field(name="🍎 Meyveler", value=fruit_text, inline=False)
        embed.add_field(name="⚔️ Silahlar", value=weapon_text, inline=False)

        view = ShopView(player, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

class ShopView(discord.ui.View):
    def __init__(self, player, user_id):
        super().__init__(timeout=60)
        self.player = player
        self.user_id = user_id

    @discord.ui.button(label="🍎 Meyve Al", style=discord.ButtonStyle.primary)
    async def buy_fruit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Bu senin dükkânın değil!", ephemeral=True)
            return
        select = ShopSelect("fruit", self.user_id)
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message("Hangi meyveyi satın almak istiyorsun?", view=view, ephemeral=True)

    @discord.ui.button(label="⚔️ Silah Al", style=discord.ButtonStyle.secondary)
    async def buy_weapon(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Bu senin dükkânın değil!", ephemeral=True)
            return
        select = ShopSelect("weapon", self.user_id)
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message("Hangi silahı satın almak istiyorsun?", view=view, ephemeral=True)

class ShopSelect(discord.ui.Select):
    def __init__(self, item_type: str, user_id: int):
        self.item_type = item_type
        self.user_id = user_id

        fruits = ["Gomu Gomu", "Mera Mera", "Hie Hie", "Quake Quake", "Pika Pika"]
        weapons = ["Cutlass", "Iron Mace", "Saber", "Dual Katana"]

        if item_type == "fruit":
            options = [
                discord.SelectOption(
                    label=f[:25],
                    value=f,
                    description=f"{SHOP_ITEMS[f]:,} Beli",
                    emoji="🍎"
                ) for f in fruits
            ]
        else:
            options = [
                discord.SelectOption(
                    label=w[:25],
                    value=w,
                    description=f"{SHOP_ITEMS[w]:,} Beli",
                    emoji="⚔️"
                ) for w in weapons
            ]

        super().__init__(placeholder="Seç...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Bu senin dükkânın değil!", ephemeral=True)
            return

        item = self.values[0]
        price = SHOP_ITEMS[item]
        player = get_player(interaction.user.id)

        if player["beli"] < price:
            await interaction.response.send_message(
                embed=error_embed(f"Yetersiz Beli! Gerekli: `{price:,}`, Mevcut: `{player['beli']:,}`"),
                ephemeral=True
            )
            return

        if self.item_type == "fruit":
            if item in player["fruits"]:
                await interaction.response.send_message(
                    embed=error_embed(f"Bu meyveye zaten sahipsin: `{item}`"),
                    ephemeral=True
                )
                return
            player["fruits"].append(item)
            icon = fruit_emoji(item) + " "
        else:
            if item in player["weapons"]:
                await interaction.response.send_message(
                    embed=error_embed(f"Bu silaha zaten sahipsin: `{item}`"),
                    ephemeral=True
                )
                return
            player["weapons"].append(item)
            icon = "⚔️ "

        player["beli"] -= price
        save_player(interaction.user.id, player)

        await interaction.response.send_message(
            embed=success_embed(
                "Satın Alındı!",
                f"{icon}`{item}` satın alındı!\n💰 Kalan Beli: `{player['beli']:,}`"
            ),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Shop(bot))
