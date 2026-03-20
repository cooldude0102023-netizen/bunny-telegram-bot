import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
SITE = "https://notesgallery.com"

TRIGGER_KEYWORDS = [
    "notes", "note", "pyq", "pyqs", "previous year question", "previous year questions",
    "syllabus", "quantum", "pdf", "study material",
    "important question", "important questions", "imp question", "imp questions"
]

user_last_message = {}

COURSES = {
    "btech": {
        "label": "B.Tech",
        "icon": "🎓",
        "years": ["1st Year", "2nd Year", "3rd Year", "4th Year"],
    },
    "bpharm": {
        "label": "B.Pharm",
        "icon": "💊",
        "years": ["1st Year", "2nd Year", "3rd Year", "4th Year"],
    },
    "mba": {
        "label": "MBA",
        "icon": "📊",
        "years": ["1st Year", "2nd Year"],
    },
    "mca": {
        "label": "MCA",
        "icon": "💻",
        "years": ["1st Year", "2nd Year"],
    },
}

YEAR_TO_SEMESTERS = {
    "1st Year": ["1st Semester", "2nd Semester"],
    "2nd Year": ["3rd Semester", "4th Semester"],
    "3rd Year": ["5th Semester", "6th Semester"],
    "4th Year": ["7th Semester", "8th Semester"],
}

RESOURCE_TYPES = [
    ("📚 Notes", "Notes"),
    ("📄 PYQs", "PYQs"),
    ("📘 Quantum", "Quantum"),
    ("📑 Syllabus", "Syllabus"),
    ("⭐ Important Questions", "Important Questions"),
]

COMING_SOON_TEXT = (
    "🚧 This section is coming soon!\n\n"
    "We’re working hard to bring this content for you.\n"
    "Stay connected with Notes Gallery 💙"
)

# Available links only. Everything else will show Coming Soon.
AVAILABLE_LINKS = {
    "btech": {
        "1st Year": {
            "Notes": f"{SITE}/aktu-b-tech-1st-year-free-study-materials/",
            "PYQs": f"{SITE}/aktu-pyqs/",
            "Quantum": f"{SITE}/quantums/",
            "Syllabus": f"{SITE}/latest-aktu-syllabus/",
        },
        "2nd Year": {
            "3rd Semester": {
                "Notes": f"{SITE}/aktu-b-tech-2nd-year-free-study-materials/",
                "PYQs": f"{SITE}/aktu-pyqs/",
                "Quantum": f"{SITE}/quantums/",
                "Syllabus": f"{SITE}/latest-aktu-syllabus/",
            },
            "4th Semester": {
                "Notes": f"{SITE}/aktu-b-tech-2nd-year-free-study-materials/",
                "PYQs": f"{SITE}/aktu-pyqs/",
                "Quantum": f"{SITE}/quantums/",
                "Syllabus": f"{SITE}/latest-aktu-syllabus/",
            },
        },
        "3rd Year": {
            "5th Semester": {
                "Notes": f"{SITE}/aktu-b-tech-3rd-year-free-study-materials/",
                "PYQs": f"{SITE}/aktu-pyqs/",
                "Quantum": f"{SITE}/quantums/",
                "Syllabus": f"{SITE}/latest-aktu-syllabus/",
            },
            "6th Semester": {
                "Notes": f"{SITE}/aktu-b-tech-3rd-year-free-study-materials/",
                "PYQs": f"{SITE}/aktu-pyqs/",
                "Quantum": f"{SITE}/quantums/",
                "Syllabus": f"{SITE}/latest-aktu-syllabus/",
            },
        },
        "4th Year": {
            "7th Semester": {
                "Syllabus": f"{SITE}/latest-aktu-syllabus/",
            },
            "8th Semester": {
                "Syllabus": f"{SITE}/latest-aktu-syllabus/",
            },
        },
    },

    "bpharm": {
        "1st Year": {
            "1st Semester": {"Notes": f"{SITE}/"},
            "2nd Semester": {"Notes": f"{SITE}/"},
        },
        "2nd Year": {
            "3rd Semester": {"Notes": f"{SITE}/"},
            "4th Semester": {"Notes": f"{SITE}/"},
        },
        "3rd Year": {
            "5th Semester": {"Notes": f"{SITE}/"},
            "6th Semester": {"Notes": f"{SITE}/"},
        },
        "4th Year": {
            "7th Semester": {"Notes": f"{SITE}/"},
            "8th Semester": {"Notes": f"{SITE}/"},
        },
    },

    "mba": {
        "1st Year": {
            "1st Semester": {
                "Notes": f"{SITE}/",
                "PYQs": f"{SITE}/",
            },
            "2nd Semester": {},
        },
        "2nd Year": {
            "3rd Semester": {
                "Notes": f"{SITE}/",
                "PYQs": f"{SITE}/",
            },
            "4th Semester": {},
        },
    },

    "mca": {
        "1st Year": {
            "1st Semester": {
                "Notes": f"{SITE}/",
                "Quantum": f"{SITE}/",
            },
            "2nd Semester": {
                "Notes": f"{SITE}/",
                "Quantum": f"{SITE}/",
            },
        },
        "2nd Year": {
            "3rd Semester": {},
            "4th Semester": {},
        },
    },
}


def get_user_key(chat_id: int, user_id: int) -> str:
    return f"{chat_id}_{user_id}"


async def delete_old_bot_message(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    key = get_user_key(chat_id, user_id)
    if key in user_last_message:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=user_last_message[key])
        except Exception:
            pass


async def send_clean_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None,
    parse_mode=None
):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Button click -> edit same message
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return
        except Exception:
            pass

    # Normal user message -> delete old bot message and send new
    await delete_old_bot_message(chat_id, user_id, context)

    sent = await update.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode=parse_mode
    )

    user_last_message[get_user_key(chat_id, user_id)] = sent.message_id


def home_keyboard():
    buttons = []
    row = []

    label_map = {
        "btech": "🎓 B.Tech",
        "bpharm": "💊 B.Pharm",
        "mba": "📊 MBA",
        "mca": "💻 MCA",
    }

    for course_key in COURSES.keys():
        row.append(InlineKeyboardButton(label_map[course_key], callback_data=f"course|{course_key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)


def years_keyboard(course_key: str):
    years = COURSES[course_key]["years"]
    buttons = [[InlineKeyboardButton(f"📅 {year}", callback_data=f"year|{course_key}|{year}")] for year in years]
    buttons.append([InlineKeyboardButton("🏠 Home", callback_data="home")])
    return InlineKeyboardMarkup(buttons)


def semesters_keyboard(course_key: str, year: str):
    semesters = YEAR_TO_SEMESTERS.get(year, [])
    buttons = [[InlineKeyboardButton(f"📘 {sem}", callback_data=f"sem|{course_key}|{year}|{sem}")] for sem in semesters]
    buttons.append([
        InlineKeyboardButton("🔙 Back", callback_data=f"course|{course_key}"),
        InlineKeyboardButton("🏠 Home", callback_data="home")
    ])
    return InlineKeyboardMarkup(buttons)


def resources_keyboard_for_year(course_key: str, year: str):
    buttons = [
        [InlineKeyboardButton(display_text, callback_data=f"res_year|{course_key}|{year}|{real_value}")]
        for display_text, real_value in RESOURCE_TYPES
    ]
    buttons.append([
        InlineKeyboardButton("🔙 Back", callback_data=f"course|{course_key}"),
        InlineKeyboardButton("🏠 Home", callback_data="home")
    ])
    return InlineKeyboardMarkup(buttons)


def resources_keyboard_for_sem(course_key: str, year: str, sem: str):
    buttons = [
        [InlineKeyboardButton(display_text, callback_data=f"res_sem|{course_key}|{year}|{sem}|{real_value}")]
        for display_text, real_value in RESOURCE_TYPES
    ]
    buttons.append([
        InlineKeyboardButton("🔙 Back", callback_data=f"year|{course_key}|{year}"),
        InlineKeyboardButton("🏠 Home", callback_data="home")
    ])
    return InlineKeyboardMarkup(buttons)


def resolve_year_resource(course_key: str, year: str, resource_type: str):
    course_data = AVAILABLE_LINKS.get(course_key, {})
    year_data = course_data.get(year, {})
    if isinstance(year_data, dict) and resource_type in year_data:
        return year_data[resource_type]
    return None


def resolve_sem_resource(course_key: str, year: str, sem: str, resource_type: str):
    course_data = AVAILABLE_LINKS.get(course_key, {})
    year_data = course_data.get(year, {})
    sem_data = year_data.get(sem, {}) if isinstance(year_data, dict) else {}
    return sem_data.get(resource_type)


def format_result_text(course_key: str, year: str, sem: str | None, resource_type: str, link: str):
    course_label = COURSES[course_key]["label"]
    course_icon = COURSES[course_key]["icon"]

    if sem:
        return (
            f"{course_icon} {course_label}\n"
            f"📅 {year}\n"
            f"📘 {sem}\n"
            f"📌 Resource: {resource_type}\n\n"
            f"🔗 Open here:\n{link}"
        )

    return (
        f"{course_icon} {course_label}\n"
        f"📅 {year}\n"
        f"📌 Resource: {resource_type}\n\n"
        f"🔗 Open here:\n{link}"
    )


def result_keyboard(course_key: str, year: str, sem: str | None):
    if sem:
        back_cb = f"sem|{course_key}|{year}|{sem}"
    else:
        back_cb = f"year|{course_key}|{year}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=back_cb)],
        [InlineKeyboardButton("🏠 Home", callback_data="home")]
    ])


async def start_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎓 Welcome to Notes Gallery Bot\n\n"
        "Choose your course to continue:"
    )
    await send_clean_message(update, context, text, reply_markup=home_keyboard())


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_flow(update, context)


async def resources_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_flow(update, context)


async def text_trigger_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()
    if any(keyword in text for keyword in TRIGGER_KEYWORDS):
        await start_flow(update, context)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split("|")
    action = parts[0]

    if data == "home":
        await send_clean_message(
            update,
            context,
            "🎓 Choose your course to continue:",
            reply_markup=home_keyboard()
        )
        return

    if action == "course":
        course_key = parts[1]
        course_label = COURSES[course_key]["label"]
        course_icon = COURSES[course_key]["icon"]
        await send_clean_message(
            update,
            context,
            f"{course_icon} {course_label}\n\nChoose your year of study:",
            reply_markup=years_keyboard(course_key)
        )
        return

    if action == "year":
        course_key, year = parts[1], parts[2]
        course_label = COURSES[course_key]["label"]
        course_icon = COURSES[course_key]["icon"]

        if course_key == "btech" and year == "1st Year":
            await send_clean_message(
                update,
                context,
                f"{course_icon} {course_label}\n📅 {year}\n\nChoose resource type:",
                reply_markup=resources_keyboard_for_year(course_key, year)
            )
            return

        await send_clean_message(
            update,
            context,
            f"{course_icon} {course_label}\n📅 {year}\n\nChoose semester:",
            reply_markup=semesters_keyboard(course_key, year)
        )
        return

    if action == "sem":
        course_key, year, sem = parts[1], parts[2], parts[3]
        course_label = COURSES[course_key]["label"]
        course_icon = COURSES[course_key]["icon"]

        await send_clean_message(
            update,
            context,
            f"{course_icon} {course_label}\n📅 {year}\n📘 {sem}\n\nChoose resource type:",
            reply_markup=resources_keyboard_for_sem(course_key, year, sem)
        )
        return

    if action == "res_year":
        course_key, year, resource_type = parts[1], parts[2], parts[3]
        link = resolve_year_resource(course_key, year, resource_type)

        if link:
            await send_clean_message(
                update,
                context,
                format_result_text(course_key, year, None, resource_type, link),
                reply_markup=result_keyboard(course_key, year, None)
            )
        else:
            await send_clean_message(
                update,
                context,
                COMING_SOON_TEXT,
                reply_markup=result_keyboard(course_key, year, None)
            )
        return

    if action == "res_sem":
        course_key, year, sem, resource_type = parts[1], parts[2], parts[3], parts[4]
        link = resolve_sem_resource(course_key, year, sem, resource_type)

        if link:
            await send_clean_message(
                update,
                context,
                format_result_text(course_key, year, sem, resource_type, link),
                reply_markup=result_keyboard(course_key, year, sem)
            )
        else:
            await send_clean_message(
                update,
                context,
                COMING_SOON_TEXT,
                reply_markup=result_keyboard(course_key, year, sem)
            )
        return


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Exception while handling update:", exc_info=context.error)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in environment variables.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("resources", resources_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_trigger_handler))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling(
        poll_interval=0.5,
        timeout=10,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
