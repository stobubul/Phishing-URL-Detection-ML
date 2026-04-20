import pandas as pd
import urllib.parse as parse
import math
import re

print("Feature Extraction işlemi başlatılıyor...")

# Master dataseti yüklüyoruz
try:
    df = pd.read_csv('../data/master_dataset.csv')
    print(f"Dataset yüklendi: {len(df)} satır işlenecek.")
except FileNotFoundError:
    print("Hata: master_dataset.csv bulunamadı.")
    exit()

# Shannon Entropy Hesaplama Fonksiyonu
def calculate_entropy(text):
    if not text:
        return 0
    entropy = 0
    for x in set(text):
        p_x = float(text.count(x)) / len(text)
        entropy += - p_x * math.log(p_x, 2)
    return entropy

# Temel Özellik Çıkarım Fonksiyonu
def extract_lexical_features(url):
    if not isinstance(url, str):
        url = str(url)
        
    features = {}
    
    # 1. Temel Lexical Özellikler (Sembol ve Uzunluk)
    features['URL_Length'] = len(url)
    features['At_Symbol_Count'] = url.count('@')
    features['Dot_Count'] = url.count('.')
    features['Hyphen_Count'] = url.count('-')
    features['Underscore_Count'] = url.count('_')
    
    # 2. İleri Düzey Karakter Özellikleri (Rakam/Harf Oranı)
    digits = sum(c.isdigit() for c in url)
    letters = sum(c.isalpha() for c in url)
    # Sıfıra bölünme hatasını engellemek için letters 0 ise oranı 0 kabul ediyoruz
    features['Digit_to_Letter_Ratio'] = (digits / letters) if letters > 0 else 0
    
    # 3. Karmaşıklık Analizi (Shannon Entropy)
    features['Shannon_Entropy'] = calculate_entropy(url)
    
    # 4. Ağ ve Yapısal Bileşenler
    try:
        parsed_url = parse.urlparse(url)
        hostname = str(parsed_url.hostname) if parsed_url.hostname else ""
        
        features['Host_Length'] = len(hostname)
        
        # Parametre Sayısı
        query_params = parse.parse_qs(parsed_url.query)
        features['Parameter_Count'] = len(query_params)
        
        # Subdomain Count (Root domain'i ayırmak karmaşık olabildiği için en pratik yol nokta saymaktır)
        # Genellikle "www.google.com" 2 nokta içerir (1 Subdomain). Nokta sayısı ne kadar çoksa subdomain o kadar fazladır.
        features['Subdomain_Count'] = hostname.count('.') 
        
        # Is_Shortened (Popüler kısaltma servisleri kontrolü)
        shorteners = ['bit.ly', 't.co', 'tinyurl.com', 'goo.gl', 'is.gd', 'cli.gs', 'tr.im', 'ow.ly', 'x.co']
        features['Is_Shortened'] = 1 if any(short in hostname for short in shorteners) else 0
        
    except Exception:
        # Parse hatalarında default değerler
        features['Host_Length'] = 0
        features['Parameter_Count'] = 0
        features['Subdomain_Count'] = 0
        features['Is_Shortened'] = 0
        
    return pd.Series(features)

# Fonksiyonu DataFrame'e uyguluyoruz
extracted_features_df = df['URL'].apply(extract_lexical_features)
final_dataset = pd.concat([df, extracted_features_df], axis=1)

# Eğitim verisinden string URL sütununu siliyoruz
final_dataset = final_dataset.drop(columns=['URL'])

# Dosyayı kaydediyoruz
final_dataset.to_csv('../data/ml_ready_dataset.csv', index=False)

print("\nİşlem Başarılı! Tüm lexical featurelar (temel ve ileri düzey) çıkarıldı.")
print(final_dataset.head())