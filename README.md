# 🍎 Blox Fruits Discord Botu

Blox Fruits temalı eğlence & RPG botu. Python + discord.py ile yazılmıştır.

## 📁 Dosya Yapısı
```
bloxbot/
├── bot.py              → Ana bot dosyası
├── requirements.txt    → Bağımlılıklar
├── config.json         → Bot ayarları
├── data/
│   └── db.json         → Oyuncu verileri (otomatik oluşur)
├── utils/
│   ├── db.py           → Veri yönetimi
│   └── embeds.py       → Embed yardımcıları
└── cogs/
    ├── profile.py      → /profile komutu
    ├── hunt.py         → /hunt komutu
    ├── inventory.py    → /inventory & /equip
    ├── daily.py        → /daily komutu
    ├── shop.py         → /shop komutu
    └── duel.py         → /duel komutu
```

## 🚀 Kurulum

### 1. Bağımlılıkları yükle
```bash
pip install -r requirements.txt
```

### 2. Token ayarla
**Linux/Mac:**
```bash
export DISCORD_TOKEN=botun_tokeni_buraya
```
**Windows:**
```cmd
set DISCORD_TOKEN=botun_tokeni_buraya
```

### 3. Botu başlat
```bash
python bot.py
```

## 🎮 Komutlar

| Komut | Açıklama |
|-------|----------|
| `/profile` | Blox Fruits profilini görüntüle |
| `/hunt` | Düşman avla, EXP & Beli kazan (30s cooldown) |
| `/inventory` | Meyve ve silah envanterini gör, kuşan |
| `/equip` | Meyve veya silah kuşan |
| `/daily` | Günlük ödülü al (24s bekleme) |
| `/shop` | Meyve & silah satın al |
| `/duel @kişi` | Düello meydan oku (isteğe bağlı bahis) |

## 🍎 Özellikler
- **38 farklı meyve** (Common → Mythical)
- **15 farklı silah**
- **5 düşman tipi** (seviyeye göre artar)
- **Seviye sistemi** (EXP & Level Up)
- **Beli ekonomisi**
- **Drop sistemi** (hunt'ta şans eseri item)
- **Düello sistemi** (bahisli/bahissiz)
- **Günlük ödül** sistemi
- **Discord UI** (Button & Select menüleri)

## ⚙️ Discord Developer Portal Ayarları
Bot için şu izinleri aktif et:
- `MESSAGE CONTENT INTENT`
- `SERVER MEMBERS INTENT`
- `GUILDS`

Bot izinleri: `Send Messages`, `Embed Links`, `Manage Channels`
