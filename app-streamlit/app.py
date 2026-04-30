import streamlit as st
import pandas as pd
import urllib.parse as parse
import math
import re
import joblib

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="SOC Phishing Radar", page_icon="🛡️", layout="centered")

# --- MODEL VE VERİ YÜKLEME ---
@st.cache_resource
def load_system():
    try:
        model = joblib.load('xgboost_waf_model.pkl')
        cols = joblib.load('model_columns.pkl')
        
        # Dinamik Whitelist Yükleme
        try:
            with open("whitelist.txt", "r", encoding="utf-8") as f:
                whitelist = [line.strip().lower() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            whitelist = ['google.com', 'github.com', 'microsoft.com']
            
        return model, cols, whitelist
    except Exception as e:
        st.error(f"Sistem yüklenirken hata oluştu: {e}")
        return None, None, []

xgb_model, model_columns, trusted_brands = load_system()

# --- ARAYÜZ TASARIMI ---
st.title("🛡️ SOC Phishing Radar - Hibrit WAF")
st.markdown("XGBoost ve Heuristic Kurallar (0-Day Tehdit Analiz Motoru)")
st.divider()

test_url = st.text_input("🔍 Analiz edilecek URL'yi girin:", placeholder="https://ornek-site.com/login")

if st.button("🚀 Canlı Analizi Başlat", type="primary"):
    if not test_url:
        st.warning("Lütfen bir URL girin!")
    else:
        with st.spinner('Bağlantı Lexical ve Heuristic motorlarda taranıyor...'):
            
            # 1. PARÇALAMA VE ÖZELLİK ÇIKARIMI (Feature Extraction)
            try:
                parsed = parse.urlparse(test_url)
                domain = str(parsed.hostname) if parsed.hostname else test_url
                port = parsed.port
                if domain.startswith('www.'): domain = domain[4:]
            except Exception:
                domain = test_url
                port = None

            def calculate_entropy(text):
                if not text: return 0
                entropy = 0
                for x in set(text):
                    p_x = float(text.count(x)) / len(text)
                    entropy += - p_x * math.log(p_x, 2)
                return entropy

            features = {}
            features['Domain_Length'] = len(domain)
            features['Dot_Count'] = domain.count('.')
            features['Hyphen_Count'] = domain.count('-')
            digits = sum(c.isdigit() for c in domain)
            features['Digit_to_Letter_Ratio'] = (digits / (len(domain) - digits)) if (len(domain) - digits) > 0 else 0
            features['Shannon_Entropy'] = calculate_entropy(domain)
            features['Subdomain_Count'] = domain.count('.') 
            trusted_tlds = ['.edu', '.edu.tr', '.gov', '.gov.tr', '.mil', '.bel.tr', '.k12.tr']
            features['Is_Trusted_TLD'] = 1 if any(domain.endswith(tld) for tld in trusted_tlds) else 0
            features['Is_IP_Address'] = 1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain) else 0
            features['Has_Non_Standard_Port'] = 1 if port is not None and port not in [80, 443] else 0
            
            df_features = pd.DataFrame([features])
            for col in model_columns:
                if col not in df_features.columns: df_features[col] = 0
            df_features = df_features[model_columns] 
            
            # 2. XGBOOST TAHMİNİ
            probabilities = xgb_model.predict_proba(df_features)[0]
            threat_score = probabilities[1]
            
            # 3. HEURISTIC (WAF) MÜDAHALE KATMANI
            SECURITY_THRESHOLD = 0.30 
            prediction = 1 if threat_score >= SECURITY_THRESHOLD else 0
            
            suspicious_words = ['secure', 'login', 'update', 'verify', 'account', 'auth', 'free']
            is_trusted_brand = any(domain == brand or domain.endswith('.' + brand) for brand in trusted_brands)
            
            rule_triggered = None
            
            if features['Is_IP_Address'] == 1 or features['Has_Non_Standard_Port'] == 1:
                prediction = 1; threat_score = 1.0 
                rule_triggered = "🚨 Kesin Tehdit (IP veya Standart Dışı Port Saptandı)"
                
            elif any(word in test_url.lower() for word in suspicious_words) and features['Is_Trusted_TLD'] == 0 and not is_trusted_brand:
                prediction = 1; threat_score = 0.95 
                rule_triggered = "⚠️ Şüpheli Kelime Avcısı (Oltalama Anahtar Kelimesi Saptandı)"
                
            elif (features['Is_Trusted_TLD'] == 1 or is_trusted_brand):
                prediction = 0; threat_score = 0.0 
                rule_triggered = "✅ Kurumsal Beyaz Liste (Marka/Kurum Toleransı Uygulandı)"

            # --- SONUÇLARI EKRANA YAZDIRMA ---
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sistem Kararı")
                if prediction == 1:
                    st.error("PHISHING (ZARARLI BAĞLANTI) 🚫")
                else:
                    st.success("CLEAN (GÜVENLİ BAĞLANTI) ✅")
                    
            with col2:
                st.subheader("Tehdit Skoru")
                if prediction == 1:
                    st.metric(label="Risk", value=f"% {threat_score*100:.1f}")
                else:
                    st.metric(label="Risk", value=f"% {threat_score*100:.1f}", delta="- Güvenli")

            if rule_triggered:
                st.info(f"**WAF Kural Motoru Devrede:** {rule_triggered}")
            
            # İstatistiksel detayları bir "Açılır Kapanır" kutuya saklayalım
            with st.expander("🔍 Yapısal (Lexical) Analiz Detayları"):
                st.json(features)