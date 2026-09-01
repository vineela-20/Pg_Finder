# 🏨 PG & Hotel Finder

A Streamlit-based web automation application that helps users find **PGs and hotels based on a PIN code**.

The application uses **Playwright to automate a web browser and search Google Maps** for accommodation listings around the requested PIN code. The extracted information is then processed and displayed through an interactive Streamlit interface.

---

## 🚀 Live Demo

> Add your Streamlit Cloud URL here after deployment.

🔗 **Live Demo:** `https://your-app-name.streamlit.app`

---

## 📌 Project Overview

Finding suitable PGs and hotels in a specific area can be time-consuming when searching manually.

This project automates part of that process:

```text
User enters PIN code
        ↓
Streamlit UI
        ↓
Python application
        ↓
Playwright browser automation
        ↓
Google Maps search
        ↓
Extract accommodation information
        ↓
Process results
        ↓
Display results in Streamlit
