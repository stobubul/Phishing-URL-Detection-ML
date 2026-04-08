import pandas as pd
import requests
import zipfile
import io

def get_clean_urls(sample_size=50000):
    print("Tranco List (Clean URLs) indiriliyor...")
    # Tranco'nun her gün güncellenen güncel Top 1M listesinin direkt indirme linki
    url = "https://tranco-list.eu/top-1m.csv.zip"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Zip dosyasını bellekte açıyoruz
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Zip içindeki csv dosyasının adını alıyoruz
            csv_filename = z.namelist()[0]
            with z.open(csv_filename) as f:
                # Tranco listesinde sütun başlığı yoktur: [Sıra, Domain] şeklindedir
                df = pd.read_csv(f, header=None, names=['Rank', 'URL'])
                
        # Sadece URL sütununu alıyoruz
        clean_df = df[['URL']].copy()
        
        # Modelin Phishing bağlantılarıyla kıyaslayabilmesi için 'https://www.' ekleyerek formatlıyoruz
        # (Lexical feature çıkarımında iki sınıfın da benzer yapıda görünmesi önemlidir)
        clean_df['URL'] = 'https://www.' + clean_df['URL']
        
        # Veri setini dengede tutmak için baştan istediğimiz kadarını alıyoruz (Örn: 50.000)
        clean_df = clean_df.head(sample_size)
        
        # Makine öğrenimi için 'Label' (Etiket) ekliyoruz. 
        # 0: Clean/Temiz standarttır.
        clean_df['Label'] = 0
        
        print(f"İşlem başarılı. Toplam {len(clean_df)} adet Clean URL elde edildi.\n")
        return clean_df
        
    except Exception as e:
        print(f"Clean URL verisi çekilirken hata oluştu: {e}")
        return None

# Fonksiyonu çalıştırıp 50.000 adet temiz URL çekiyoruz
# (Bu sayıyı PhishTank'ten elde ettiğin veri sayısına yakın tutmalısın)
clean_dataset = get_clean_urls(sample_size=50000)

if clean_dataset is not None:
    # Veri setini CSV olarak kaydediyoruz
    clean_dataset.to_csv("clean_urls.csv", index=False)
    print("Veriler 'clean_urls.csv' dosyasına kaydedildi.")
    
    print("\nClean Dataset Önizlemesi:")
    print(clean_dataset.head())