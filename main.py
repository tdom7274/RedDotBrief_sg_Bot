import logging
import os

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException


# ============================================
# SETTINGS
# ============================================
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")

# Source credited under "further reading".
FURTHER_READING_URL = "https://herethereandgone.com/maximising-your-time-singapore/"
FURTHER_READING_NAME = "Here, There & Gone"

# Optional: your own site / socials (empty = hidden).
SITE_URL = ""
INSTAGRAM_URL = ""

BRAND = "Singapore Guide"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


# ============================================
# PLACES  (original descriptions — not copied from any article)
# key -> (title, area, desc, [tips])
# ============================================
PLACES = {
    "gardens": (
        "🌳 Gardens by the Bay",
        "Marina Bay",
        "Futuristic gardens with the towering Supertrees and two cooled conservatories, "
        "the Flower Dome and Cloud Forest. The evening light show is free.",
        ["Go at dusk for the Garden Rhapsody show", "Book conservatories ahead"],
    ),
    "mbs": (
        "🏙 Marina Bay Sands SkyPark",
        "Marina Bay",
        "The city's most famous skyline view, from the observation deck atop the three "
        "hotel towers. Sweeping views over the bay and downtown.",
        ["Sunset slots are busiest", "Great with the light show below"],
    ),
    "hawker": (
        "🍜 Hawker centres",
        "Citywide",
        "Singapore's beating culinary heart — open-air food courts with cheap, brilliant "
        "local dishes. Try Hainanese chicken rice, laksa, char kway teow and satay.",
        ["Maxwell & Lau Pa Sat are classics", "Cash still handy at some stalls"],
    ),
    "botanic": (
        "🌺 Singapore Botanic Gardens",
        "Tanglin",
        "A UNESCO World Heritage site and a green oasis, with the free National Orchid "
        "Garden at its centre. Perfect for a slow morning.",
        ["Go early to beat the heat", "Orchid Garden has a small fee"],
    ),
    "sentosa": (
        "🏖 Sentosa Island",
        "Sentosa",
        "A resort island of beaches, Universal Studios, cable cars and boardwalks. A full "
        "day of family-friendly fun just off the south coast.",
        ["Arrive by cable car for the views", "Book big attractions online"],
    ),
    "chinatown": (
        "🏮 Chinatown",
        "Outram",
        "Temples, heritage shophouses and street food side by side. Visit the Buddha Tooth "
        "Relic Temple and browse the markets.",
        ["Evenings are lively", "Great for souvenirs"],
    ),
    "kampongglam": (
        "🕌 Kampong Glam & Haji Lane",
        "Rochor",
        "The Sultan Mosque, Malay heritage and Haji Lane's narrow run of indie boutiques, "
        "murals and cafés.",
        ["Best for photos and coffee", "Dress modestly near the mosque"],
    ),
    "jewel": (
        "💧 Jewel Changi Airport",
        "Changi",
        "Even if you're not flying: the world's tallest indoor waterfall inside a lush "
        "glass dome, with gardens, shops and food.",
        ["The Rain Vortex light show runs nightly", "Easy MRT access"],
    ),
}

PLACE_ORDER = ["gardens", "mbs", "hawker", "botanic", "sentosa", "chinatown", "kampongglam", "jewel"]


# ============================================
# TEXTS
# ============================================
DIV = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈"

TEXT_START = (
    "🇸🇬  <b>SINGAPORE</b>\n"
    "<i>Best things to do — right here in the chat</i>\n"
    f"{DIV}\n"
    "A quick, hand-picked guide to the city's icons, its food and its "
    "neighbourhoods.\n\n"
    "▸ Tap <b>Top things to do</b> to begin."
)

TEXT_LIST = (
    "🧭  <b>Top things to do</b>\n"
    f"{DIV}\n"
    "Eight highlights, each with a couple of quick tips.\n"
    "Pick one to read it in full."
)

TEXT_MENU = (
    "🗂  <b>Menu</b>\n"
    f"{DIV}\n"
    "🧭  <b>Top things to do</b> — the highlights\n"
    "💡  <b>Tips</b> — getting around, weather, food\n"
    "📰  <b>Further reading</b> — go deeper\n"
    "ℹ️  <b>About</b> — this guide"
)

TEXT_TIPS = (
    "💡  <b>Practical tips</b>\n"
    f"{DIV}\n"
    "🚇  <b>Getting around</b>\n"
    "The MRT is fast, cheap and easy — a contactless card taps you through.\n\n"
    "🌡️  <b>Weather</b>\n"
    "Hot and humid year-round; carry water and plan midday breaks in the a/c.\n\n"
    "🍜  <b>Food</b>\n"
    "Hawker centres are the best value — follow the queues.\n\n"
    "🚯  <b>Etiquette</b>\n"
    "No eating or drinking on the MRT; keep public spaces tidy.\n\n"
    "💳  <b>Money</b>\n"
    "Cards work almost everywhere; keep small cash for hawker stalls."
)

TEXT_ABOUT = (
    f"ℹ️  <b>About {BRAND}</b>\n"
    f"{DIV}\n"
    "A quick mini-guide to Singapore — short write-ups of well-known sights, "
    "made for easy reading right here in Telegram.\n\n"
    f"📰  For a deeper dive, tap <b>Further reading</b> to visit {FURTHER_READING_NAME}."
)

HIGHLIGHTS = "✦ Good to know"


# ============================================
# HELPERS
# ============================================
def btn(text, data):
    return types.InlineKeyboardButton(text=text, callback_data=data)


def url_btn(text, url):
    return types.InlineKeyboardButton(text=text, url=url)


def read_btn():
    return url_btn(f"📰 Further reading — {FURTHER_READING_NAME}", FURTHER_READING_URL)


def site_btn():
    return url_btn("🌐 Website", SITE_URL) if SITE_URL else None


def ig_btn():
    return url_btn("📸 Instagram", INSTAGRAM_URL) if INSTAGRAM_URL else None


def make_markup(rows):
    markup = types.InlineKeyboardMarkup()
    for row in rows:
        row = [b for b in row if b is not None]
        if row:
            markup.row(*row)
    return markup


BTN_LIST = ("🧭 Top things to do", "list")
BTN_MENU = ("🗂 Menu", "menu")


# ============================================
# SCREEN / CARD BUILDERS
# ============================================
def place_text(key):
    title, area, desc, tips = PLACES[key]
    lines = "\n".join(f"▸ {t}" for t in tips)
    return (
        f"<b>{title}</b>\n"
        f"<i>📍 {area}</i>\n"
        f"{DIV}\n"
        f"{desc}\n\n"
        f"<b>{HIGHLIGHTS}</b>\n{lines}"
    )


def place_rows(key):
    return [
        [read_btn()],
        [btn("‹ Back to list", "list"), btn(*BTN_MENU)],
    ]


def screen(action):
    if action in ("home", "start"):
        return TEXT_START, [
            [btn(*BTN_LIST)],
            [btn("💡 Tips", "tips"), btn("ℹ️ About", "about")],
            [read_btn()],
            [site_btn(), ig_btn()],
        ]
    if action == "list":
        rows = [[btn(PLACES[k][0], f"place:{k}")] for k in PLACE_ORDER]
        rows.append([btn(*BTN_MENU)])
        return TEXT_LIST, rows
    if action == "menu":
        return TEXT_MENU, [
            [btn(*BTN_LIST)],
            [btn("💡 Tips", "tips"), btn("ℹ️ About", "about")],
            [read_btn()],
            [site_btn(), ig_btn()],
        ]
    if action == "tips":
        return TEXT_TIPS, [[btn(*BTN_LIST)], [btn(*BTN_MENU)]]
    if action == "about":
        return TEXT_ABOUT, [[read_btn()], [btn(*BTN_LIST), btn(*BTN_MENU)]]
    return None


# ============================================
# HANDLERS
# ============================================
@bot.message_handler(commands=["start"])
def start(message):
    text, rows = screen("home")
    bot.send_message(message.chat.id, text, reply_markup=make_markup(rows))


def render(call, text, rows):
    markup = make_markup(rows)
    try:
        bot.edit_message_text(
            text, chat_id=call.message.chat.id,
            message_id=call.message.message_id, reply_markup=markup,
        )
    except ApiTelegramException:
        bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("place:"))
def show_place(call):
    bot.answer_callback_query(call.id)
    key = call.data.split(":", 1)[1]
    if key in PLACES:
        render(call, place_text(key), place_rows(key))


@bot.callback_query_handler(func=lambda call: True)
def show_screen(call):
    bot.answer_callback_query(call.id)
    result = screen(call.data)
    if result:
        render(call, result[0], result[1])


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.info("%s bot is starting", BRAND)
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    main()
