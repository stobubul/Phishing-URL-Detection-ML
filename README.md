# Zero-Day Phishing URL Detection Model

This repository contains the source code and data pipeline for a Machine Learning project developed as part of the **BIL 3112 Machine Learning** course at Dokuz Eylul University, Department of Computer Science.

## 📌 Project Overview
Traditional cybersecurity measures generally block only known threats, leaving users vulnerable to newly created, zero-day phishing websites. The primary objective of this project is to build a proactive machine learning classifier capable of detecting zero-day phishing URLs. 

To minimize operational costs, API rate limits, and network latency associated with network-based metrics (e.g., Domain Age, SSL certificates, DNS resolution), this model strictly relies on extracting and analyzing the **lexical features** (structural properties) of the URLs.

## 📊 Dataset Preparation
Instead of using static, outdated datasets, we built a custom data pipeline aggregating dynamic threat intelligence feeds to ensure the model learns from current attack vectors. The final master dataset contains **106,092 balanced records**.

* **Malicious (Phishing) URLs:** Data gathered from [PhishTank](https://www.phishtank.com/) and [OpenPhish](https://openphish.com/). Total: 56,092 URLs. Label = `1`
* **Clean (Benign) URLs:** Data sampled from the [Tranco Top 1M List](https://tranco-list.eu/), the academic standard for domain rankings. Total: 50,000 URLs. Label = `0`

> **Note:** Due to GitHub's file size limits and security best practices, the raw `.csv` dataset files (containing live phishing links) are not included in this repository. You can generate the dataset by running the data gathering scripts located in the `/src` directory.

## 🛠️ Feature Engineering (Lexical Analysis)
The feature extraction pipeline parses the raw string URLs and creates a numerical feature matrix. To detect the structural tricks used by phishing campaigns, 10 specific features are extracted across three categories:

**1. Basic Character & Symbol Analysis:**
* `URL_Length`
* Special character counts: `@`, `-`, `_`, `.`

**2. Structural Network Components:**
* `Subdomain_Count`
* `Is_Shortened` (Checks for bit.ly, tinyurl, etc.)
* `Host_Length`
* `Parameter_Count`

**3. Advanced Complexity Analysis:**
* `Digit_to_Letter_Ratio` (High ratio often indicates IP usage or evasion)
* `Shannon_Entropy` (Mathematical measurement of randomness to detect Domain Generation Algorithms - DGA)

## 🚀 Getting Started

### 1. Data Preprocessing
To clean the raw threat intelligence feeds and merge them into a single, balanced, and shuffled dataset:
```bash
python src/data_preprocessing.py
(Outputs: data/master_dataset.csv)

2. Feature Extraction
To convert the string URLs into a numerical feature matrix ready for Machine Learning algorithms:

python src/feature_extraction.py
(Outputs: data/ml_ready_dataset.csv)

```
## 🧠 Model Training (In Progress)
(Documentation regarding Train/Test splits, algorithm selection (e.g., Random Forest), and evaluation metrics will be added in the next phase.)


Bu güncellemeyi de GitHub'a yolladıktan sonra (commit mesajı olarak `docs: update README with final dataset metrics and advanced features` kullanabilirsin), artık makine öğrenimi modellerimizi eğiteceğimiz o kritik Python koduna geçebiliriz!
