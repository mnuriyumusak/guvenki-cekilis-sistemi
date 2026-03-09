import pandas as pd
import requests
import random
import datetime
import time

# --- AYARLAR ---
DRAND_API_URL = "https://api.drand.sh/public/"
# Drand Mainnet Genesis Zamanı (Unix Timestamp) ve Periyodu (30sn)
GENESIS_TIME = 1595431050 
PERIOD = 30

def get_drand_round_from_time(target_time_str):
    """Verilen zamanı Drand Round numarasına çevirir."""
    # Zaman formatı: "01-03-2026 13:00:00"
    dt = datetime.datetime.strptime(target_time_str, "%d-%m-%Y %H:%M:%S")
    target_timestamp = time.mktime(dt.timetuple())
    
    if target_timestamp < GENESIS_TIME:
        raise ValueError("Zaman Drand başlangıcından (2020) önce olamaz.")
    
    drand_round = int((target_timestamp - GENESIS_TIME) / PERIOD) + 1
    return drand_round

def fetch_drand_randomness(drand_round):
    """Belirli bir round numarasının rastgele değerini API'den çeker."""
    url = f"{DRAND_API_URL}{drand_round}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Drand API hatası! Henüz bu zaman gelmemiş olabilir. Kod: {response.status_code}")
    
    data = response.json()
    return data['randomness']

def conduct_lottery(csv_file, target_time, winner_count):
    # 1. Listeyi yükle
    df = pd.read_csv(csv_file)
    
    # 2. Listeyi sabitle (Alfabetik sırala)
    # Bu adım hileyi önler; herkesin listeyi aynı sırada işlemesini sağlar.
    df = df.sort_values(by=df.columns[0]).reset_index(drop=True)
    participants = df.values.tolist()
    
    # 3. Drand Round hesapla ve Seed'i çek
    drand_round = get_drand_round_from_time(target_time)
    print(f"Hesaplanan Drand Round: {drand_round}")
    
    seed = fetch_drand_randomness(drand_round)
    print(f"Kullanılan Seed (Rastgelelik): {seed}")
    
    # 4. Seçimi yap (Deterministik Rastgelelik)
    # Aynı seed ve aynı liste, her bilgisayarda AYNI sonucu verir.
    random.seed(seed)
    winners = random.sample(participants, min(winner_count, len(participants)))
    
    # 5. Sonuçları Kaydet
    winners_df = pd.DataFrame(winners, columns=df.columns)
    winners_df.to_csv("kazananlar.csv", index=False)
    print(f"\nÇekiliş tamamlandı! {len(winners)} kazanan 'kazananlar.csv' dosyasına yazıldı.")

# --- KULLANIM ÖRNEĞİ ---
if __name__ == "__main__":
    # Örnek Parametreler
    input_csv = "katilimcilar.csv"  # Katılımcı listesi dosyası
    cekilis_zamani = "01-03-2026 13:00:00" # GG-AA-YYYY SS:DD:SS
    kisi_sayisi = 10000 # Seçilecek kişi sayısı
    
    try:
        conduct_lottery(input_csv, cekilis_zamani, kisi_sayisi)
    except Exception as e:
        print(f"Hata: {e}")