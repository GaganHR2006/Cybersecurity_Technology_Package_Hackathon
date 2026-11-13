# AcmeCorp Company Portal — Vercel Deployment

This directory contains the production-ready static deployment of the **AcmeCorp Company Website & Employee Portal**, designed to demonstrate real-time cyber attacks and detection with **CyberWatch Intelligence Platform**.

## 🌐 Included Pages

- **`index.html`** (`/`): The public AcmeCorp Corporate Landing Page (solutions, products, revenue stats, navigation).
- **`login.html`** (`/login`): The Employee Single Sign-On Portal. Features live client-side credential testing, error banners, attempt tracking, and a **"⚡ Simulate Brute-Force Attack Live"** button.
- **`dashboard.html`** (`/dashboard`): The confidential Employee Portal Dashboard (sensitive HR employee salary table, corporate financial transactions ledger, and active compromise alert banner).
- **`monitor.html`** (`/monitor`): Real-time Attack Telemetry Feed showing live authentication events, failed attempt volume, attacker IP risk meters, and MITRE ATT&CK indicators.

---

## 🚀 How to Deploy to Vercel

### Option 1: Via Vercel CLI (Fastest — 1 Minute)
Double-click `DEPLOY_TO_VERCEL.bat` in the project root, or run in PowerShell:
```powershell
cd c:\Users\gagan\Desktop\Cybersecurity_Technology_Package_Hackathon\vercel-site
npx --yes vercel
```
Follow the interactive prompts (press Enter to accept default project settings).  
To publish directly to production:
```powershell
npx --yes vercel --prod
```

### Option 2: Via GitHub on Vercel.com
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import repository: `GaganHR2006/Cybersecurity_Technology_Package_Hackathon`
3. In **Project Settings**:
   - Set **Root Directory** to `vercel-site`
4. Click **Deploy**!

---

## 🎯 How It Connects to CyberWatch

When someone visits the Vercel-deployed site and enters wrong passwords (or clicks the live attack button):
1. The browser records the authentication telemetry in `localStorage` and displays it in `monitor.html`.
2. It sends normalized alert payloads to the local CyberWatch backend at `http://localhost:8000/api/v1/alerts/ingest`.
3. The local CyberWatch SOC dashboard at `http://localhost:5173` picks up the alerts, correlates them, scores the risk, and surfaces response actions for the security analyst!
