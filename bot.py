import os
import logging
import threading
from flask import Flask
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

NEWS_URL = "https://notesgallery.com/latest-aktu-news-and-updates/"
INTERNSHIPS_URL = "https://notesgallery.com/jobs-internships-for-college-students/"

TRIGGER_KEYWORDS = [
    "notes", "note", "pyq", "pyqs", "previous year question", "previous year questions",
    "syllabus", "quantum", "pdf", "study material",
    "important question", "important questions", "imp question", "imp questions"
]

COMING_SOON = "COMING_SOON"
COMING_SOON_TEXT = (
    "🚧 Coming Soon...\n\n"
    "We’re working hard to bring this content for you.\n"
    "Stay connected with Notes Gallery 💙"
)

# --------------------------------------------------
# WEB SERVER FOR RENDER WEB SERVICE
# --------------------------------------------------
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bunny bot is alive!"

@web_app.route("/health")
def health():
    return {"status": "ok", "service": "bunny-bot"}

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# --------------------------------------------------
# BOT UI CONFIG
# --------------------------------------------------
COURSES = {
    "btech": {"label": "B.Tech", "icon": "💻"},
    "bpharm": {"label": "B.Pharm", "icon": "💊"},
    "mba": {"label": "MBA", "icon": "📊"},
    "mca": {"label": "MCA", "icon": "🖥"},
}

RESOURCE_TYPES = [
    ("📚 Notes", "Notes"),
    ("📄 PYQs", "PYQs"),
    ("⚡ Quantum", "Quantum"),
    ("📑 Syllabus", "Syllabus"),
    ("⭐ Important Questions", "Important Questions"),
]

BT_YEAR_OPTIONS = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
BPHARM_YEAR_OPTIONS = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
MBA_YEAR_OPTIONS = ["1st Year", "2nd Year"]
MCA_YEAR_OPTIONS = ["1st Year", "2nd Year", "3rd Year"]

YEAR_TO_SEMESTERS = {
    "1st Year": ["1st Semester", "2nd Semester"],
    "2nd Year": ["3rd Semester", "4th Semester"],
    "3rd Year": ["5th Semester", "6th Semester"],
    "4th Year": ["7th Semester", "8th Semester"],
}

BTECH_BRANCHES = {
    "2nd Year": {
        "3rd Semester": [
            ("💻 CSE", "cse"),
            ("🌐 IT", "it"),
            ("📡 ECE", "ece"),
            ("⚡ EEE/EN", "eee"),
            ("🏗 Civil", "civil"),
            ("⚙ Mechanical", "mech"),
            ("🧩 Open Elective", "oe"),
        ],
        "4th Semester": [
            ("💻 CSE", "cse"),
            ("🌐 IT", "it"),
            ("📡 ECE", "ece"),
            ("⚡ EEE/EN", "eee"),
            ("🏗 Civil", "civil"),
            ("⚙ Mechanical", "mech"),
            ("🧩 Open Elective", "oe"),
        ],
    },
    "3rd Year": {
        "5th Semester": [
            ("💻 CSE", "cse"),
            ("🤖 AI/ML", "aiml"),
            ("🧠 CSE(DS)", "cseds"),
            ("🌐 IT", "it"),
            ("📡 ECE", "ece"),
            ("⚡ EEE/EE", "eee"),
            ("🏗 Civil", "civil"),
            ("⚙ Mechanical", "mech"),
            ("🧩 Open Elective", "oe"),
        ],
        "6th Semester": [
            ("💻 CSE", "cse"),
            ("🤖 AI/ML", "aiml"),
            ("🧠 CSE(DS)", "cseds"),
            ("🌐 IT", "it"),
            ("📡 ECE", "ece"),
            ("⚡ EEE/EE", "eee"),
            ("🏗 Civil", "civil"),
            ("⚙ Mechanical", "mech"),
        ],
    },
}

# --------------------------------------------------
# LINK DATA
# --------------------------------------------------

BTECH_FIRST_YEAR = {
    "Notes": "https://notesgallery.com/aktu-notes/aktu-1st-year-notes-2/",
    "PYQs": "https://notesgallery.com/aktu-pyqs/1st-year-pyqs/",
    "Quantum": "https://notesgallery.com/quantum-series-pdfs/1st-year-quantum-pdf/",
    "Syllabus": "https://notesgallery.com/1st-year-syllabus-2025/",
    "Important Questions": COMING_SOON,
}

BTECH_BRANCH_LINKS = {
    "2nd Year": {
        "3rd Semester": {
            "cse": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/cse-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/cse-2nd-year-pyqs-pdf/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/cse-2nd-year-quantum-pdf-2/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "it": {
                "Notes": COMING_SOON,
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/it-2nd-year-pyqs/",
                "Quantum": COMING_SOON,
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "ece": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/ece-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/ece-2nd-year-pyqs/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/ece-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "eee": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/eee-en-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/eee-en-2nd-year-pyqs/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/eee-en-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "civil": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/civil-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/civil-2nd-year-pyqs/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/civil-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "mech": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/mechanical-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/mechanical-2nd-year-pyqs/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/mechanical-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "oe": {
                "Notes": "https://notesgallery.com/open-elective-notes-aktu-notes-2025-download/",
                "PYQs": "https://notesgallery.com/open-elective-pyqs-2nd-year-btech-aktu/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/open-elective-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
        },
        "4th Semester": {
            "cse": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/cse-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/cse-2nd-year-pyqs-pdf/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/cse-2nd-year-quantum-pdf-2/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "it": {
                "Notes": COMING_SOON,
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/it-2nd-year-pyqs/",
                "Quantum": COMING_SOON,
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "ece": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/ece-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/ece-2nd-year-pyqs/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/ece-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "eee": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/eee-en-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/eee-en-2nd-year-pyqs/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/eee-en-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "civil": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/civil-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/civil-2nd-year-pyqs/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/civil-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "mech": {
                "Notes": "https://notesgallery.com/aktu-notes/aktu-2nd-year-notes-2/mechanical-2nd-year-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-2nd-year-pyqs/mechanical-2nd-year-pyqs/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/mechanical-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
            "oe": {
                "Notes": "https://notesgallery.com/open-elective-notes-aktu-notes-2025-download/",
                "PYQs": "https://notesgallery.com/open-elective-pyqs-2nd-year-btech-aktu/",
                "Quantum": "https://notesgallery.com/quantum-series-pdfs/aktu-2nd-year-quantum-pdf-download-notes/open-elective-2nd-year-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-2nd-year-syllabus/",
                "Important Questions": COMING_SOON,
            },
        },
    },
    "3rd Year": {
        "5th Semester": {
            "cse": {
                "Notes": "https://notesgallery.com/computer-science-engineering-5th-semester-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/aktu-cse-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/cse-5th-semester-quantum-series-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "aiml": {
                "Notes": "https://notesgallery.com/aiml-5th-semester-notes-aktu/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/aiml-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/aiml-5th-semester-quantum-series-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "cseds": {
                "Notes": "https://notesgallery.com/cseds-5th-semester-notes/",
                "PYQs": "https://notesgallery.com/cseds-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/cse-ds-5th-semester-quantum-series-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "it": {
                "Notes": "https://notesgallery.com/it-5th-semester-notes/",
                "PYQs": COMING_SOON,
                "Quantum": "https://notesgallery.com/it-5th-semester-quantum-series-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "ece": {
                "Notes": "https://notesgallery.com/ece-5th-semester-notes-aktu/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/ece-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/ece-5th-semester-quantum-series-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "eee": {
                "Notes": "https://notesgallery.com/eee-ee-5th-semester-notes-aktu/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/eee-ee-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/en-eee-5th-semester-quantum-series-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "civil": {
                "Notes": "https://notesgallery.com/civil-engineering-5th-semester-notes-aktu/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/civil-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/civil-5th-semester-quantum-series-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "mech": {
                "Notes": "https://notesgallery.com/mechanical-5th-semester-notes-aktu/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/mechanical-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/mechanical-5th-semester-quantum-series-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "oe": {
                "Notes": "https://notesgallery.com/open-elective-3rd-year-b-tech/",
                "PYQs": COMING_SOON,
                "Quantum": COMING_SOON,
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
        },
        "6th Semester": {
            "cse": {
                "Notes": "https://notesgallery.com/tag/6th-semester-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/aktu-cse-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/latest-6th-sem-quantums-cse-and-allied-3rd-year/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "aiml": {
                "Notes": "https://notesgallery.com/aiml-6th-semester-notes-aktu-b-tech-free-pdf/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/aiml-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/latest-6th-sem-quantums-cse-and-allied-3rd-year/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "cseds": {
                "Notes": "https://notesgallery.com/cseds-6th-semester-notes-aktu-b-tech-free-pdf/",
                "PYQs": "https://notesgallery.com/cseds-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/latest-6th-sem-quantums-cse-and-allied-3rd-year/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "it": {
                "Notes": "https://notesgallery.com/it-6th-semester-notes-aktu-b-tech-free-pdf/",
                "PYQs": COMING_SOON,
                "Quantum": "https://notesgallery.com/latest-6th-sem-quantums-cse-and-allied-3rd-year/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "ece": {
                "Notes": "https://notesgallery.com/ece-6th-semester-notes-aktu-btech-free-pdf/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/ece-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/ece-6th-semester-quantums/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "eee": {
                "Notes": "https://notesgallery.com/eee-6th-semester-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/eee-ee-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/latest-6th-sem-eee-ee-quantums-3rd-year/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "civil": {
                "Notes": "https://notesgallery.com/civil-engineering-6th-semester-notes-aktu/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/civil-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/civil-engineering-6th-semester-quantum-pdf/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
            "mech": {
                "Notes": "https://notesgallery.com/6th-semester-mechanical-engineering-notes/",
                "PYQs": "https://notesgallery.com/aktu-pyqs/aktu-3rd-year-pyqs/mechanical-3rd-year-pyqs/",
                "Quantum": "https://notesgallery.com/6th-sem-mechanical-engineering-quantum-3rd-year/",
                "Syllabus": "https://notesgallery.com/aktu-3rd-year-syllabus-2024-25/",
                "Important Questions": COMING_SOON,
            },
        },
    },
}

BTECH_FOURTH_YEAR = {
    "7th Semester": {
        "Notes": COMING_SOON,
        "PYQs": COMING_SOON,
        "Quantum": COMING_SOON,
        "Syllabus": "https://notesgallery.com/4th-year-syllabus/",
        "Important Questions": COMING_SOON,
    },
    "8th Semester": {
        "Notes": COMING_SOON,
        "PYQs": COMING_SOON,
        "Quantum": COMING_SOON,
        "Syllabus": "https://notesgallery.com/4th-year-syllabus/",
        "Important Questions": COMING_SOON,
    },
}

BPHARM_LINKS = {
    "1st Year": {
        "1st Semester": {
            "Notes": "https://notesgallery.com/aktu-b-pharm-1st-semester-notes/",
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
        "2nd Semester": {
            "Notes": "https://notesgallery.com/aktu-bpharm-2nd-semester-notes/",
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
    },
    "2nd Year": {
        "3rd Semester": {
            "Notes": "https://notesgallery.com/aktu-bpharm-3rd-semester-notes/",
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
        "4th Semester": {
            "Notes": "https://notesgallery.com/aktu-bpharm-4th-semester-notes/",
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
    },
    "3rd Year": {
        "5th Semester": {
            "Notes": "https://notesgallery.com/aktu-bpharm-5th-semester-notes/",
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
        "6th Semester": {
            "Notes": "https://notesgallery.com/aktu-bpharm-6th-semester-notes/",
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
    },
    "4th Year": {
        "7th Semester": {
            "Notes": "https://notesgallery.com/aktu-bpharm-7th-semester-notes/",
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
        "8th Semester": {
            "Notes": "https://notesgallery.com/aktu-bpharm-8th-semester-notes/",
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
    },
}

MBA_LINKS = {
    "1st Year": {
        "1st Semester": {
            "Notes": "https://notesgallery.com/mba-1st-semester-notes-aktu/",
            "PYQs": "https://notesgallery.com/aktu-mba-1st-semester-pyqs/",
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
        "2nd Semester": {
            "Notes": COMING_SOON,
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
    },
    "2nd Year": {
        "3rd Semester": {
            "Notes": "https://notesgallery.com/mba-3rd-semester-notes-aktu/",
            "PYQs": "https://notesgallery.com/aktu-mba-3rd-semester-pyqs/",
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
        "4th Semester": {
            "Notes": COMING_SOON,
            "PYQs": COMING_SOON,
            "Quantum": COMING_SOON,
            "Syllabus": COMING_SOON,
            "Important Questions": COMING_SOON,
        },
    },
}

MCA_LINKS = {
    "1st Year": {
        "Notes": "https://notesgallery.com/1st-year-notes-aktu-mca-free-pdf/",
        "PYQs": COMING_SOON,
        "Quantum": "https://notesgallery.com/mca-1st-year-quantum-series-pdf/",
        "Syllabus": COMING_SOON,
        "Important Questions": COMING_SOON,
    },
    "2nd Year": {
        "Notes": COMING_SOON,
        "PYQs": COMING_SOON,
        "Quantum": COMING_SOON,
        "Syllabus": COMING_SOON,
        "Important Questions": COMING_SOON,
    },
    "3rd Year": {
        "Notes": COMING_SOON,
        "PYQs": COMING_SOON,
        "Quantum": COMING_SOON,
        "Syllabus": COMING_SOON,
        "Important Questions": COMING_SOON,
    },
}

# --------------------------------------------------
# MESSAGE STATE
# --------------------------------------------------
user_last_message = {}

def get_user_key(chat_id: int, user_id: int) -> str:
    return f"{chat_id}_{user_id}"

async def delete_old_bot_message(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    key = get_user_key(chat_id, user_id)
    if key in user_last_message:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=user_last_message[key])
        except Exception:
            pass

async def send_clean_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
            return
        except Exception:
            pass

    await delete_old_bot_message(chat_id, user_id, context)

    sent = await update.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )

    user_last_message[get_user_key(chat_id, user_id)] = sent.message_id

# --------------------------------------------------
# KEYBOARDS
# --------------------------------------------------
def with_footer(rows, back_cb=None, home=True):
    footer = []

    nav_row = []
    if back_cb:
        nav_row.append(InlineKeyboardButton("🔙 Back", callback_data=back_cb))
    if home:
        nav_row.append(InlineKeyboardButton("🏠 Home", callback_data="home"))
    if nav_row:
        footer.append(nav_row)

    footer.append([
        InlineKeyboardButton("📰 AKTU News", url=NEWS_URL),
        InlineKeyboardButton("💼 Latest Internships", url=INTERNSHIPS_URL),
    ])

    return InlineKeyboardMarkup(rows + footer)

def home_keyboard():
    rows = [
        [InlineKeyboardButton("💻 B.Tech", callback_data="course|btech"),
         InlineKeyboardButton("💊 B.Pharm", callback_data="course|bpharm")],
        [InlineKeyboardButton("📊 MBA", callback_data="course|mba"),
         InlineKeyboardButton("🖥 MCA", callback_data="course|mca")],
    ]
    return with_footer(rows, back_cb=None, home=False)

def year_keyboard(course_key: str):
    if course_key == "btech":
        years = BT_YEAR_OPTIONS
    elif course_key == "bpharm":
        years = BPHARM_YEAR_OPTIONS
    elif course_key == "mba":
        years = MBA_YEAR_OPTIONS
    else:
        years = MCA_YEAR_OPTIONS

    icon_map = {
        "1st Year": "🟢",
        "2nd Year": "🔵",
        "3rd Year": "🟠",
        "4th Year": "🔴",
    }

    rows = [
        [InlineKeyboardButton(f"{icon_map.get(year, '🔹')} {year}", callback_data=f"year|{course_key}|{year}")]
        for year in years
    ]
    return with_footer(rows, back_cb=None, home=True)

def semester_keyboard(course_key: str, year: str):
    semesters = YEAR_TO_SEMESTERS.get(year, [])
    rows = [[InlineKeyboardButton(f"📘 {sem}", callback_data=f"sem|{course_key}|{year}|{sem}")] for sem in semesters]
    return with_footer(rows, back_cb=f"course|{course_key}", home=True)

def branch_keyboard(year: str, sem: str):
    branches = BTECH_BRANCHES[year][sem]
    rows = [[InlineKeyboardButton(label, callback_data=f"branch|{year}|{sem}|{key}")] for label, key in branches]
    return with_footer(rows, back_cb=f"sem|btech|{year}|{sem}", home=True)

def resource_keyboard_for_year(course_key: str, year: str):
    rows = [[InlineKeyboardButton(display, callback_data=f"res_year|{course_key}|{year}|{real}")]
            for display, real in RESOURCE_TYPES]
    return with_footer(rows, back_cb=f"course|{course_key}", home=True)

def resource_keyboard_for_sem(course_key: str, year: str, sem: str):
    rows = [[InlineKeyboardButton(display, callback_data=f"res_sem|{course_key}|{year}|{sem}|{real}")]
            for display, real in RESOURCE_TYPES]
    return with_footer(rows, back_cb=f"year|{course_key}|{year}", home=True)

def resource_keyboard_for_branch(year: str, sem: str, branch: str):
    rows = [[InlineKeyboardButton(display, callback_data=f"res_branch|{year}|{sem}|{branch}|{real}")]
            for display, real in RESOURCE_TYPES]
    return with_footer(rows, back_cb=f"branchback|{year}|{sem}", home=True)

def result_keyboard(back_cb: str):
    rows = [[InlineKeyboardButton("🔙 Back", callback_data=back_cb)]]
    return with_footer(rows, back_cb=None, home=True)

def result_with_link_keyboard(link: str, back_cb: str):
    rows = [
        [InlineKeyboardButton("🚀 Open Link", url=link)],
        [InlineKeyboardButton("🔙 Back", callback_data=back_cb)],
    ]
    return with_footer(rows, back_cb=None, home=True)

# --------------------------------------------------
# RESOLVERS
# --------------------------------------------------
def get_btech_year_resource(year: str, resource_type: str):
    if year == "1st Year":
        return BTECH_FIRST_YEAR.get(resource_type, COMING_SOON)
    return COMING_SOON

def get_btech_sem_resource(year: str, sem: str, resource_type: str):
    if year == "4th Year":
        return BTECH_FOURTH_YEAR.get(sem, {}).get(resource_type, COMING_SOON)
    return COMING_SOON

def get_btech_branch_resource(year: str, sem: str, branch: str, resource_type: str):
    return BTECH_BRANCH_LINKS.get(year, {}).get(sem, {}).get(branch, {}).get(resource_type, COMING_SOON)

def get_bpharm_resource(year: str, sem: str, resource_type: str):
    return BPHARM_LINKS.get(year, {}).get(sem, {}).get(resource_type, COMING_SOON)

def get_mba_resource(year: str, sem: str, resource_type: str):
    return MBA_LINKS.get(year, {}).get(sem, {}).get(resource_type, COMING_SOON)

def get_mca_resource(year: str, resource_type: str):
    return MCA_LINKS.get(year, {}).get(resource_type, COMING_SOON)

def format_result(title_lines, resource_type, link):
    header = "\n".join(title_lines)
    return f"{header}\n📌 Resource: {resource_type}\n\n🔗 Link:\n{link}"

def branch_label_from_key(year: str, sem: str, branch_key: str):
    for label, key in BTECH_BRANCHES.get(year, {}).get(sem, []):
        if key == branch_key:
            return label
    return branch_key.upper()

# --------------------------------------------------
# HANDLERS
# --------------------------------------------------
async def start_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🎬 Welcome to Notes Gallery Bot\n\nChoose your course to continue:"
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

    if data == "home":
        await send_clean_message(update, context, "🎬 Choose your course to continue:", reply_markup=home_keyboard())
        return

    parts = data.split("|")
    action = parts[0]

    if action == "course":
        course_key = parts[1]
        course = COURSES[course_key]
        text = f"{course['icon']} {course['label']}\n\n🎯 Choose your year of study:"
        await send_clean_message(update, context, text, reply_markup=year_keyboard(course_key))
        return

    if action == "year":
        course_key, year = parts[1], parts[2]
        course = COURSES[course_key]

        if course_key == "btech" and year == "1st Year":
            text = f"{course['icon']} {course['label']}\n🟢 {year}\n\n🔥 Choose resource type:"
            await send_clean_message(update, context, text, reply_markup=resource_keyboard_for_year(course_key, year))
            return

        if course_key == "mca":
            year_icon = {"1st Year": "🟢", "2nd Year": "🔵", "3rd Year": "🟠"}.get(year, "🔹")
            text = f"{course['icon']} {course['label']}\n{year_icon} {year}\n\n🔥 Choose resource type:"
            await send_clean_message(update, context, text, reply_markup=resource_keyboard_for_year(course_key, year))
            return

        year_icon = {"1st Year": "🟢", "2nd Year": "🔵", "3rd Year": "🟠", "4th Year": "🔴"}.get(year, "🔹")
        text = f"{course['icon']} {course['label']}\n{year_icon} {year}\n\n📘 Choose semester:"
        await send_clean_message(update, context, text, reply_markup=semester_keyboard(course_key, year))
        return

    if action == "sem":
        course_key, year, sem = parts[1], parts[2], parts[3]
        course = COURSES[course_key]
        year_icon = {"1st Year": "🟢", "2nd Year": "🔵", "3rd Year": "🟠", "4th Year": "🔴"}.get(year, "🔹")

        if course_key == "btech" and year in ["2nd Year", "3rd Year"]:
            text = f"{course['icon']} {course['label']}\n{year_icon} {year}\n📘 {sem}\n\n🎯 Choose branch:"
            await send_clean_message(update, context, text, reply_markup=branch_keyboard(year, sem))
            return

        text = f"{course['icon']} {course['label']}\n{year_icon} {year}\n📘 {sem}\n\n🔥 Choose resource type:"
        await send_clean_message(update, context, text, reply_markup=resource_keyboard_for_sem(course_key, year, sem))
        return

    if action == "branch":
        year, sem, branch = parts[1], parts[2], parts[3]
        branch_label = branch_label_from_key(year, sem, branch)
        year_icon = {"2nd Year": "🔵", "3rd Year": "🟠"}.get(year, "🔹")
        text = f"💻 B.Tech\n{year_icon} {year}\n📘 {sem}\n🏷️ {branch_label}\n\n🔥 Choose resource type:"
        await send_clean_message(update, context, text, reply_markup=resource_keyboard_for_branch(year, sem, branch))
        return

    if action == "branchback":
        year, sem = parts[1], parts[2]
        text = f"💻 B.Tech\n📘 {sem}\n\n🎯 Choose branch:"
        await send_clean_message(update, context, text, reply_markup=branch_keyboard(year, sem))
        return

    if action == "res_year":
        course_key, year, resource_type = parts[1], parts[2], parts[3]
        course = COURSES[course_key]

        if course_key == "btech":
            link = get_btech_year_resource(year, resource_type)
        elif course_key == "mca":
            link = get_mca_resource(year, resource_type)
        else:
            link = COMING_SOON

        if link == COMING_SOON:
            await send_clean_message(update, context, COMING_SOON_TEXT,
                                     reply_markup=result_keyboard(back_cb=f"year|{course_key}|{year}"))
        else:
            year_icon = {"1st Year": "🟢", "2nd Year": "🔵", "3rd Year": "🟠", "4th Year": "🔴"}.get(year, "🔹")
            text = format_result([f"{course['icon']} {course['label']}", f"{year_icon} {year}"], resource_type, link)
            await send_clean_message(update, context, text,
                                     reply_markup=result_with_link_keyboard(link, back_cb=f"year|{course_key}|{year}"))
        return

    if action == "res_sem":
        course_key, year, sem, resource_type = parts[1], parts[2], parts[3], parts[4]
        course = COURSES[course_key]

        if course_key == "bpharm":
            link = get_bpharm_resource(year, sem, resource_type)
        elif course_key == "mba":
            link = get_mba_resource(year, sem, resource_type)
        elif course_key == "btech":
            link = get_btech_sem_resource(year, sem, resource_type)
        else:
            link = COMING_SOON

        if link == COMING_SOON:
            await send_clean_message(update, context, COMING_SOON_TEXT,
                                     reply_markup=result_keyboard(back_cb=f"sem|{course_key}|{year}|{sem}"))
        else:
            year_icon = {"1st Year": "🟢", "2nd Year": "🔵", "3rd Year": "🟠", "4th Year": "🔴"}.get(year, "🔹")
            text = format_result([f"{course['icon']} {course['label']}", f"{year_icon} {year}", f"📘 {sem}"], resource_type, link)
            await send_clean_message(update, context, text,
                                     reply_markup=result_with_link_keyboard(link, back_cb=f"sem|{course_key}|{year}|{sem}"))
        return

    if action == "res_branch":
        year, sem, branch, resource_type = parts[1], parts[2], parts[3], parts[4]
        link = get_btech_branch_resource(year, sem, branch, resource_type)
        branch_label = branch_label_from_key(year, sem, branch)
        year_icon = {"2nd Year": "🔵", "3rd Year": "🟠"}.get(year, "🔹")

        if link == COMING_SOON:
            await send_clean_message(update, context, COMING_SOON_TEXT,
                                     reply_markup=result_keyboard(back_cb=f"branch|{year}|{sem}|{branch}"))
        else:
            text = format_result(["💻 B.Tech", f"{year_icon} {year}", f"📘 {sem}", f"🏷️ {branch_label}"], resource_type, link)
            await send_clean_message(update, context, text,
                                     reply_markup=result_with_link_keyboard(link, back_cb=f"branch|{year}|{sem}|{branch}"))
        return

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Exception while handling update:", exc_info=context.error)

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in environment variables.")

    threading.Thread(target=run_web_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("resources", resources_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_trigger_handler))
    app.add_error_handler(error_handler)

    print("Bot + Web server is running...")
    app.run_polling(
        poll_interval=0.5,
        timeout=10,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
