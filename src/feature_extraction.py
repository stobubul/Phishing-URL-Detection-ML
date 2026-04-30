import pandas as pd
import urllib.parse as parse
import math
import re

print("Faz 4: Saf Makine Öğrenimi (Pure ML) Özellik Çıkarımı Başlatılıyor...")

try:
    df = pd.read_csv('data/master_dataset.csv') # Eğer hata verirse '../data/master_dataset.csv' yap
except FileNotFoundError:
    print("Hata: master_dataset.csv bulunamadı.")
    exit()

def calculate_entropy(text):
    if not text: return 0
    entropy = 0
    for x in set(text):
        p_x = float(text.count(x)) / len(text)
        entropy += - p_x * math.log(p_x, 2)
    return entropy

def extract_pure_ml_features(url):
    url_str = str(url)
    features = {}
    
    try:
        parsed_url = parse.urlparse(url_str)
        domain = str(parsed_url.hostname) if parsed_url.hostname else url_str
        path = str(parsed_url.path)
        port = parsed_url.port
        if domain.startswith('www.'):
            domain = domain[4:]
    except Exception:
        domain = url_str
        path = ""
        port = None

    # --- 1. ALAN ADI (DOMAIN) ÖZELLİKLERİ ---
    features['Domain_Length'] = len(domain)
    features['Dot_Count'] = domain.count('.')
    features['Hyphen_Count'] = domain.count('-')
    # Underscore_Count ÇIKARILDI!
    
    digits = sum(c.isdigit() for c in domain)
    letters = sum(c.isalpha() for c in domain)
    features['Digit_to_Letter_Ratio'] = (digits / letters) if letters > 0 else 0
    
    features['Shannon_Entropy'] = calculate_entropy(domain)
    features['Subdomain_Count'] = domain.count('.') 
    
    # --- 2. YENİ: DİZİN (PATH) VE GÖRÜNÜRLÜK ÖZELLİKLERİ ---
    # Eğik çizgi (/) sayısını sayarak klasör derinliğini buluruz
    features['Path_Depth'] = path.count('/')
    
    # Şüpheli kelimeleri SADECE domainde değil, TÜM URL'de arıyoruz!
    suspicious_words = ['secure', 'login', 'update', 'verify', 'account', 'support', 'auth', 'webscr']
    features['Has_Suspicious_Word_In_URL'] = 1 if any(word in url_str.lower() for word in suspicious_words) else 0
    
    # --- 3. STANDART GÜVENLİK İNDİKATÖRLERİ ---
    trusted_tlds = ['.edu', '.edu.tr', '.gov', '.gov.tr', '.mil', '.bel.tr', '.k12.tr']
    features['Is_Trusted_TLD'] = 1 if any(domain.endswith(tld) for tld in trusted_tlds) else 0
    features['Is_IP_Address'] = 1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain) else 0
    features['Has_Non_Standard_Port'] = 1 if port is not None and port not in [80, 443] else 0
    
    return pd.Series(features)

print("Özellikler çıkarılıyor, lütfen bekleyin...")
extracted_features_df = df['URL'].apply(extract_pure_ml_features)
final_dataset = pd.concat([df, extracted_features_df], axis=1)

final_dataset = final_dataset.drop(columns=['URL'])

# YENİ V4 DOSYASI OLARAK KAYDEDİYORUZ
final_dataset.to_csv('data/ml_ready_dataset_v4.csv', index=False)
print("\nİşlem Başarılı! Saf ML veri seti 'ml_ready_dataset_v4.csv' olarak kaydedildi.")