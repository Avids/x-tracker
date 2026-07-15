import os
import json
import html
import re
import requests
from datetime import datetime as dt_datetime, timezone, timedelta
import datetime as dt

STATE_FILE = "last_seen.json"
COOKIES_FILE = "cookies.json"

def load_accounts(accounts_file="accounts.txt"):
    if not os.path.exists(accounts_file): return []
    with open(accounts_file, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {}
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def load_cookies_safely(client, file_path=COOKIES_FILE):
    with open(file_path, 'r') as f:
        raw_data = json.load(f)
    if isinstance(raw_data, list):
        clean_cookies = {}
        for cookie in raw_data:
            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                clean_cookies[cookie['name']] = cookie['value']
        client.set_cookies(clean_cookies)
    else:
        client.load_cookies(file_path)

def load_exclusions(exclusions_file="exclusions.txt"):
    if not os.path.exists(exclusions_file): return []
    with open(exclusions_file, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]

def is_valid_content(text, exclusions):
    text_lower = text.lower()
    for bad_word in exclusions:
        if bad_word in text_lower: return False
    return True

def clean_tweet_text(text, ticker_pattern, handle, tweet_id):
    clean_text = html.unescape(text)
    clean_text = re.compile(r'https?://\S+').sub('', clean_text)
    clean_text = re.compile(r'@\w+').sub('', clean_text)
    clean_text = ticker_pattern.sub(lambda m: m.group(0).replace('$', '#'), clean_text)
    clean_text = clean_text.replace("_", "\\_").replace("*", "\\*")
    
    tweet_url = f"https://x.com/{handle}/status/{tweet_id}"
    
    if len(clean_text) > 300:
        temp_text = clean_text[:290].strip()
        sentence_endings = [m.start() for m in re.finditer(r'[.!?]\s', temp_text)]
        if sentence_endings:
            split_index = sentence_endings[-1] + 1
            truncated = temp_text[:split_index].strip()
        else:
            truncated = re.sub(r'\s+\S+$', '', temp_text)
        clean_text = f"{truncated}... [continue...]({tweet_url})"
    else:
        clean_text = clean_text.strip()
        if "see more" in clean_text.lower():
            clean_text = re.compile(r'(?i)see more.*').sub(f"[See more on X]({tweet_url})", clean_text)
        else:
            clean_text = f"{clean_text}\n\n🔗 [View original post]({tweet_url})"
    return clean_text.strip()

def send_to_telegram(text, image_url, handle, created_at_str, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    try:
        utc_time = dt_datetime.strptime(created_at_str, "%a %b %d %H:%M:%S %z %Y")
        eastern_time = utc_time.astimezone(dt.timezone(dt.timedelta(hours=-4)))
        formatted_time = eastern_time.strftime("%I:%M %p | %b %d")
    except:
        formatted_time = ""
    time_badge = f" 🕒 _{formatted_time}_" if formatted_time else ""
    caption_text = f"👤 #{handle}{time_badge}\n\n{text}"
    payload = {"chat_id": chat_id, "photo": image_url, "caption": caption_text, "parse_mode": "Markdown"}
    try: return requests.post(url, json=payload, timeout=15).status_code == 200
    except: return False