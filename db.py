import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "../data/db.json")

FRUITS = [
    "Gomu Gomu", "Mera Mera", "Hie Hie", "Quake Quake", "Yami Yami",
    "Pika Pika", "Magu Magu", "Gura Gura", "Ope Ope", "Ito Ito",
    "Zushi Zushi", "Tori Tori", "Soru Soru", "Bari Bari", "Noro Noro",
    "Doku Doku", "Kage Kage", "Horo Horo", "Suke Suke", "Nikyu Nikyu",
    "Gasu Gasu", "Fude Fude", "Ton Ton", "Nui Nui", "Bisu Bisu",
    "Shiro Shiro", "Yuki Yuki", "Numa Numa", "Jake Jake", "Pero Pero",
    "Buku Buku", "Ryu Ryu", "Tama Tama", "Mochi Mochi", "Wara Wara",
    "Soru Soru (Mythical)", "Uo Uo", "Juku Juku"
]

WEAPONS = [
    "Cutlass", "Iron Mace", "Dual Katana", "Saber", "Dark Blade",
    "Dragon Trident", "Pole v2", "Shark Anchor", "True Triple Katana",
    "Gravity Cane", "Serpent Bow", "Soul Guitar", "Canvander",
    "Hallow Scythe", "Midnight Blade"
]

ENEMIES = [
    {"name": "Pirate", "min_exp": 10, "max_exp": 25, "min_beli": 50, "max_beli": 150, "drop_chance": 5},
    {"name": "Marine", "min_exp": 15, "max_exp": 35, "min_beli": 80, "max_beli": 200, "drop_chance": 8},
    {"name": "Sky Bandit", "min_exp": 30, "max_exp": 60, "min_beli": 150, "max_beli": 350, "drop_chance": 12},
    {"name": "Dark Master", "min_exp": 50, "max_exp": 100, "min_beli": 300, "max_beli": 700, "drop_chance": 18},
    {"name": "Raid Boss", "min_exp": 100, "max_exp": 200, "min_beli": 600, "max_beli": 1500, "drop_chance": 30},
]

SHOP_ITEMS = {
    "Gomu Gomu": 500,
    "Mera Mera": 800,
    "Hie Hie": 700,
    "Quake Quake": 1200,
    "Pika Pika": 1000,
    "Cutlass": 200,
    "Iron Mace": 150,
    "Saber": 600,
    "Dual Katana": 900,
}

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_player(user_id: int) -> dict:
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {
            "level": 1,
            "exp": 0,
            "beli": 100,
            "fruits": [],
            "weapons": ["Cutlass"],
            "equipped_fruit": None,
            "equipped_weapon": "Cutlass",
            "kills": 0,
            "last_daily": None,
            "wins": 0,
            "losses": 0,
        }
        save_db(db)
    return db[uid]

def save_player(user_id: int, data: dict):
    db = load_db()
    db[str(user_id)] = data
    save_db(db)

def exp_to_next_level(level: int) -> int:
    return level * 100

def add_exp(player: dict, amount: int) -> tuple[dict, list[str]]:
    """EXP ekle, level atlamayı kontrol et. (player, mesajlar) döner."""
    messages = []
    player["exp"] += amount
    while player["exp"] >= exp_to_next_level(player["level"]):
        player["exp"] -= exp_to_next_level(player["level"])
        player["level"] += 1
        messages.append(f"🎉 **Level {player['level']}** oldun!")
    return player, messages
