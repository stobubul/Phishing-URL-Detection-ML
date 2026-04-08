# Zero-Day Phishing URL Detection Model

This repository contains the source code and data pipeline for a Machine Learning project developed as part of the **BIL 3112 Machine Learning** course at Dokuz Eylul University, Department of Computer Science.

## 📌 Project Overview
Traditional cybersecurity measures generally block only known threats, leaving users vulnerable to newly created, zero-day phishing websites. The primary objective of this project is to build a proactive machine learning classifier capable of detecting zero-day phishing URLs. 

To minimize operational costs, API rate limits, and network latency associated with network-based metrics (e.g., Domain Age, SSL certificates, DNS resolution), this model strictly relies on extracting and analyzing the **lexical features** (structural properties) of the URLs.

## 📊 Dataset Preparation
Instead of using static, outdated datasets, we built a custom data pipeline aggregating dynamic threat intelligence feeds to ensure the model learns from current attack vectors.

* **Malicious (Phishing) URLs:** Data gathered from [PhishTank](https://www.phishtank.com/) and [OpenPhish](https://openphish.com/). Label = `1`
* **Clean (Benign) URLs:** Data sampled from the [Tranco Top 1M List](https://tranco-list.eu/), the academic standard for domain rankings. Label = `0`

> **Note:** Due to GitHub's file size limits and security best practices, the raw `.csv` dataset files (containing live phishing links) are not included in this repository. You can generate the dataset by running the data gathering scripts located in the `/src` directory.

## 🛠️ Features (Lexical Analysis)
The feature extraction script parses the URLs and creates a numerical dataset based on properties such as:
* URL Length
* Count of special characters (`@`, `-`, `.`, etc.)
* Hostname characteristics
* Parameter counts

## 🚀 Getting Started
*(Instructions for running the data gathering and feature extraction scripts will be added here as the project progresses.)*