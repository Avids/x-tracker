import os
import re
import asyncio
import random
from datetime import datetime, timezone, timedelta
from twikit import Client
import shared

async def main():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("Missing environment configurations.")
        return

    twitter_accounts = shared.load_accounts("accounts.txt")
    if not twitter_accounts: 
        print("No accounts found in accounts.txt")
        return
        
    state = shared.load_state()
    exclusions = shared.load_exclusions("exclusions.txt")
    ticker_pattern = re.compile(r"\$[A-Za-z]{1,5}\b")
    
    client = Client('en-US')
    client.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    if not os.path.exists(shared.COOKIES_FILE):
        print("Missing cookies.json configuration.")
        return
    shared.load_cookies_safely(client, shared.COOKIES_FILE)

    print(f"--- Starting x-tracker Execution Scan ---")
    now_utc = datetime.now(timezone.utc)

    for account_name in twitter_accounts:
        try:
            print(f"🔍 Processing Target: @{account_name}")
            user = await client.get_user_by_screen_name(account_name)
            last_seen_id = state.get(account_name, "0")
            
            tweets = await client.get_user_tweets(user.id, 'Tweets', count=7)
                
            clean_tweets = []
            for t in tweets:
                if hasattr(t, 'retweeted_status') and t.retweeted_status: continue
                if hasattr(t, 'reply_to') and t.reply_to: continue
                if last_seen_id != "0" and int(t.id) <= int(last_seen_id): continue
                clean_tweets.append(t)
            
            valid_time_tweets = []
            for t in clean_tweets:
                try:
                    if now_utc - datetime.strptime(t.created_at, "%a %b %d %H:%M:%S %z %Y") <= timedelta(hours=48):
                        valid_time_tweets.append(t)
                except: pass

            for tweet in sorted(valid_time_tweets[:7], key=lambda x: int(x.id)):
                text = tweet.text or ""
                if hasattr(tweet, 'quoted_status') and tweet.quoted_status:
                    quoted_text = tweet.quoted_status.get('text', '') if isinstance(tweet.quoted_status, dict) else getattr(tweet.quoted_status, 'text', '')
                    if quoted_text: text = f"{text}\n\n[Quoted]: {quoted_text}"

                image_url = None
                if tweet.media and len(tweet.media) > 0:
                    item = tweet.media[0]
                    image_url = item.get('media_url_https') or item.get('url') if isinstance(item, dict) else getattr(item, 'media_url_https', getattr(item, 'url', None))

                if bool(ticker_pattern.search(text)) and bool(image_url) and shared.is_valid_content(text, exclusions):
                    processed_text = shared.clean_tweet_text(text, ticker_pattern, account_name, tweet.id)
                    if shared.send_to_telegram(processed_text, image_url, account_name, tweet.created_at, bot_token, chat_id):
                        state[account_name] = tweet.id
                        shared.save_state(state)
                else:
                    state[account_name] = tweet.id
                    shared.save_state(state)
                        
            await asyncio.sleep(random.uniform(3.0, 6.0))
        except Exception as e: 
            print(f"Error handling target @{account_name}: {e}")

if __name__ == "__main__":
    asyncio.run(main())