import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
import spotipy
import random
from spotipy.oauth2 import SpotifyClientCredentials

# --- 1. SPOTIFY AYARLARI ---
try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv('SPOTIPY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
    ))
    SPOTIFY_ENABLED = True
except:
    SPOTIFY_ENABLED = False
    print(">> UYARI: Spotify API eksik. Sadece YouTube modunda çalışacak.")

# --- 2. YOUTUBE VE FFMEG AYARLARI ---
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

# Network hatalarına karşı daha dirençli ayarlar
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 10M -analyzeduration 10M',
    'options': '-vn',
}

FFMPEG_FILTERS = {
    'normal': {},
    'bass': {'options': '-vn -af bass=g=20'},
    'nightcore': {'options': '-vn -af asetrate=48000*1.25,aresample=48000'},
    'slowed': {'options': '-vn -af asetrate=48000*0.8,aresample=48000,aecho=0.8:0.9:1000:0.3'},
    '8d': {'options': '-vn -af apulsator=hz=0.125'},
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, filter_type='normal'):
        loop = loop or asyncio.get_event_loop()
        
        if not url.startswith("http"): url = f"ytsearch:{url}"
        
        # Blocking (Bloklayan) işlemi Executor'a taşıdık
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data: data = data['entries'][0]
        
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        
        current_opts = FFMPEG_OPTIONS.copy()
        if filter_type in FFMPEG_FILTERS:
            current_opts.update(FFMPEG_FILTERS[filter_type])

        return cls(discord.FFmpegPCMAudio(filename, **current_opts), data=data)

# --- 3. UI KISMI ---
class SongRequestModal(discord.ui.Modal, title="Şarkı İste"):
    song_name = discord.ui.TextInput(label="Ne Çalalım?", placeholder="Link veya İsim...", required=True)
    def __init__(self, music_cog, ctx):
        super().__init__()
        self.music_cog = music_cog
        self.ctx = ctx
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🔍 **{self.song_name.value}** işleniyor...", ephemeral=True)
        await self.music_cog.play(self.ctx, search=self.song_name.value)

class FilterSelect(discord.ui.Select):
    def __init__(self, music_cog, ctx):
        options = [
            discord.SelectOption(label="Normal", emoji="💿"),
            discord.SelectOption(label="Bassboost", emoji="🔥"),
            discord.SelectOption(label="Nightcore", emoji="⚡"),
            discord.SelectOption(label="Slowed", emoji="🌙"),
            discord.SelectOption(label="8D Audio", emoji="🎧"),
        ]
        super().__init__(placeholder="🎛️ Efekt Seç...", min_values=1, max_values=1, options=options, row=2)
        self.music_cog = music_cog
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0].lower().split(" ")[0]
        code = "bass" if "bass" in val else "nightcore" if "night" in val else "slowed" if "slow" in val else "8d" if "8d" in val else "normal"
        self.music_cog.current_filter = code
        await interaction.response.send_message(f"🎛️ Efekt: **{self.values[0]}** (Sonraki şarkıda aktif)", ephemeral=True)

class MusicControlView(discord.ui.View):
    def __init__(self, music_cog, ctx):
        super().__init__(timeout=None)
        self.music_cog = music_cog
        self.ctx = ctx
        self.add_item(FilterSelect(music_cog, ctx))

    @discord.ui.button(label="Çal", style=discord.ButtonStyle.green, emoji="▶️", row=0)
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SongRequestModal(self.music_cog, self.ctx))

    # --- YENİ EKLENEN BUTON: DURAKLAT/DEVAM ---
    @discord.ui.button(label="Dur/Devam", style=discord.ButtonStyle.blurple, emoji="⏯️", row=0)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc:
            return await interaction.response.send_message("⚠️ Bir kanalda değilim.", ephemeral=True)
        
        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Müzik duraklatıldı.", ephemeral=True)
        elif vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Müzik devam ediyor.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Şu an çalan bir şey yok.", ephemeral=True)
    
    @discord.ui.button(label="Geç", style=discord.ButtonStyle.primary, emoji="⏭️", row=0)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.music_cog.skip(self.ctx)
        if not interaction.response.is_done(): await interaction.response.defer()

    @discord.ui.button(label="Döngü", style=discord.ButtonStyle.secondary, emoji="🔁", row=1)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.music_cog.loop_command(self.ctx)
        if not interaction.response.is_done(): await interaction.response.defer()

    @discord.ui.button(label="Karıştır", style=discord.ButtonStyle.secondary, emoji="🔀", row=1)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.music_cog.shuffle_command(self.ctx)
        if not interaction.response.is_done(): await interaction.response.defer()

    @discord.ui.button(label="Kuyruk", style=discord.ButtonStyle.gray, emoji="📜", row=1)
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.music_cog.queue_command(self.ctx)
        if not interaction.response.is_done(): await interaction.response.defer()

    @discord.ui.button(label="Çıkış", style=discord.ButtonStyle.red, emoji="⏹️", row=1)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.music_cog.leave(self.ctx)
        if not interaction.response.is_done(): await interaction.response.defer()

# --- 4. ANA MÜZİK MANTIĞI ---
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []      
        self.is_playing = False
        self.loop = False 
        self.current_filter = "normal"

    def play_next(self, ctx):
        if len(self.queue) > 0:
            self.is_playing = True
            
            if self.loop and hasattr(self, 'current_song_data'):
                 self.queue.append(self.current_song_data)

            next_song = self.queue.pop(0)
            self.current_song_data = next_song 
            
            query = next_song['query']
            display_title = next_song.get('title', query)
            
            self.bot.loop.create_task(self.play_music_async(ctx, query, display_title))
        else:
            self.is_playing = False
            asyncio.run_coroutine_threadsafe(ctx.send("✅ Kuyruk bitti. Sessizlik..."), self.bot.loop)

    async def play_music_async(self, ctx, query, display_title):
        try:
            msg = await ctx.send(f"💿 Hazırlanıyor: **{display_title}**...")

            source = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True, filter_type=self.current_filter)
            if not ctx.voice_client: return

            ctx.voice_client.play(source, after=lambda e: self.play_next(ctx))
            
            loop_icon = "🔁" if self.loop else ""
            filter_tag = f" | 🎛️ {self.current_filter.capitalize()}" if self.current_filter != "normal" else ""
            await msg.edit(content=f"🎶 Şimdi Çalıyor: **{source.title}** {loop_icon}{filter_tag}")
            
        except Exception as e:
            await ctx.send(f"⚠️ Hata oluştu ({display_title}), sıradaki şarkıya geçiliyor...")
            print(f"Hata Detayı: {e}")
            self.play_next(ctx)

    # --- YARDIMCI FONKSIYON: SPOTIFY VERİSİNİ ARKA PLANDA ÇEKME ---
    def fetch_spotify_tracks(self, search):
        """Bu fonksiyon Spotify verisini çekerken botu dondurmaz."""
        tracks_to_add = []
        try:
            if "track" in search:
                tracks_to_add.append(sp.track(search))
            elif "playlist" in search:
                results = sp.playlist_tracks(search)
                tracks = results['items']
                while results['next']:
                    results = sp.next(results)
                    tracks.extend(results['items'])
                tracks_to_add = [t['track'] for t in tracks if t['track']]
            elif "album" in search:
                results = sp.album_tracks(search)
                tracks_to_add = results['items']
                while results['next']:
                    results = sp.next(results)
                    tracks_to_add.extend(results['items'])
            return tracks_to_add
        except Exception as e:
            print(f"Spotify Fetch Hatası: {e}")
            return []

    # --- KOMUTLAR ---
    @commands.command(name='balyanak')
    async def balyanak_panel(self, ctx):
        """Ana Paneli Açar"""
        embed = discord.Embed(title="🍯 Balyanak Kontrol", description="Duraklat/Devam Eklendi! ⏯️", color=discord.Color.gold())
        if self.bot.user.avatar: embed.set_thumbnail(url=self.bot.user.avatar.url)
        view = MusicControlView(self, ctx)
        await ctx.send(embed=embed, view=view)

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice: return await ctx.send("❌ Sese gir!")
        if not ctx.voice_client: await ctx.author.voice.channel.connect()

        async with ctx.typing():
            tracks_added = 0
            
            # --- SPOTIFY (OPTIMIZED) ---
            if "spotify.com" in search and SPOTIFY_ENABLED:
                # Bloklayan işlemi 'executor' ile arka plana atıyoruz. Bot donmuyor.
                tracks = await self.bot.loop.run_in_executor(None, lambda: self.fetch_spotify_tracks(search))
                
                if tracks:
                    for track in tracks:
                        query = f"{track['name']} {track['artists'][0]['name']} audio"
                        self.queue.append({'query': query, 'title': track['name']})
                        tracks_added += 1
                    await ctx.send(f"✅ Spotify'dan **{tracks_added}** şarkı eklendi!")
                else:
                    await ctx.send("❌ Spotify verisi çekilemedi.")

            # --- YOUTUBE PLAYLIST ---
            elif "list=" in search:
                try:
                    flat_opts = {'extract_flat': True, 'noplaylist': False, 'quiet': True, 'ignoreerrors': True}
                    with yt_dlp.YoutubeDL(flat_opts) as ydl:
                        info = await self.bot.loop.run_in_executor(None, lambda: ydl.extract_info(search, download=False))
                    if 'entries' in info:
                        for entry in info['entries']:
                            if entry:
                                url = entry.get('url')
                                if len(url) == 11: url = f"https://www.youtube.com/watch?v={url}"
                                self.queue.append({'query': url, 'title': entry.get('title', 'Video')})
                                tracks_added += 1
                        await ctx.send(f"✅ YouTube Playlist (**{tracks_added}** şarkı) eklendi.")
                except Exception as e:
                    await ctx.send(f"❌ Playlist Hatası: {e}")

            # --- NORMAL ---
            else:
                self.queue.append({'query': search, 'title': search})
                await ctx.send(f"✅ Kuyrukta: **{search}**")

            # BAŞLAT
            if not ctx.voice_client.is_playing() and not self.is_playing:
                self.play_next(ctx)

    @commands.command(name='skip', aliases=['s'])
    async def skip(self, ctx):
        if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            await ctx.send("⏭️ Geçiliyor...")
            ctx.voice_client.stop()
        else:
            await ctx.send("⚠️ Çalan yok.")

    @commands.command(name='pause')
    async def pause_command(self, ctx):
        """Müziği duraklatır."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Duraklatıldı.")
        elif ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Devam ediliyor.")

    @commands.command(name='loop')
    async def loop_command(self, ctx):
        self.loop = not self.loop
        status = "🔁 AÇIK" if self.loop else "➡️ KAPALI"
        await ctx.send(f"**Döngü Modu:** {status}")

    @commands.command(name='shuffle')
    async def shuffle_command(self, ctx):
        if len(self.queue) < 2: return await ctx.send("⚠️ Yetersiz şarkı.")
        random.shuffle(self.queue)
        await ctx.send("🔀 **Kuyruk karıştırıldı!**")

    @commands.command(name='queue', aliases=['q'])
    async def queue_command(self, ctx):
        if not self.queue: return await ctx.send("Kuyruk boş.")
        lines = [f"{i+1}. {s['title']}" for i, s in enumerate(self.queue[:15])]
        footer = f"\n... ve {len(self.queue)-15} şarkı daha" if len(self.queue) > 15 else ""
        await ctx.send(f"**📜 Kuyruk:**\n" + "\n".join(lines) + footer)

    @commands.command(name='leave', aliases=['disconnect'])
    async def leave(self, ctx):
        if ctx.voice_client:
            self.queue.clear()
            await ctx.voice_client.disconnect()
            self.is_playing = False
            self.loop = False
            self.current_filter = "normal"

async def setup(bot):
    await bot.add_cog(Music(bot))