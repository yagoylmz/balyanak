import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# 1. Token'ı yükle
load_dotenv()

# 2. İzinleri ayarla
intents = discord.Intents.default()
intents.message_content = True

# 3. Botu Tanımla (İşte 'bot' burada tanımlanıyor, hata çözüldü)
bot = commands.Bot(command_prefix='!', intents=intents)

# 4. Bot Açılınca Ne Yapsın? (Balyanak Ayarları)
@bot.event
async def on_ready():
    print(f'---------------------------------------------------')
    print(f'Giriş Yapıldı: {bot.user} (ID: {bot.user.id})')
    print(f'Antigravity Systems: Online 🚀')
    print(f'---------------------------------------------------')

    # Durum Mesajı Ayarı (Senin istediğin)
    activity = discord.Activity(
        type=discord.ActivityType.listening, 
        name="!balyanak | Müziğin Tadı 🍯"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

# 5. Ana Çalıştırma Fonksiyonu
async def main():
    # Müzik modülünü (cogs/music.py) yükle
    try:
        await bot.load_extension('cogs.music')
        print(">> Müzik Modülü (cogs.music) Başarıyla Yüklendi ✅")
    except Exception as e:
        print(f"!! Modül Yüklenirken Hata: {e}")

    # Token kontrolü ve başlatma
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("HATA: .env dosyasında DISCORD_TOKEN bulunamadı!")
        return

    await bot.start(token)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Kapatılırken hata vermesin
        pass