import sys
sys.stdout.reconfigure(encoding='utf-8')
from config import FRESHMINDS_WEB_URL
from handlers import after_result_keyboard

kb = after_result_keyboard("https://t.me/test", "00629726", "Aschalew")
print("Generated Button URL:")
for row in kb.inline_keyboard:
    for btn in row:
        print(f"  {btn.text} -> {btn.url}")
