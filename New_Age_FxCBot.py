#!/usr/bin/env python3
"""
daily_telegram_bot.py
Simple daily Telegram sender with user input and weekend delivery.
Requires: requests, schedule
"""

import requests, schedule, time, logging
import os
from datetime import datetime
from pathlib import Path
import time


# ------------- CONFIG -------------
TELEGRAM_BOT_TOKEN = "6767405300:AAEyckYT-5W5Z3iGwvvUNbWVnXpMeQWBtr4" # replace with your token
CHAT_ID   =  -"1001779062214"             # replace with your chat id (string or number)
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "08:00")                 # 24-hour HH:MM when message will be sent daily
MESSAGE_FILE = os.getenv("MESSAGE_FILE", "daily_message.txt")      # optional file. If exists, message is read from here
LOG_FILE = "bot.log"
SEND_ON_START = os.getenv("SEND_ON_START", "false").lower() == "true"



"""
if not BOT_TOKEN and not CHAT_ID:
    print("ERROR BOT_TOKEN and CHAT_ID musbe set as environment variable.")
    exit(1)
"""
# ----------------------------------

# Setup logging
logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

def prompt_for_message():
    """
    If MESSAGE_FILE exists, read message from it.
    Otherwise prompt the user to enter a message (multiline allowed).
    """
    p = Path(MESSAGE_FILE)
    if p.exists():
        msg = p.read_text(encoding='utf-8').strip()
        logging.info("Loaded message from %s", MESSAGE_FILE)
        return msg
    """
    else:
        print("Enter your daily message. Finish with an empty line (press Enter twice):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        msg = "\n".join(lines).strip()
        if not msg:
            print("No message entered. Exiting.")
            logging.error("No message entered by user.")
            exit(1)
        # optionally save message for reuse
        save = input("Save message to daily_message.txt for reuse? (y/n): ").strip().lower()
        if save == "y":
            p.write_text(msg, encoding='utf-8')
            logging.info("Saved message to %s", MESSAGE_FILE)
        return msg
    """

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": str(chat_id),
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, data=payload, timeout=15)
        if r.status_code == 200:
            logging.info("Message sent successfully.")
            return True
        else:
            logging.error("Failed to send message. Status %s, Response: %s", r.status_code, r.text)
            return False
    except Exception as e:
        logging.exception("Exception sending message: %s", e)
        return False

def job():
    global daily_message
    today = datetime.now().strftime("%A")  # e.g. "Saturday"
    message_to_send = daily_message

    # Optional: weekend special message
    if today in ["Saturday"]:
        message_to_send = f"🌞 Happy Weekend - ( {today} )!\n\n"
    if today in ["Sunday"]:
        message_to_send = f"🌞 Hey traders, Happy {today}!\n\nWelcome to a new week"
    logging.info(f"Sending scheduled message for {today}")
    sent = send_telegram_message(BOT_TOKEN, CHAT_ID, message_to_send)
    if sent:
        print(f"[{datetime.now()}] {today} message sent.")
    else:
        print(f"[{datetime.now()}] Failed to send {today} message.  See {LOG_FILE} for details.")


"""
if __name__ == "__main__":
    logging.info("Bot starting.")
    if "YOUR_TELEGRAM_BOT_TOKEN" in BOT_TOKEN or "YOUR_CHAT_ID" in CHAT_ID:
        print("Please update BOT_TOKEN and CHAT_ID in the script before running.")
        logging.error("BOT_TOKEN/CHAT_ID not configured.")
        exit(1)
"""

    daily_message = prompt_for_message()

    # Schedule job every day at SCHEDULE_TIME (including weekends)
    # Schedule job for weekdays (Mon–Fri)
    schedule.every().monday.at(SCHEDULE_TIME).do(job)
    schedule.every().tuesday.at(SCHEDULE_TIME).do(job)
    schedule.every().wednesday.at(SCHEDULE_TIME).do(job)
    schedule.every().thursday.at(SCHEDULE_TIME).do(job)
    schedule.every().friday.at(SCHEDULE_TIME).do(job)

    # Schedule weekend messages (Sat–Sun)
    schedule.every().saturday.at(SCHEDULE_TIME).do(job)
    schedule.every().sunday.at(SCHEDULE_TIME).do(job)


    print(f"Bot scheduled: will send daily (Mon-Fri) at {SCHEDULE_TIME}. Logs: {LOG_FILE}")
    logging.info("Scheduled daily job at %s", SCHEDULE_TIME)

    # Initial immediate send option
if SEND_ON_START:
    print("SEND_ON_START=true → sending immediate message...")
    job()

    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("Bot stopped by user.")
        logging.info("Bot stopped by user.")

while True:
    schedule.run_pending()
    time.sleep(30)





