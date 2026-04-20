import pandas as pd

print("Data Preprocessing başlatılıyor...")

# 1. PhishTank verisini işleme (Zararlı / Label: 1)
# Sadece 'url' sütununu okuyup adını 'URL' yapıyoruz
df_phish = pd.read_csv('../data/phishtank.csv', usecols=['url'])
df_phish = df_phish.rename(columns={'url': 'URL'})
df_phish['Label'] = 1
print(f"PhishTank verisi yüklendi: {len(df_phish)} satır.")

# 2. Tranco verisini işleme (Temiz / Label: 0)
# Görsele göre başlık satırı yok ve veriler virgülle ayrılmış.
df_clean = pd.read_csv('../data/trancolist.csv', header=None, names=['URL', 'Label'])
df_clean['Label'] = 0 # Hata payını sıfırlamak için label'ı kesin olarak 0 yapıyoruz
print(f"Tranco verisi yüklendi: {len(df_clean)} satır.")

# 3. İki verisetini birleştirme (Master Dataset)
df_master = pd.concat([df_phish, df_clean], ignore_index=True)

# 4. Verileri karıştırma (Shuffling)
# Modelin sürekli 1'leri okuyup sonra 0'lara geçmesini engellemek için satırları karıştırıyoruz
df_master = df_master.sample(frac=1, random_state=42).reset_index(drop=True)

# 5. Sonucu yeni bir CSV olarak kaydetme
df_master.to_csv('../data/master_dataset.csv', index=False)

print("\nİşlem Başarılı! Master Dataset oluşturuldu.")
print("Veri Seti Önizlemesi:")
print(df_master.head())