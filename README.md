# 🍯 Balyanak Discord Music Bot

<p align="center">
  <img src="https://media.discordapp.net/attachments/YOUR_IMAGE_LINK_HERE.png" alt="Balyanak Banner" width="100%" />
</p>

<p align="center">
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version"></a>
    <a href="https://discordpy.readthedocs.io/en/stable/"><img src="https://img.shields.io/badge/Library-Discord.py%202.0+-7289DA.svg" alt="Discord.py"></a>
    <a href="https://github.com/yt-dlp/yt-dlp"><img src="https://img.shields.io/badge/Audio-yt--dlp-red.svg" alt="yt-dlp"></a>
    <a href="https://ffmpeg.org/"><img src="https://img.shields.io/badge/Backend-FFmpeg-green.svg" alt="FFmpeg"></a>
</p>

**Balyanak**, Python ve modern asenkron programlama teknikleri kullanılarak geliştirilmiş, yüksek performanslı ve hibrit kontrollü (UI + Komut) bir Discord müzik botudur. 

Spotify, YouTube ve SoundCloud entegrasyonları sayesinde kesintisiz müzik deneyimi sunar. Gelişmiş **"Lazy Loading"** algoritması ile 500+ şarkılık çalma listelerini saniyeler içinde işler.

---

## 🚀 Özellikler (Features)

### 🎧 Gelişmiş Müzik Deneyimi
* **Çapraz Platform Desteği:** YouTube (Video/Playlist), Spotify (Track/Album/Playlist) ve SoundCloud desteği.
* **Akıllı Arama:** Link olmasa bile şarkı ismini YouTube'da en doğru sonuçla eşleştirir.
* **Ses Efektleri (Filters):** Gerçek zamanlı FFmpeg filtreleme.
    * 🔥 **Bassboost**
    * ⚡ **Nightcore**
    * 🌙 **Slowed + Reverb**
    * 🎧 **8D Audio**

### 💻 Teknik Yetenekler
* **Hibrit Kontrol Arayüzü:** `!balyanak` komutu ile açılan interaktif butonlar, açılır menüler (dropdowns) ve modallar.
* **Non-Blocking (Asenkron) Mimari:** Spotify API çağrıları ve veri işleme süreçleri ana döngüyü (Event Loop) kilitlemeden arka planda (Executor) çalışır.
* **Memory Optimization:** Kuyruk sistemi RAM dostu olacak şekilde optimize edilmiştir.
* **Auto-Recovery:** Oynatma hatalarında bot çökmez, kullanıcıyı bilgilendirip otomatik olarak bir sonraki şarkıya geçer.

---

## 🛠️ Kurulum (Installation)

Projeyi kendi bilgisayarınızda veya sunucunuzda çalıştırmak için adımları izleyin.

### Gereksinimler
* Python 3.8 veya üzeri
* FFmpeg (Sisteme kurulu ve PATH'e ekli olmalı)
* Discord Bot Token
* Spotify API Credentials (ID & Secret)

### 1. Projeyi Klonlayın
```bash
git clone [https://github.com/kullaniciadin/balyanak.git](https://github.com/kullaniciadin/balyanak.git)
cd balyanak
