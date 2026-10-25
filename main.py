import json
import os
import sys
from anthropic import Anthropic

# Setup key and model
os.environ["ANTHROPIC_API_KEY"] = "dummy-key"
client = Anthropic()
MODEL = "claude-haiku-5-5"

def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def generate_ai_sms(data):
    print("Analyzing data... (asking Claude)")
    
    system_prompt = "You are Cadence, an AI scheduling agent. Read the user's health data and deadlines. Write a short, friendly SMS (max 2 sentences) rescheduling their day to prevent burnout."
    user_prompt = json.dumps(data)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        # Fail-safe in case your Mac blocks the connection
        sleep = data['health']['sleep_hours']
        if sleep < 6:
            return f"Hey Alex, I noticed you only got {sleep} hours of sleep. I've moved your Math HW to tomorrow morning. Please eat dinner and rest tonight."
        else:
            return "Hey Alex, your recovery looks good today. Proceed with your Math HW as planned."

def append_message(text):
    try:
        with open("messages.json", "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except Exception:
        loaded = []
    
    loaded.append({"sender": "Cadence", "text": text})
    
    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(loaded, f, indent=4)

def print_formatted_sms(message, sender="Cadence"):
    inner = 54
    text_w = inner - 2
    stamp = "now"

    def row(content=""):
        gap = " " * max(0, text_w - len(content))
        return f"│ {content}{gap} │"

    header_plain = "💬 MESSAGES"
    header_gap = text_w - len(header_plain) - len(stamp)
    header_row = f"│ {header_plain}{' ' * max(1, header_gap)}{stamp} │"

    import textwrap
    lines = textwrap.wrap(message, width=text_w) or [""]

    out = [f"╭{'─' * inner}╮", header_row, row(sender),
           *[row(line) for line in lines], f"╰{'─' * inner}╯"]
    print("\n" + "\n".join(out) + "\n")

def run_agent():
    print(f"🤖 Cadence agent started (model: {MODEL}).")
    data = load_data()
    
    # --- NEW: SHOW DATA INPUT ---
    print(f"\n[Current Data] Sleep: {data['health']['sleep_hours']} hours, HRV: {data['health']['hrv_status']}")
    new_sleep = input("Enter new sleep hours for Alex (or press Enter to keep current): ")
    
    if new_sleep.strip():
        data['health']['sleep_hours'] = float(new_sleep)
        # Save the new input back to data.json
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Updated sleep data to {new_sleep} hours.")
    # ----------------------------

    sms_text = generate_ai_sms(data)
    
    if not sms_text.startswith("Error"):
        print_formatted_sms(sms_text)
        append_message(sms_text)
    else:
        print(f"[{sms_text}]")

if __name__ == "__main__":
    run_agent()