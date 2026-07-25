# Zero-Day Phishing URL Detection Model & Hybrid WAF

This repository contains the complete source code, data processing pipeline, benchmark suite, and deployment interface for a Machine Learning & Heuristic Cybersecurity project developed as part of the **BIL 3112 Machine Learning** course at Dokuz Eylul University, Department of Computer Science.

---

## 📌 Project Overview

Traditional cybersecurity solutions (blacklists and signature-based systems) fail against newly created, zero-day phishing websites. The primary objective of this project is to build a real-time, proactive classifier capable of detecting zero-day phishing URLs in milliseconds without relying on external network queries (e.g., DNS resolution, WHOIS, SSL validation) or web page content downloading.

### Key Highlights

- **Zero External Dependencies:** Relies strictly on lightweight **lexical features** (structural properties) extracted from the URL string, preserving privacy and ensuring sub-millisecond inference.
- **Data Leakage Discovery & Mitigation:** Diagnosed and eliminated a critical flaw in lexical phishing research where models achieved artificial >99% F1-scores by exploiting dataset source asymmetry (learning "long URL = phishing"). Redesigned the feature space to achieve a realistic, production-ready **~90.3% F1-score**.
- **Hybrid WAF Architecture:** Augments pure Machine Learning probabilistic predictions with a 3-layer deterministic heuristic engine to cover edge cases (IP-based URLs, path-hidden keywords, trusted domains).
- **Champion Model Selection:** Benchmark of 10 Machine Learning algorithms identified **XGBoost** ($AUC = 0.9507$) as the optimal champion model based on accuracy, recall, and training speed ($0.40$ seconds).
- **Interactive Web Dashboard:** Deployed via a Streamlit-based web interface (**SOC Phishing Radar**).

---

## 📊 Dataset Preparation & Data Leakage Mitigation

### Dataset Composition

The master dataset contains **106,092 balanced records** aggregated from dynamic threat intelligence feeds:

- **Malicious (Phishing) URLs:** 56,091 verified active URLs collected from [PhishTank](https://www.phishtank.com/) (`Label = 1`).
- **Clean (Benign) URLs:** 50,001 domains sampled from the [Tranco Top 1M List](https://tranco-list.eu/) (`Label = 0`), normalized to `https://www.<domain>/` format.

> **Note:** Raw `.csv` files containing active phishing links are excluded from the repository per security best practices. Generate the dataset locally using scripts in `/src`.

### The Data Leakage Pitfall (Phase 1 vs. Phase 2)

- **Phase 1 (Data Leakage):** Including full URL features (`URL_Length`, `Path_Depth`, `Host_Length`) produced inflated F1-scores above **99%**. Feature importance analysis revealed that models made decisions almost entirely based on `URL_Length` (~27%) and `Host_Length` (~21%). Because PhishTank records contained full paths while Tranco records contained root domains, the models learned dataset source signatures rather than genuine phishing patterns.
- **Phase 2 (Bias Mitigation):** All full-URL length and path-dependent features were stripped. The feature space was constrained strictly to **9 domain-level lexical features**, dropping artificial metrics down to a realistic **90.3% F1-score** aligned with academic literature.

---

## 🛠️ Feature Engineering (Domain-Level Lexical Features)

The refined pipeline parses raw URLs into structural hostname components and extracts 9 lightweight numerical features.

### 1. Structural & Symbol Analysis

- `Domain_Length`: Character count of the domain (detects DGA generation).
- `Dot_Count`: Count of dot (`.`) characters in domain (indicates excessive subdomain concealment).
- `Hyphen_Count`: Count of hyphen (`-`) characters in domain (detects brand-spoofing).
- `Subdomain_Count`: Total number of subdomains.

### 2. Complexity & Character Metrics

- `Digit_to_Letter_Ratio`: Ratio of digits to letters (detects IP usage or evasion patterns).
- `Shannon_Entropy`: Mathematical measurement of randomness ($H(s) = -\sum p(x)\log_2 p(x)$) to detect Domain Generation Algorithms (DGA).

### 3. Deterministic & Security Indicators

- `Is_Trusted_TLD`: Binary flag set to `1` for institutional TLDs (`.edu`, `.gov`, `.mil`, `.edu.tr`, `.gov.tr`, etc.).
- `Is_IP_Address`: Binary flag set to `1` if hostname is a direct IPv4 address.
- `Has_Non_Standard_Port`: Binary flag set to `1` if URL uses non-standard ports (other than 80/443).

---

## 🧠 Model Training & Performance Benchmarks

Ten supervised machine learning algorithms were trained and evaluated on an 80/20 stratified split ($N = 106,092$).

| Rank | Algorithm | Accuracy | Precision | Recall | F1-Score | Training Time (s) |
|:---:|---|:---:|:---:|:---:|:---:|:---:|
| 1 | **LightGBM** | 0.9010 | 0.9383 | 0.8700 | **0.9028** | 2.22s |
| 2 | **XGBoost** 🏆 | 0.9006 | 0.9364 | 0.8711 | **0.9026** | **0.40s** |
| 3 | **Random Forest** | 0.8993 | 0.9308 | 0.8747 | 0.9018 | 2.77s |
| 4 | **Decision Tree** | 0.8980 | 0.9313 | 0.8713 | 0.9003 | 0.07s |
| 5 | **KNN** | 0.8966 | 0.9246 | 0.8758 | 0.8996 | 2.11s |
| 6 | **Gradient Boosting** | 0.8934 | 0.9366 | 0.8565 | 0.8947 | 2.95s |
| 7 | **MLP (Neural Network)** | 0.8923 | 0.9369 | 0.8537 | 0.8934 | 24.79s |
| 8 | **Linear SVC** | 0.8185 | 0.8908 | 0.7485 | 0.8135 | 0.10s |
| 9 | **Logistic Regression** | 0.8131 | 0.8780 | 0.7508 | 0.8094 | 0.20s |
| 10 | **Naive Bayes** | 0.7872 | 0.8949 | 0.6770 | 0.7708 | 0.02s |

### Why XGBoost Was Selected as Champion

Although LightGBM achieved a marginally higher F1-score (+0.0002), **XGBoost** was chosen as the champion model because:

- **Speed:** 5.5× faster training ($0.40$s vs. $2.22$s) and sub-millisecond inference time.
- **Discriminative Power:** Highest ROC-AUC score ($AUC = 0.9507$) and Average Precision ($AP = 0.9641$).
- **Deployment Ease:** Compact model serialization (`xgboost_waf_model.pkl`) for real-time WAF integration.

---

## 🛡️ Hybrid Heuristic WAF Engine

To compensate for edge cases where domain-only ML models might miss malicious intent (e.g., path-based keyword injection or direct IP access), a **3-Layer Deterministic Rule Engine** was built over the XGBoost probabilistic model.

1. **Rule 1: Absolute Threat Filter**
   - If `Is_IP_Address == 1` or `Has_Non_Standard_Port == 1` → Overrides prediction to **100% Phishing Risk**.

2. **Rule 2: Suspicious Keyword Scanner**
   - Scans full URL for phishing keywords (`secure`, `login`, `update`, `verify`, `account`, `auth`, `free`) outside trusted TLDs/brands → Forces **95% Phishing Risk** (restores path sensitivity deterministically).

3. **Rule 3: Institutional Whitelist**
   - If TLD is institutional (`.edu`, `.gov`, `.mil`, `.edu.tr`, etc.) or domain exists in `whitelist.txt` → Forces **0% Risk (CLEAN)** to eliminate False Positives on trusted infrastructure.

> **Security Threshold:** The decision threshold is lowered from `0.50` to **`0.30`** to prioritize **Recall** (reducing dangerous False Negatives in SOC monitoring).

---

## 🚀 Getting Started

### 1. Data Preprocessing

To clean raw dynamic threat feeds (PhishTank & Tranco) and produce the shuffled master dataset:

```bash
python src/data_preprocessing.py
# Outputs: data/master_dataset.csv
```

### 2. Feature Extraction

To extract domain-level lexical features into a Machine Learning-ready dataset:

```bash
python src/feature_extraction.py
# Outputs: data/ml_ready_dataset_v4.csv
```

### 3. Model Training & Export

To train all 10 algorithms, evaluate metrics, and export the serialized champion model:

```bash
python src/train.py
# Outputs: xgboost_waf_model.pkl, model_columns.pkl
```

### 4. Run Interactive Web Interface (SOC Radar)

To launch the Streamlit WAF dashboard:

```bash
streamlit run app.py
```

---

## 💻 Web Interface (SOC Phishing Radar)

The repository includes a Streamlit Web Dashboard (`app.py`) allowing SOC analysts to input suspicious URLs and view:

- **System Decision:** Real-time binary classification (**PHISHING** vs **CLEAN**).
- **Threat Score:** Risk score percentage derived from calibrated probabilities.
- **WAF Rule Triggers:** Instant feedback on triggered heuristic rules.
- **Lexical Feature Inspection:** Detailed JSON breakdown of extracted domain properties.
