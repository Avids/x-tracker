# x-tracker 🚀

A lightweight, serverless automation engine designed to track selected profiles on X (formerly Twitter), extract high-quality technical setups or analytical charts containing asset tickers, process text constraints cleanly, and broadcast them directly into a Telegram Channel or Group.

Powered entirely by **GitHub Actions** and **Python**, meaning it requires **zero active server costs or infrastructure upkeep**.

---

## ✨ Features
* **Serverless Scheduling:** Runs seamlessly on a automated cron schedule every 3 hours everyday.
* **Smarter Content Stripping:** Automatically strips external links, handle mentions, and raw symbols while transforming tickers into clean native identifiers (e.g., `$AAPL` into `#AAPL`).
* **Smart Truncation Boundaries:** Intelligently slices sentences up to 300 characters without truncating midway through words or half-finished clauses.
* **Custom Dynamic Filters:** Filters retweets, nested replies, or promotional updates instantly using an out-of-code tracking database (`exclusions.txt`).
* **High-Water Mark Tracking:** Automatically updates and commits state configurations to guarantee that duplicate posts never hit your feeds.

---

## 🛠️ Configuration & Deployment Setup

### 1. Prerequisites
Before deploying, make sure you have gathered the following parameters:
* A **Telegram Bot Token** (Acquired from [@BotFather](https://t.me/BotFather)).
* A **Telegram Chat ID** (Your target public channel handle like `@my_channel` or numeric private chat ID).
* Your authenticated **X Session Cookies** (Exported in JSON array format using standard browser storage inspection plugins like *EditThisCookie*).

---

### 2. Forking and Populating the Repository
1. **Fork or Create** a private or public repository on GitHub containing these tracking files.
2. Open **`accounts.txt`** and write the target handles you wish to track (one handle per line, without using the `@` prefix).
3. Open **`exclusions.txt`** and input any spam words or promotional text patterns (e.g., `discord`, `course`, `subscriber`) you wish to auto-discard.

---

### 3. Setting Up Repository Security Credentials
To keep your API credentials secure, inject them into your GitHub Environment variables:
1. Navigate to your repository's **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret** and inject:
   * `TELEGRAM_BOT_TOKEN` : *Your Telegram Bot API Token.*
   * `TELEGRAM_CHAT_ID` : *Your destination Telegram Group/Channel tracking ID.*

---

### 4. Setting Up Authentication Cookies
To allow the headless browser scraping module to execute requests cleanly without getting blocked by login screens:
1. Save your exported JSON cookie payload array into a file named **`cookies.json`** in your repository's root folder.
2. Commit and push the file up to your repository branch.

---

### 5. Granting Automation Script Write Permissions
To enable the script to remember which posts it has already scanned and update its state file:
1. Navigate to **Settings** -> **Actions** -> **General**.
2. Scroll to **Workflow permissions**.
3. Toggle the selection to **Read and write permissions**, then click **Save**.

---

## 🚀 Usage & Manual Overrides
Once configured, the workflow handles everything on its own. To run an immediate diagnostic scan outside of the normal 3-hour window:
1. Head over to the **Actions** tab inside your repository dashboard.
2. Select **x-tracker Automation Engine** from the sidebar.
3. Click the **Run workflow** dropdown button to trigger a manual scan.

## ⚖️ Disclaimer
This automation tool is built strictly for personal research and data organization utility setups. Use responsibly according to the usage policies of target platforms.