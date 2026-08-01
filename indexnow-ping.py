#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
indexnow_ping.py — sitemap.xml'deki tüm URL'leri IndexNow protokolüne bildirir.
Bing, Yandex, Seznam.cz gibi motorlar bu tek istekten haberdar olur.
Google bu protokolü desteklemez (Search Console/robots.txt üzerinden ayrı çalışır).

Çalışma mantığı:
1. CNAME dosyasından domaini okur
2. sitemap.xml'i okuyup içindeki tüm <loc> URL'lerini çıkarır
3. IndexNow API'sine tek bir istekte tüm listeyi gönderir

Gerekli: aynı klasörde CNAME, sitemap.xml ve <key>.txt dosyaları bulunmalı.
"""
import os, re, json, urllib.request, urllib.error

INDEXNOW_KEY = "f34738eb8841c713f5ee04804f7aa471"

def get_domain():
    if os.path.exists("CNAME"):
        with open("CNAME") as f:
            return f.read().strip()
    return None

def get_sitemap_urls():
    if not os.path.exists("sitemap.xml"):
        return []
    with open("sitemap.xml", encoding="utf-8") as f:
        content = f.read()
    return re.findall(r"<loc>(.*?)</loc>", content)

def main():
    domain = get_domain()
    if not domain:
        print("CNAME bulunamadı, IndexNow atlanıyor.")
        return

    urls = get_sitemap_urls()
    if not urls:
        print("sitemap.xml boş veya bulunamadı, IndexNow atlanıyor.")
        return

    payload = {
        "host": domain,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{domain}/{INDEXNOW_KEY}.txt",
        "urlList": urls
    }

    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"IndexNow: {domain} — {len(urls)} URL bildirildi. Durum: {resp.status}")
    except urllib.error.HTTPError as e:
        # IndexNow başarı durumunda 200 veya 202 döner; diğer kodlar sorunu işaret eder.
        print(f"IndexNow HATA: {domain} — HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"IndexNow HATA: {domain} — {e}")

if __name__ == "__main__":
    main()
