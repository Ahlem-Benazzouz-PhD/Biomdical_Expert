# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 15:11:34 2026

@author: Dr Ahlem BENAZZOUZ, PhD
"""

# -*- coding: utf-8 -*-
"""
Biomedical Instrumentation Assistant
CustomTkinter rounded chat interface

Multi-Agent Workflow:
    1. User provides laboratory components.
    2. Project subagent proposes project options.
    3. User selects a project.
    4. Assistant identifies required components.
    5. User verifies component availability.
    6. YES -> complete project generation.
    7. NO -> ask whether to search Algerian suppliers.
    8. YES -> supplier subagent searches Algerian suppliers.
    9. NO -> explain why project cannot be finalized.
   10. New Chat resets workflow state.

GUI intentionally preserved from the original baseline.
"""

import os
import re
import math
import json
import wave
import tempfile
import threading
import subprocess
import tkinter as tk
import tkinter.font as tkfont

from dataclasses import dataclass
from tkinter import messagebox
from pathlib import Path
from array import array


# =============================================================
# CUSTOMTKINTER
# =============================================================

try:
    import customtkinter as ctk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    ctk = None
    CUSTOMTKINTER_AVAILABLE = False


# =============================================================
# OPTIONAL IMAGE LIBRARY
# =============================================================

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None


# =============================================================
# DOTENV
# =============================================================

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass


# =============================================================
# LANGCHAIN / GEMINI / MIDDLEWARE
# =============================================================

try:
    from langchain.agents import create_agent
    from langchain.messages import HumanMessage
    from langchain.agents.middleware import (
        dynamic_prompt,
        ModelRequest
    )
    from langchain_google_genai import ChatGoogleGenerativeAI

    LANGCHAIN_AVAILABLE = True

except ImportError:
    create_agent = None
    HumanMessage = None
    dynamic_prompt = None
    ModelRequest = None
    ChatGoogleGenerativeAI = None

    LANGCHAIN_AVAILABLE = False


# =============================================================
# TAVILY
# =============================================================

try:
    from langchain_community.tools.tavily_search import (
        TavilySearchResults
    )
except ImportError:
    TavilySearchResults = None


# =============================================================
# VOICE
# =============================================================

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    PYTTSX3_AVAILABLE = False


# =============================================================
# WINDOWS SOUND
# =============================================================

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    winsound = None
    WINSOUND_AVAILABLE = False


# =============================================================
# APPLICATION SETTINGS
# =============================================================

APP_TITLE = "Biomedical Instrumentation Assistant"

WINDOW_WIDTH = 1250
WINDOW_HEIGHT = 780


# =============================================================
# LIGHT MODE COLORS
# =============================================================

BG_MAIN = "#eef6ff"
BG_HEADER = "#e7f1ff"
BG_AVATAR = "#dcecff"
BG_CHAT = "#ffffff"
BG_CHAT_AREA = "#f8fbff"
BG_INPUT = "#f8fbff"

PRIMARY = "#1677d2"
PRIMARY_DARK = "#0e62b0"

TEXT_DARK = "#173b6c"
TEXT_NORMAL = "#24496f"
TEXT_MUTED = "#71849b"


# =============================================================
# MESSAGE BUBBLES
# =============================================================

USER_BUBBLE = "#e4f1ff"
USER_BUBBLE_BORDER = "#c5def6"

EXPERT_BUBBLE = "#ffffff"
EXPERT_BUBBLE_BORDER = "#dce7f2"

SYSTEM_BUBBLE = "#f0f5fa"


# =============================================================
# DARK MODE COLORS
# =============================================================

DARK_BG_MAIN = "#0d151d"
DARK_BG_HEADER = "#15212c"
DARK_BG_AVATAR = "#172630"
DARK_BG_CHAT = "#17232e"
DARK_BG_CHAT_AREA = "#101a23"
DARK_BG_INPUT = "#1a2935"

DARK_TEXT_DARK = "#e7f2fa"
DARK_TEXT_NORMAL = "#d0dfeb"
DARK_TEXT_MUTED = "#98aaba"

DARK_BORDER = "#304655"

DARK_USER_BUBBLE = "#203b52"
DARK_USER_BUBBLE_BORDER = "#355873"

DARK_EXPERT_BUBBLE = "#1e2d38"
DARK_EXPERT_BUBBLE_BORDER = "#344b5b"

DARK_SYSTEM_BUBBLE = "#24333e"


# =============================================================
# LANGUAGE CONTEXT
# =============================================================

@dataclass
class LanguageContext:
    """
    Runtime context passed to LangChain.

    The language is selected by the user in the GUI and is
    injected into every agent invocation.
    """

    language: str = "English"


# =============================================================
# SUPPORTED LANGUAGES
# =============================================================

SUPPORTED_LANGUAGES = {
    "English": {
        "native": "English",
        "code": "en",
        "rtl": False
    },

    "Français": {
        "native": "French",
        "code": "fr",
        "rtl": False
    },

    "العربية": {
        "native": "Arabic",
        "code": "ar",
        "rtl": True
    }
}


# =============================================================
# LOCALIZED UI TEXT
# =============================================================

LANGUAGE_TEXT = {

    "English": {
        "hello": "Hello!👋 ",
        "expert": "I am a Biomedical Instrumentation Expert.",
        "help": "How can I help you with your biomedical project?",
        "thinking": "Biomedical Expert is thinking...",
        "ready": "Ready",
        "testing_voice": "Testing Windows voice...",
        "voice_test": "Testing voice...",
        "recommendation": "Here is what I recommend.",
        "send": "Send  ➤",
        "thinking_button": "Thinking...",
        "user": "You",
        "expert_name": "Biomedical Expert",
        "system": "System",
        "language": "language",
        "mode": "mode",
        "voice": "🔊  Test Voice",
        "chat_title": "💬  Biomedical Project Assistant",
        "new_chat": "＋ New Chat"
    },

    "Français": {
        "hello": "Bonjour ! 👋",
        "expert": "Je suis un expert en instrumentation biomédicale.",
        "help": "Comment puis-je vous aider dans votre projet biomédical ?",
        "thinking": "L’expert biomédical réfléchit...",
        "ready": "Prêt",
        "testing_voice": "Test de la voix Windows...",
        "voice_test": "Test de la voix...",
        "recommendation": "Voici ce que je vous recommande.",
        "send": "Envoyer  ➤",
        "thinking_button": "Réflexion...",
        "user": "Vous",
        "expert_name": "Expert biomédical",
        "system": "Système",
        "language": "langue",
        "mode": "mode",
        "voice": "🔊  Tester la voix",
        "chat_title": "💬  Assistant de projet biomédical",
        "new_chat": "＋ Nouveau chat"
    },

    "العربية": {
        "hello": "مرحباً! 👋",
        "expert": "أنا خبير في الأجهزة والأنظمة الطبية الحيوية.",
        "help": "كيف يمكنني مساعدتك في مشروعك الطبي الحيوي؟",
        "thinking": "الخبير في الأجهزة الطبية الحيوية يفكر...",
        "ready": "جاهز",
        "testing_voice": "جارٍ اختبار صوت Windows...",
        "voice_test": "اختبار الصوت...",
        "recommendation": "إليك ما أوصي به.",
        "send": "إرسال  ➤",
        "thinking_button": "جارٍ التفكير...",
        "user": "أنت",
        "expert_name": "الخبير في الأجهزة الطبية الحيوية",
        "system": "النظام",
        "language": "اللغة",
        "mode": "الوضع",
        "voice": "🔊  اختبار الصوت",
        "chat_title": "💬  مساعد المشاريع الطبية الحيوية",
        "new_chat": "＋ محادثة جديدة"
    }
}


# =============================================================
# BASE SYSTEM PROMPT
# =============================================================

SYSTEM_PROMPT = """
You are a Biomedical Instrumentation Expert assisting researchers,
biomedical engineers, students, and healthcare technology developers.

Your expertise includes:

* Biomedical instrumentation
* ECG
* EEG
* EMG
* EOG
* PPG
* Biosensors
* Analog front-end circuits
* Instrumentation amplifiers
* Filters
* Signal acquisition
* ADC
* ESP32 and embedded systems
* MATLAB
* Python
* Biomedical signal processing
* Machine learning and AI for healthcare
* Medical devices
* Human-computer interfaces
* BCI and HCI
* Data acquisition systems
* PCB and prototype development

Give practical, technically accurate and structured answers.

### Laboratory-First Approach

When the user starts the chat, and they have not yet provided information
about the electronic components available in their laboratory:

Do not immediately propose a circuit, component list, or complete
hardware architecture.

Instead, first ask the user:

"What electronic components do you have in your lab?"

Wait for the user's answer before proposing the hardware design.

Prioritize the components available in the lab and only suggest
additional components when necessary.

Once the user provides the available components,
prioritize those components when designing the project.

If an additional component is genuinely required, clearly identify it as
an additional required component and explain why it is needed.

When the user selects one of the proposed biomedical projects,
preferably organize the response using useful headings such as:

---- Objective

---- Recommended Architecture

---- Components

---- Signal Processing

---- Implementation

---- Testing

---- Safety Considerations

Use Markdown formatting.

Use bold text for important technical terms.

Use bullet points and numbered lists when appropriate.

When explaining circuits or signal-processing systems,
explain the signal path clearly.

Prefer realistic, low-cost laboratory prototypes when appropriate.

Do not present a laboratory prototype as a clinically certified
medical device.

Mention safety, isolation, patient protection and regulatory
considerations whenever they are relevant.

If web search is available, use it when current component
documentation, standards, datasheets or recent technical
information is needed.

Do not unnecessarily repeat the question.

When the user asks for details, provide detailed technical explanations,
including equations, signal paths, circuit principles, implementation
steps, assumptions and practical considerations when appropriate.

When the user asks for a simple answer, remain concise.

Always prioritize technical correctness, practical feasibility,
laboratory availability and biomedical safety.
"""


# =============================================================
# PROJECT SUBAGENT PROMPT
# =============================================================

PROJECT_AGENT_PROMPT = """
You are the Project Design Subagent of a Biomedical Instrumentation
Assistant.

Your role is to design practical biomedical instrumentation laboratory
projects based primarily on components explicitly provided by the user.

IMPORTANT WORKFLOW RULES:

1. Do not search for suppliers.
2. Do not recommend suppliers.
3. Do not perform supplier searches.
4. Do not assume a missing component is available.
5. Prefer projects that maximize the use of laboratory components.
6. Prefer realistic, low-cost university laboratory prototypes.
7. Never present a prototype as a clinically certified medical device.

When laboratory components are provided, propose several project
options.

For each project option provide:

- Project title
- Objective
- Main principle
- Main available components used
- Required components
- Expected output
- Main signal path
- Difficulty level

When the user selects a project, identify its complete required
component list.

Separate:

- Required components
- Components already available
- Components that are missing

The project cannot be considered ready until the user confirms
that the required components are physically available.

When generating the final project, include when appropriate:

- Objective
- Recommended architecture
- Circuit architecture
- Components
- Signal path
- Circuit principles
- Component values
- Power supply
- Signal acquisition
- Signal conditioning
- Filtering
- Embedded system
- Software
- Signal processing
- Testing
- Expected results
- Safety considerations
- Practical implementation

Always answer in the user's selected language.
"""


# =============================================================
# SUPPLIER SUBAGENT PROMPT
# =============================================================

SUPPLIER_AGENT_PROMPT = """
You are the Algerian Biomedical Components Supplier Subagent.

Your ONLY task is to search for suppliers in Algeria for components
that are explicitly identified as missing from a selected biomedical
instrumentation project.

IMPORTANT:

Supplier research is authorized ONLY when the application has already
confirmed that the user explicitly answered YES to the supplier-search
question.

You must never initiate supplier research yourself.

For each missing component, search for relevant Algerian suppliers.

Return a compact table:

| Supplier | Website | Components | Contact | Price |

Rules:

- Prefer suppliers operating in Algeria.
- Include the supplier website when available.
- Include contact information when available.
- Include price when publicly available.
- If price is unavailable, write "Not available".
- Never invent prices.
- Never invent websites.
- Never invent telephone numbers.
- Never invent email addresses.
- Never claim availability without evidence.
- Clearly distinguish unavailable information.
- Keep the supplier result compact.
- Do not redesign the biomedical project.
- Do not replace the project subagent.
- Do not generate a complete project.

Always answer in the user's selected language.
"""


# =============================================================
# DYNAMIC LANGUAGE PROMPT
# =============================================================

if dynamic_prompt is not None:

    @dynamic_prompt
    def dynamic_language_prompt(
        request: ModelRequest
    ) -> str:

        try:
            language = request.runtime.context.language
        except Exception:
            language = "English"

        language_data = SUPPORTED_LANGUAGES.get(
            language,
            SUPPORTED_LANGUAGES["English"]
        )

        language_name = language_data["native"]

        language_instruction = f"""

### User Language

The user's selected language is: {language_name}.

You MUST answer the user in {language_name}.

Rules:

1. Write the complete answer in {language_name}.
2. Do not switch to English unless the user explicitly asks for English.
3. Technical terms may include their standard international
   abbreviation, such as ECG, EEG, EMG, EOG, PPG, ADC, ESP32,
   MATLAB and Python.
4. Explain those technical terms in {language_name} when appropriate.
5. Keep code, Python syntax, MATLAB syntax, component names,
   electronic symbols and standard technical notation unchanged.
6. If the user asks for a detailed explanation, provide the details
   in {language_name}.
7. If the user asks for a short answer, keep it concise in
   {language_name}.
8. Maintain the same technical accuracy regardless of language.
9. Do not mention this language instruction to the user.

"""

        return SYSTEM_PROMPT + language_instruction

else:
    dynamic_language_prompt = None


# =============================================================
# APPLICATION
# =============================================================

class BiomedicalExpertApp:

    def __init__(self, root):

        self.root = root

        # -----------------------------------------------------
        # CUSTOMTKINTER APPEARANCE
        # -----------------------------------------------------

        if CUSTOMTKINTER_AVAILABLE:
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")

        # -----------------------------------------------------
        # WINDOW
        # -----------------------------------------------------

        self.root.title(APP_TITLE)

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.minsize(
            1000,
            650
        )

        self.root.configure(
            bg=BG_MAIN
        )

        icon_path = (
            Path(__file__).parent
            / "assets"
            / "icon.ico"
        )

        if icon_path.exists():
            self.root.iconbitmap(
                str(icon_path)
            )

        load_dotenv()

        # -----------------------------------------------------
        # CURRENT MODE
        # -----------------------------------------------------

        self.current_mode = "Light"

        self._set_initial_colors()

        # -----------------------------------------------------
        # CURRENT LANGUAGE
        # -----------------------------------------------------

        self.current_language = "English"

        self.language_context = LanguageContext(
            language=self.current_language
        )

        # -----------------------------------------------------
        # BACKGROUND IMAGE STATE
        # -----------------------------------------------------

        self.avatar_background_image = None
        self.avatar_background_item = None

        self.light_background_path = (
            Path(__file__).parent
            / "assets"
            / "image_1.png"
        )

        self.dark_background_path = (
            Path(__file__).parent
            / "assets"
            / "image_2.png"
        )

        # -----------------------------------------------------
        # AVATAR STATE
        # -----------------------------------------------------

        self.expert_photo = None
        self.expert_image_item = None
        self.fallback_avatar_item = None

        # -----------------------------------------------------
        # BUBBLE STATE
        # -----------------------------------------------------

        self.bubble_text = None

        # -----------------------------------------------------
        # THINKING DOTS
        # -----------------------------------------------------

        self.waiting_labels = []

        # -----------------------------------------------------
        # GENERAL STATE
        # -----------------------------------------------------

        self.agent = None

        # -----------------------------------------------------
        # MULTI-AGENT STATE
        # -----------------------------------------------------

        self.project_agent = None
        self.supplier_agent = None

        self.workflow_state = (
            "WAITING_FOR_LAB_COMPONENTS"
        )

        self.lab_components = []
        self.project_options = []
        self.selected_project = None

        self.required_components = []
        self.available_components = []
        self.missing_components = []

        self.supplier_search_explicitly_confirmed = False

        self.workflow_context = {}

        # -----------------------------------------------------
        # APPLICATION STATE
        # -----------------------------------------------------

        self.busy = False
        self.thinking_animation = False
        self.thinking_step = 0
        self.bubble_animation_running = False

        # -----------------------------------------------------
        # VOICE STATE
        # -----------------------------------------------------

        self.voice_lock = threading.Lock()
        self.voice_available = False

        # -----------------------------------------------------
        # THINKING SOUND
        # -----------------------------------------------------

        self.thinking_sound_path = None
        self.thinking_sound_playing = False

        self._prepare_thinking_sound()

        # -----------------------------------------------------
        # BUILD AI
        # -----------------------------------------------------

        self._build_agent()

        # -----------------------------------------------------
        # BUILD UI
        # -----------------------------------------------------

        self._build_ui()

        # -----------------------------------------------------
        # WINDOW CLOSE
        # -----------------------------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self._on_close
        )

        # -----------------------------------------------------
        # WELCOME
        # -----------------------------------------------------

        self._show_welcome()

    # =========================================================
    # INITIAL COLORS
    # =========================================================

    def _set_initial_colors(self):

        self.current_bg_main = BG_MAIN
        self.current_header = BG_HEADER
        self.current_avatar = BG_MAIN

        self.current_chat = BG_CHAT
        self.current_chat_area = BG_CHAT_AREA
        self.current_input = BG_INPUT

        self.current_text_dark = TEXT_DARK
        self.current_text_normal = TEXT_NORMAL
        self.current_text_muted = TEXT_MUTED

        self.current_border = "#d6e4f2"

        self.current_user_bubble = USER_BUBBLE
        self.current_user_border = USER_BUBBLE_BORDER

        self.current_expert_bubble = EXPERT_BUBBLE
        self.current_expert_border = EXPERT_BUBBLE_BORDER

        self.current_system_bubble = SYSTEM_BUBBLE

        self.current_mode_bg = "#ffffff"
        self.current_mode_fg = TEXT_DARK
        self.current_mode_active = "#dcecff"

    # =========================================================
    # LANGUAGE HELPER
    # =========================================================

    def _language_text(
        self,
        key
    ):

        language_data = LANGUAGE_TEXT.get(
            self.current_language,
            LANGUAGE_TEXT["English"]
        )

        return language_data.get(
            key,
            LANGUAGE_TEXT["English"].get(
                key,
                key
            )
        )

    # =========================================================
    # LANGUAGE DIRECTION
    # =========================================================

    def _is_rtl(self):

        return SUPPORTED_LANGUAGES.get(
            self.current_language,
            {}
        ).get(
            "rtl",
            False
        )

    # =========================================================
    # CHANGE LANGUAGE
    # =========================================================

    def _change_language(
        self,
        language
    ):

        if language.startswith("✓ "):
            language = language[2:]

        if language not in SUPPORTED_LANGUAGES:
            language = "English"

        self.current_language = language

        self.language_context = LanguageContext(
            language=language
        )

        self.language_var.set(
            f"✓ {language}"
        )

        menu = self.language_menu["menu"]

        menu.delete(
            0,
            "end"
        )

        for item in SUPPORTED_LANGUAGES:

            label = (
                f"✓ {item}"
                if item == language
                else item
            )

            menu.add_command(
                label=label,
                command=lambda value=item:
                self._change_language(value)
            )

        menu.configure(
            font=("Segoe UI", 9),
            bg=self.current_mode_bg,
            fg=self.current_mode_fg,
            activebackground=self.current_mode_active,
            activeforeground=self.current_mode_fg
        )

        self._update_language_ui()

        if hasattr(
            self,
            "bubble_text"
        ):

            self.avatar_panel.itemconfig(
                self.bubble_text,
                justify=(
                    "right"
                    if self._is_rtl()
                    else "center"
                )
            )

        if hasattr(
            self,
            "status"
        ):

            self.status.configure(
                text=self._language_text("ready")
            )

    # =========================================================
    # UPDATE LANGUAGE UI
    # =========================================================

    def _update_language_ui(self):

        if hasattr(
            self,
            "mode_label"
        ):

            self.mode_label.configure(
                text=self._language_text("mode")
            )

        if hasattr(
            self,
            "language_label"
        ):

            self.language_label.configure(
                text=self._language_text("language")
            )

        if hasattr(
            self,
            "voice_test_btn"
        ):

            self.voice_test_btn.configure(
                text=self._language_text("voice")
            )

        if hasattr(
            self,
            "new_chat_btn"
        ):

            self.new_chat_btn.configure(
                text=self._language_text("new_chat")
            )

        if hasattr(
            self,
            "chat_title"
        ):

            self.chat_title.configure(
                text=self._language_text("chat_title")
            )

        if hasattr(
            self,
            "send_btn"
        ) and not self.busy:

            self.send_btn.configure(
                text=self._language_text("send")
            )

    # =========================================================
    # THINKING SOUND
    # =========================================================

    def _prepare_thinking_sound(self):

        if not WINSOUND_AVAILABLE:
            return

        try:

            sample_rate = 22050
            note_duration = 0.65

            notes = [
                261.63,
                329.63,
                392.00,
                329.63
            ]

            samples = array("h")
            amplitude = 850

            for frequency in notes:

                count = int(
                    sample_rate * note_duration
                )

                fade_samples = int(
                    sample_rate * 0.08
                )

                for i in range(count):

                    t = i / sample_rate

                    value = math.sin(
                        2 * math.pi * frequency * t
                    )

                    envelope = 1.0

                    if i < fade_samples:
                        envelope = i / fade_samples

                    elif i > count - fade_samples:
                        envelope = (
                            (count - i)
                            / fade_samples
                        )

                    sample = int(
                        amplitude
                        * value
                        * envelope
                    )

                    samples.append(sample)

            sound_path = (
                Path(tempfile.gettempdir())
                / "biomedical_expert_thinking.wav"
            )

            with wave.open(
                str(sound_path),
                "wb"
            ) as wav_file:

                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)

                wav_file.writeframes(
                    samples.tobytes()
                )

            self.thinking_sound_path = sound_path

            print(
                "Thinking sound:",
                sound_path
            )

        except Exception as exc:

            print(
                "Could not create thinking sound:",
                repr(exc)
            )

            self.thinking_sound_path = None

    # =========================================================
    # START THINKING SOUND
    # =========================================================

    def _start_thinking_sound(self):

        if (
            not WINSOUND_AVAILABLE
            or self.thinking_sound_path is None
        ):
            return

        try:

            winsound.PlaySound(
                str(self.thinking_sound_path),
                winsound.SND_FILENAME
                | winsound.SND_ASYNC
                | winsound.SND_LOOP
            )

            self.thinking_sound_playing = True

        except Exception as exc:

            print(
                "Thinking sound error:",
                repr(exc)
            )

    # =========================================================
    # STOP THINKING SOUND
    # =========================================================

    def _stop_thinking_sound(self):

        if not WINSOUND_AVAILABLE:
            return

        try:

            winsound.PlaySound(
                None,
                winsound.SND_PURGE
            )

            self.thinking_sound_playing = False

        except Exception as exc:

            print(
                "Could not stop thinking sound:",
                repr(exc)
            )

    # =========================================================
    # AI AGENTS
    # =========================================================

    def _build_agent(self):

        self.agent = None
        self.project_agent = None
        self.supplier_agent = None

        if (
            ChatGoogleGenerativeAI is None
            or create_agent is None
            or dynamic_language_prompt is None
        ):

            print(
                "LangChain/Gemini/middleware libraries "
                "are unavailable."
            )

            return

        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if not api_key:

            print(
                "No GOOGLE_API_KEY or GEMINI_API_KEY found."
            )

            return

        model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.1-flash-lite"
        )

        try:

            model = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.2
            )

            # -------------------------------------------------
            # GENERAL TOOLS
            # -------------------------------------------------

            tools = []

            tavily_key = os.getenv(
                "TAVILY_API_KEY"
            )

            if (
                tavily_key
                and TavilySearchResults is not None
            ):

                try:

                    tools.append(
                        TavilySearchResults(
                            max_results=5
                        )
                    )

                    print(
                        "Tavily search enabled."
                    )

                except Exception as exc:

                    print(
                        "Tavily initialization failed:",
                        repr(exc)
                    )

            # -------------------------------------------------
            # MAIN BIOMEDICAL EXPERT
            # -------------------------------------------------

            self.agent = create_agent(
                model=model,
                tools=tools,
                middleware=[
                    dynamic_language_prompt
                ],
                context_schema=LanguageContext
            )

            # -------------------------------------------------
            # PROJECT SUBAGENT
            #
            # IMPORTANT:
            # No supplier tools.
            # -------------------------------------------------

            self.project_agent = create_agent(
                model=model,
                tools=[],
                middleware=[
                    dynamic_language_prompt
                ],
                context_schema=LanguageContext
            )

            # -------------------------------------------------
            # SUPPLIER SUBAGENT
            #
            # Supplier agent receives Tavily, but Python
            # workflow controls when it is allowed to run.
            # -------------------------------------------------

            supplier_tools = []

            if (
                tavily_key
                and TavilySearchResults is not None
            ):

                try:

                    supplier_tools.append(
                        TavilySearchResults(
                            max_results=5
                        )
                    )

                    print(
                        "Supplier Tavily search enabled."
                    )

                except Exception as exc:

                    print(
                        "Supplier Tavily initialization failed:",
                        repr(exc)
                    )

            self.supplier_agent = create_agent(
                model=model,
                tools=supplier_tools,
                middleware=[
                    dynamic_language_prompt
                ],
                context_schema=LanguageContext
            )

            print(
                "Gemini agent initialized successfully."
            )

            print(
                "Project subagent initialized."
            )

            print(
                "Supplier subagent initialized."
            )

            print(
                "Dynamic language middleware enabled."
            )

        except Exception as exc:

            print(
                "Agent initialization error:",
                repr(exc)
            )

            self.agent = None
            self.project_agent = None
            self.supplier_agent = None

    # =========================================================
    # USER INTERFACE
    # =========================================================

    def _build_ui(self):

        # =====================================================
        # HEADER
        # =====================================================

        self.header = tk.Frame(
            self.root,
            bg=BG_HEADER,
            height=70
        )

        self.header.pack(
            fill="x"
        )

        self.header.pack_propagate(
            False
        )

        # -----------------------------------------------------
        # LEFT HEADER
        # -----------------------------------------------------

        self.header_icon = tk.Label(
            self.header,
            text="🩺",
            font=("Segoe UI Emoji", 28),
            bg=BG_HEADER
        )

        self.header_icon.pack(
            side="left",
            padx=(22, 8)
        )

        self.title_frame = tk.Frame(
            self.header,
            bg=BG_HEADER
        )

        self.title_frame.pack(
            side="left"
        )

        self.title_label = tk.Label(
            self.title_frame,
            text=APP_TITLE,
            font=("Segoe UI", 20, "bold"),
            fg=TEXT_DARK,
            bg=BG_HEADER
        )

        self.title_label.pack(
            anchor="w"
        )

        self.subtitle_label = tk.Label(
            self.title_frame,
            text="AI assistant for biomedical instrumentation",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_HEADER
        )

        self.subtitle_label.pack(
            anchor="w"
        )

        # =====================================================
        # LANGUAGE SELECTION
        # =====================================================

        self.language_frame = tk.Frame(
            self.header,
            bg=BG_HEADER
        )

        self.language_frame.pack(
            side="right",
            padx=(8, 10)
        )

        self.language_label = tk.Label(
            self.language_frame,
            text="language",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_HEADER
        )

        self.language_label.pack(
            side="left",
            padx=(0, 8)
        )

        self.language_var = tk.StringVar(
            value="✓ English"
        )

        self.language_menu = tk.OptionMenu(
            self.language_frame,
            self.language_var,
            "✓ English",
            "Français",
            "العربية",
            command=self._change_language
        )

        self.language_menu.config(
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg=TEXT_DARK,
            activebackground="#dcecff",
            activeforeground=TEXT_DARK,
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=5
        )

        self.language_menu["menu"].config(
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg=TEXT_DARK,
            activebackground="#dcecff",
            activeforeground=TEXT_DARK
        )

        self.language_menu.pack(
            side="left"
        )

        # =====================================================
        # MODE SELECTION
        # =====================================================

        self.mode_frame = tk.Frame(
            self.header,
            bg=BG_HEADER
        )

        self.mode_frame.pack(
            side="right",
            padx=(10, 8)
        )

        self.mode_label = tk.Label(
            self.mode_frame,
            text="mode",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_HEADER
        )

        self.mode_label.pack(
            side="left",
            padx=(0, 8)
        )

        self.mode_var = tk.StringVar(
            value="✓ Light"
        )

        self.mode_menu = tk.OptionMenu(
            self.mode_frame,
            self.mode_var,
            "✓ Light",
            "Dark",
            command=self._change_mode
        )

        self.mode_menu.config(
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg=TEXT_DARK,
            activebackground="#dcecff",
            activeforeground=TEXT_DARK,
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=5
        )

        self.mode_menu["menu"].config(
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg=TEXT_DARK,
            activebackground="#dcecff",
            activeforeground=TEXT_DARK
        )

        self.mode_menu.pack(
            side="left"
        )

        # =====================================================
        # HEADER INFORMATION
        # =====================================================

        self.header_info = tk.Label(
            self.header,
            text="AI • Biomedical Engineering • Signal Processing",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_HEADER
        )

        self.header_info.pack(
            side="right",
            padx=15
        )

        # =====================================================
        # MAIN AREA
        # =====================================================

        self.main_container = tk.Frame(
            self.root,
            bg=BG_MAIN
        )

        self.main_container.pack(
            fill="both",
            expand=True
        )

        self.main = self.main_container

        # =====================================================
        # EQUAL WIDTH COLUMNS
        # =====================================================

        self.main.grid_columnconfigure(
            0,
            weight=1,
            uniform="main_panels"
        )

        self.main.grid_columnconfigure(
            1,
            weight=1,
            uniform="main_panels"
        )

        self.main.grid_rowconfigure(
            0,
            weight=1
        )

        # =====================================================
        # LEFT SIDE
        # =====================================================

        self._build_avatar_panel(
            self.main
        )

        # =====================================================
        # RIGHT SIDE
        # =====================================================

        if CUSTOMTKINTER_AVAILABLE:

            self._build_customtkinter_chat(
                self.main
            )

        else:

            messagebox.showerror(
                "CustomTkinter Required",
                "Please install CustomTkinter:\n\n"
                "pip install customtkinter"
            )

            self.root.destroy()

            return

        self.root.after(
            100,
            self._refresh_avatar_panel
        )

    # =========================================================
    # MODE SWITCH
    # =========================================================

    def _change_mode(
        self,
        mode
    ):

        if mode.startswith("✓ "):
            mode = mode[2:]

        self.current_mode = mode

        self.mode_var.set(
            f"✓ {mode}"
        )

        if CUSTOMTKINTER_AVAILABLE:

            if mode == "Dark":
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")

        self._apply_mode_colors(
            mode
        )

        menu = self.mode_menu["menu"]

        menu.configure(
            tearoff=0
        )

        menu.delete(
            0,
            "end"
        )

        if mode == "Light":

            menu.add_command(
                label="✓ Light",
                command=lambda:
                self._change_mode("Light")
            )

            menu.add_command(
                label="Dark",
                command=lambda:
                self._change_mode("Dark")
            )

        else:

            menu.add_command(
                label="Light",
                command=lambda:
                self._change_mode("Light")
            )

            menu.add_command(
                label="✓ Dark",
                command=lambda:
                self._change_mode("Dark")
            )

        menu.configure(
            font=("Segoe UI", 9),
            bg=self.current_mode_bg,
            fg=self.current_mode_fg,
            activebackground=self.current_mode_active,
            activeforeground=self.current_mode_fg
        )

        if hasattr(
            self,
            "language_menu"
        ):

            self.language_menu.configure(
                bg=self.current_mode_bg,
                fg=self.current_mode_fg,
                activebackground=self.current_mode_active,
                activeforeground=self.current_mode_fg
            )

            self.language_menu["menu"].configure(
                bg=self.current_mode_bg,
                fg=self.current_mode_fg,
                activebackground=self.current_mode_active,
                activeforeground=self.current_mode_fg
            )

        self.root.after(
            50,
            self._refresh_avatar_panel
        )

    # =========================================================
    # APPLY MODE COLORS
    # =========================================================

    def _apply_mode_colors(
        self,
        mode
    ):

        if mode == "Dark":

            self.current_bg_main = DARK_BG_MAIN
            self.current_header = DARK_BG_HEADER
            self.current_avatar = DARK_BG_MAIN

            self.current_chat = DARK_BG_CHAT
            self.current_chat_area = DARK_BG_CHAT_AREA
            self.current_input = DARK_BG_INPUT

            self.current_text_dark = DARK_TEXT_DARK
            self.current_text_normal = DARK_TEXT_NORMAL
            self.current_text_muted = DARK_TEXT_MUTED

            self.current_border = DARK_BORDER

            self.current_user_bubble = DARK_USER_BUBBLE
            self.current_user_border = DARK_USER_BUBBLE_BORDER

            self.current_expert_bubble = DARK_EXPERT_BUBBLE
            self.current_expert_border = DARK_EXPERT_BUBBLE_BORDER

            self.current_system_bubble = DARK_SYSTEM_BUBBLE

            self.current_mode_bg = "#263846"
            self.current_mode_fg = "#e7f2fa"
            self.current_mode_active = "#3a5264"

        else:

            self.current_bg_main = BG_MAIN
            self.current_header = BG_HEADER
            self.current_avatar = BG_MAIN

            self.current_chat = BG_CHAT
            self.current_chat_area = BG_CHAT_AREA
            self.current_input = BG_INPUT

            self.current_text_dark = TEXT_DARK
            self.current_text_normal = TEXT_NORMAL
            self.current_text_muted = TEXT_MUTED

            self.current_border = "#d6e4f2"

            self.current_user_bubble = USER_BUBBLE
            self.current_user_border = USER_BUBBLE_BORDER

            self.current_expert_bubble = EXPERT_BUBBLE
            self.current_expert_border = EXPERT_BUBBLE_BORDER

            self.current_system_bubble = SYSTEM_BUBBLE

            self.current_mode_bg = "#ffffff"
            self.current_mode_fg = TEXT_DARK
            self.current_mode_active = "#dcecff"

        self.root.configure(
            bg=self.current_bg_main
        )

        self.main_container.configure(
            bg=self.current_bg_main
        )

        self.main.configure(
            bg=self.current_bg_main
        )

        self.header.configure(
            bg=self.current_header
        )

        self.header_icon.configure(
            bg=self.current_header
        )

        self.title_frame.configure(
            bg=self.current_header
        )

        self.title_label.configure(
            bg=self.current_header,
            fg=self.current_text_dark
        )

        self.subtitle_label.configure(
            bg=self.current_header,
            fg=self.current_text_muted
        )

        self.header_info.configure(
            bg=self.current_header,
            fg=self.current_text_muted
        )

        self.mode_frame.configure(
            bg=self.current_header
        )

        self.mode_label.configure(
            bg=self.current_header,
            fg=self.current_text_muted
        )

        self.language_frame.configure(
            bg=self.current_header
        )

        self.language_label.configure(
            bg=self.current_header,
            fg=self.current_text_muted
        )

        self.mode_menu.configure(
            bg=self.current_mode_bg,
            fg=self.current_mode_fg,
            activebackground=self.current_mode_active,
            activeforeground=self.current_mode_fg
        )

        self.mode_menu["menu"].configure(
            bg=self.current_mode_bg,
            fg=self.current_mode_fg,
            activebackground=self.current_mode_active,
            activeforeground=self.current_mode_fg
        )

        if hasattr(
            self,
            "language_menu"
        ):

            self.language_menu.configure(
                bg=self.current_mode_bg,
                fg=self.current_mode_fg,
                activebackground=self.current_mode_active,
                activeforeground=self.current_mode_fg
            )

            self.language_menu["menu"].configure(
                bg=self.current_mode_bg,
                fg=self.current_mode_fg,
                activebackground=self.current_mode_active,
                activeforeground=self.current_mode_fg
            )

        if hasattr(
            self,
            "avatar_panel"
        ):

            self.avatar_panel.configure(
                bg=self.current_bg_main
            )

            self._redraw_speech_bubble()

        if hasattr(
            self,
            "chat_panel"
        ):

            self.chat_panel.configure(
                fg_color=self.current_chat,
                border_color=self.current_border
            )

        if hasattr(
            self,
            "chat_scroll"
        ):

            self.chat_scroll.configure(
                fg_color=self.current_chat_area
            )

        if hasattr(
            self,
            "input_box"
        ):

            self.input_box.configure(
                fg_color=self.current_input,
                text_color=self.current_text_normal,
                border_color=self.current_border
            )

        if hasattr(
            self,
            "status"
        ):

            self.status.configure(
                text_color=self.current_text_muted
            )

        if hasattr(
            self,
            "voice_test_btn"
        ):

            if mode == "Dark":

                self.voice_test_btn.configure(
                    fg_color="#263846",
                    hover_color="#385264",
                    text_color="#e7f2fa"
                )

            else:

                self.voice_test_btn.configure(
                    fg_color="#e9f3ff",
                    hover_color="#d5e9ff",
                    text_color=TEXT_DARK
                )

        if hasattr(
            self,
            "new_chat_btn"
        ):

            if mode == "Dark":

                self.new_chat_btn.configure(
                    fg_color="#263846",
                    hover_color="#385264",
                    text_color="#e7f2fa"
                )

            else:

                self.new_chat_btn.configure(
                    fg_color="#e9f3ff",
                    hover_color="#d5e9ff",
                    text_color=TEXT_DARK
                )

        if hasattr(
            self,
            "send_btn"
        ):

            self.send_btn.configure(
                fg_color=PRIMARY,
                hover_color=PRIMARY_DARK
            )

    # =========================================================
    # BUILD LEFT AVATAR PANEL
    # =========================================================

    def _build_avatar_panel(
        self,
        main
    ):

        self.avatar_panel = tk.Canvas(
            main,
            bg=self.current_bg_main,
            bd=0,
            highlightthickness=0,
            relief="flat"
        )

        self.avatar_panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 12),
            pady=0
        )

        self.avatar_panel.bind(
            "<Configure>",
            self._on_avatar_panel_resize
        )

        image_path = (
            Path(__file__).parent
            / "assets"
            / "biomedical_expert3.png"
        )

        if (
            Image is not None
            and image_path.exists()
        ):

            try:

                img = Image.open(
                    image_path
                ).convert("RGBA")

                img.thumbnail(
                    (330, 450),
                    Image.Resampling.LANCZOS
                )

                self.expert_photo = ImageTk.PhotoImage(
                    img,
                    master=self.root
                )

            except Exception as exc:

                print(
                    "Avatar image error:",
                    repr(exc)
                )

                self.expert_photo = None

        self._draw_speech_bubble()

        self.bubble_text = self.avatar_panel.create_text(
            180,
            70,
            text="",
            width=285,
            justify="center",
            anchor="center",
            font=("Segoe UI", 11),
            fill=TEXT_DARK,
            tags="bubble_text"
        )

        self.waiting_labels = []

        canvas_width = 360
        dot_y = 175
        start_x = canvas_width / 2 - 28

        for index in range(3):

            dot = self.avatar_panel.create_text(
                start_x + index * 28,
                dot_y,
                text="●",
                font=("Segoe UI", 13, "bold"),
                fill="#b7c9dc",
                anchor="center",
                tags="thinking_dot"
            )

            self.waiting_labels.append(
                dot
            )

        self._set_waiting_visible(
            False
        )

        if self.expert_photo is not None:

            self.expert_image_item = (
                self.avatar_panel.create_image(
                    180,
                    600,
                    image=self.expert_photo,
                    anchor="s",
                    tags="expert_avatar"
                )
            )

        else:

            self._create_fallback_avatar()

        self.root.after(
            100,
            self._refresh_avatar_panel
        )

    # =========================================================
    # LEFT PANEL RESIZE
    # =========================================================

    def _on_avatar_panel_resize(
        self,
        event
    ):

        self.root.after_idle(
            self._refresh_avatar_panel
        )

    # =========================================================
    # REFRESH AVATAR PANEL
    # =========================================================

    def _refresh_avatar_panel(self):

        if not hasattr(
            self,
            "avatar_panel"
        ):
            return

        try:

            self.avatar_panel.update_idletasks()

            width = max(
                self.avatar_panel.winfo_width(),
                1
            )

            height = max(
                self.avatar_panel.winfo_height(),
                1
            )

            self._draw_avatar_background(
                width,
                height
            )

            self._position_avatar(
                width,
                height
            )

            self._draw_speech_bubble()

            if self.bubble_text is not None:

                bubble_center_x = width / 2

                bubble_center_y = (
                    self._bubble_y1
                    + (
                        self._bubble_y2
                        - self._bubble_y1
                    ) / 2
                    - 2
                )

                self.avatar_panel.coords(
                    self.bubble_text,
                    bubble_center_x,
                    bubble_center_y
                )

                self.avatar_panel.itemconfig(
                    self.bubble_text,
                    width=max(
                        200,
                        self._bubble_width - 55
                    ),
                    justify=(
                        "right"
                        if self._is_rtl()
                        else "center"
                    )
                )

                self.avatar_panel.tag_raise(
                    self.bubble_text
                )

            dot_y = (
                self._bubble_y2
                + 32
            )

            start_x = (
                width / 2
                - 28
            )

            for index, dot in enumerate(
                self.waiting_labels
            ):

                self.avatar_panel.coords(
                    dot,
                    start_x + index * 28,
                    dot_y
                )

            if self.expert_image_item is not None:

                self.avatar_panel.tag_raise(
                    self.expert_image_item
                )

            for dot in self.waiting_labels:

                self.avatar_panel.tag_raise(
                    dot
                )

            if self.bubble_text is not None:

                self.avatar_panel.tag_raise(
                    self.bubble_text
                )

        except Exception as exc:

            print(
                "Avatar panel refresh error:",
                repr(exc)
            )

    # =========================================================
    # DRAW LEFT-PANEL BACKGROUND
    # =========================================================

    def _draw_avatar_background(
        self,
        width,
        height
    ):

        if Image is None:

            self.avatar_panel.configure(
                bg=self.current_bg_main
            )

            return

        if self.current_mode == "Light":
            image_path = self.light_background_path
        else:
            image_path = self.dark_background_path

        if not image_path.exists():

            self.avatar_panel.configure(
                bg=self.current_bg_main
            )

            return

        try:

            image = Image.open(
                image_path
            ).convert("RGB")

            source_width, source_height = (
                image.size
            )

            scale = max(
                width / source_width,
                height / source_height
            )

            new_width = max(
                1,
                int(source_width * scale)
            )

            new_height = max(
                1,
                int(source_height * scale)
            )

            image = image.resize(
                (
                    new_width,
                    new_height
                ),
                Image.Resampling.LANCZOS
            )

            left = max(
                0,
                (new_width - width) // 2
            )

            top = max(
                0,
                (new_height - height) // 2
            )

            right = left + width
            bottom = top + height

            image = image.crop(
                (
                    left,
                    top,
                    right,
                    bottom
                )
            )

            self.avatar_background_image = (
                ImageTk.PhotoImage(
                    image,
                    master=self.root
                )
            )

            if self.avatar_background_item is not None:

                self.avatar_panel.delete(
                    self.avatar_background_item
                )

            self.avatar_background_item = (
                self.avatar_panel.create_image(
                    0,
                    0,
                    image=self.avatar_background_image,
                    anchor="nw",
                    tags="panel_background"
                )
            )

            self.avatar_panel.tag_lower(
                self.avatar_background_item
            )

        except Exception as exc:

            print(
                "Avatar background image error:",
                repr(exc)
            )

    # =========================================================
    # POSITION AVATAR
    # =========================================================

    def _position_avatar(
        self,
        width,
        height
    ):

        if self.expert_image_item is not None:

            center_x = width / 2
            avatar_y = height - 8

            self.avatar_panel.coords(
                self.expert_image_item,
                center_x,
                avatar_y
            )

            self.avatar_panel.tag_raise(
                self.expert_image_item
            )

        elif self.fallback_avatar_item is not None:

            self.avatar_panel.coords(
                self.fallback_avatar_item,
                width / 2,
                height - 35
            )

            self.avatar_panel.tag_raise(
                self.fallback_avatar_item
            )

    # =========================================================
    # FALLBACK AVATAR
    # =========================================================

    def _create_fallback_avatar(self):

        self.fallback_avatar_item = (
            self.avatar_panel.create_text(
                180,
                600,
                text="👩‍🔬",
                font=("Segoe UI Emoji", 105),
                fill=(
                    DARK_TEXT_DARK
                    if self.current_mode == "Dark"
                    else TEXT_DARK
                ),
                anchor="s",
                tags="fallback_avatar"
            )
        )

    # =========================================================
    # SPEECH BUBBLE
    # =========================================================

    def _draw_speech_bubble(self):

        if not hasattr(
            self,
            "avatar_panel"
        ):
            return

        canvas = self.avatar_panel

        width = max(
            canvas.winfo_width(),
            360
        )

        height = max(
            canvas.winfo_height(),
            500
        )

        bubble_width = min(
            350,
            width - 36
        )

        bubble_width = max(
            280,
            bubble_width
        )

        x1 = (
            width - bubble_width
        ) / 2

        x2 = (
            width + bubble_width
        ) / 2

        bubble_height = 125

        avatar_area_height = 450

        y2 = (
            height
            - avatar_area_height
            - 25
        )

        y2 = max(
            180,
            y2
        )

        y1 = y2 - bubble_height
        y1 = max(
            18,
            y1
        )

        y2 = y1 + bubble_height

        radius = 40

        self._bubble_width = bubble_width
        self._bubble_y1 = y1
        self._bubble_y2 = y2

        canvas.delete(
            "speech_bubble"
        )

        if self.current_mode == "Dark":

            fill = "#22333f"
            outline = "#3e5869"

        else:

            fill = "#ffffff"
            outline = "#c5d9ee"

        canvas.create_rectangle(
            x1 + radius,
            y1,
            x2 - radius,
            y2,
            fill=fill,
            outline=fill,
            tags="speech_bubble"
        )

        canvas.create_rectangle(
            x1,
            y1 + radius,
            x2,
            y2 - radius,
            fill=fill,
            outline=fill,
            tags="speech_bubble"
        )

        canvas.create_arc(
            x1,
            y1,
            x1 + radius * 2,
            y1 + radius * 2,
            start=90,
            extent=90,
            fill=fill,
            outline=fill,
            tags="speech_bubble"
        )

        canvas.create_arc(
            x2 - radius * 2,
            y1,
            x2,
            y1 + radius * 2,
            start=0,
            extent=90,
            fill=fill,
            outline=fill,
            tags="speech_bubble"
        )

        canvas.create_arc(
            x1,
            y2 - radius * 2,
            x1 + radius * 2,
            y2,
            start=180,
            extent=90,
            fill=fill,
            outline=fill,
            tags="speech_bubble"
        )

        canvas.create_arc(
            x2 - radius * 2,
            y2 - radius * 2,
            x2,
            y2,
            start=270,
            extent=90,
            fill=fill,
            outline=fill,
            tags="speech_bubble"
        )

        canvas.create_line(
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            fill=outline,
            width=2,
            tags="speech_bubble"
        )

        canvas.create_line(
            x1 + radius,
            y2,
            x2 - radius,
            y2,
            fill=outline,
            width=2,
            tags="speech_bubble"
        )

        canvas.create_line(
            x1,
            y1 + radius,
            x1,
            y2 - radius,
            fill=outline,
            width=2,
            tags="speech_bubble"
        )

        canvas.create_line(
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            fill=outline,
            width=2,
            tags="speech_bubble"
        )

        tail_center = width / 2

        tail_points = [
            tail_center - 22,
            y2 - 1,
            tail_center,
            y2 + 30,
            tail_center + 22,
            y2 - 1
        ]

        canvas.create_polygon(
            tail_points,
            fill=fill,
            outline=fill,
            tags="speech_bubble"
        )

        canvas.create_line(
            tail_center - 22,
            y2,
            tail_center,
            y2 + 30,
            tail_center + 22,
            y2,
            fill=outline,
            width=2,
            smooth=True,
            splinesteps=20,
            tags="speech_bubble"
        )

        canvas.tag_raise(
            "speech_bubble"
        )

    # =========================================================
    # REDRAW SPEECH BUBBLE
    # =========================================================

    def _redraw_speech_bubble(self):

        if not hasattr(
            self,
            "avatar_panel"
        ):
            return

        self._draw_speech_bubble()

        if self.bubble_text is not None:

            width = max(
                self.avatar_panel.winfo_width(),
                360
            )

            bubble_center_x = width / 2

            bubble_center_y = (
                self._bubble_y1
                + (
                    self._bubble_y2
                    - self._bubble_y1
                ) / 2
            )

            self.avatar_panel.coords(
                self.bubble_text,
                bubble_center_x,
                bubble_center_y
            )

            self.avatar_panel.itemconfig(
                self.bubble_text,
                fill=(
                    DARK_TEXT_DARK
                    if self.current_mode == "Dark"
                    else TEXT_DARK
                ),
                width=max(
                    200,
                    self._bubble_width - 55
                ),
                justify=(
                    "right"
                    if self._is_rtl()
                    else "center"
                )
            )

            self.avatar_panel.tag_raise(
                self.bubble_text
            )

    # =========================================================
    # WAITING DOT VISIBILITY
    # =========================================================

    def _set_waiting_visible(
        self,
        visible
    ):

        state = (
            "normal"
            if visible
            else "hidden"
        )

        if hasattr(
            self,
            "avatar_panel"
        ):

            for dot in self.waiting_labels:

                self.avatar_panel.itemconfigure(
                    dot,
                    state=state
                )

    # =========================================================
    # WELCOME
    # =========================================================

    def _show_welcome(self):

        self._animate_welcome()

        welcome_text = (
            f"{self._language_text('hello')} "
            f"{self._language_text('expert')} "
            f"{self._language_text('help')}"
        )

        self._speak_async(
            welcome_text
        )

        if self.agent is None:

            self._append_system(
                "Gemini is not configured. "
                "Add GOOGLE_API_KEY or GEMINI_API_KEY "
                "to your .env file."
            )

    # =========================================================
    # WELCOME ANIMATION
    # =========================================================

    def _animate_welcome(self):

        if self.bubble_animation_running:
            return

        self.bubble_animation_running = True

        self._welcome_lines = [
            self._language_text("hello"),
            self._language_text("expert"),
            self._language_text("help")
        ]

        self._welcome_line_index = 0
        self._welcome_current_text = ""

        self.avatar_panel.itemconfig(
            self.bubble_text,
            text=""
        )

        self._type_welcome_line()

    def _type_welcome_line(self):

        if (
            self._welcome_line_index
            >= len(self._welcome_lines)
        ):

            self.bubble_animation_running = False
            return

        line = self._welcome_lines[
            self._welcome_line_index
        ]

        if len(
            self._welcome_current_text
        ) < len(line):

            self._welcome_current_text += line[
                len(self._welcome_current_text)
            ]

            display_text = ""

            for i in range(
                self._welcome_line_index
            ):

                display_text += (
                    self._welcome_lines[i]
                    + "\n\n"
                )

            display_text += (
                self._welcome_current_text
            )

            self.avatar_panel.itemconfig(
                self.bubble_text,
                text=display_text,
                justify=(
                    "right"
                    if self._is_rtl()
                    else "center"
                )
            )

            self.root.after(
                35,
                self._type_welcome_line
            )

        else:

            self._welcome_line_index += 1
            self._welcome_current_text = ""

            self.root.after(
                650,
                self._type_welcome_line
            )

    # =========================================================
    # VOICE
    # =========================================================

    def _speak_async(
        self,
        text
    ):

        if not text:
            return

        threading.Thread(
            target=self._speak,
            args=(text,),
            daemon=True
        ).start()

    # =========================================================
    # ACTUAL SPEECH
    # =========================================================

    def _speak(
        self,
        text
    ):

        with self.voice_lock:

            print()
            print("=" * 60)
            print("VOICE REQUEST:")
            print("Language:", self.current_language)
            print(text)
            print("=" * 60)

            speech_text = re.sub(
                r'[\U0001F300-\U0001FAFF'
                r'\U00002700-\U000027BF'
                r'\U00002600-\U000026FF'
                r'\U00002300-\U000023FF]+',
                '',
                text
            ).strip()

            if PYTTSX3_AVAILABLE:

                engine = None

                try:

                    print(
                        "Trying pyttsx3 / SAPI5..."
                    )

                    engine = pyttsx3.init(
                        driverName="sapi5"
                    )

                    engine.setProperty(
                        "rate",
                        165
                    )

                    engine.setProperty(
                        "volume",
                        1.0
                    )

                    voices = engine.getProperty(
                        "voices"
                    )

                    selected_voice = None

                    if voices:

                        language_voice_keywords = {

                            "English": [
                                "zira",
                                "david",
                                "aria",
                                "jenny",
                                "english",
                                "en-us"
                            ],

                            "Français": [
                                "france",
                                "french",
                                "fr-fr",
                                "hortense",
                                "denise"
                            ],

                            "العربية": [
                                "arabic",
                                "ar-sa",
                                "ar-eg",
                                "ar"
                            ]
                        }

                        keywords = (
                            language_voice_keywords.get(
                                self.current_language,
                                language_voice_keywords[
                                    "English"
                                ]
                            )
                        )

                        print(
                            "Installed Windows voices:"
                        )

                        for voice in voices:

                            voice_name = str(
                                getattr(
                                    voice,
                                    "name",
                                    ""
                                )
                            )

                            voice_id = str(
                                getattr(
                                    voice,
                                    "id",
                                    ""
                                )
                            )

                            print(
                                "   ",
                                voice_name,
                                "|",
                                voice_id
                            )

                            name_lower = (
                                voice_name.lower()
                            )

                            id_lower = (
                                voice_id.lower()
                            )

                            if any(
                                keyword in name_lower
                                or keyword in id_lower
                                for keyword in keywords
                            ):

                                selected_voice = voice
                                break

                    if selected_voice is not None:

                        engine.setProperty(
                            "voice",
                            selected_voice.id
                        )

                        print(
                            "Selected voice:",
                            selected_voice.name
                        )

                    elif voices:

                        engine.setProperty(
                            "voice",
                            voices[0].id
                        )

                        print(
                            "Using first available voice:",
                            voices[0].name
                        )

                    engine.say(
                        speech_text
                    )

                    engine.runAndWait()

                    print(
                        "pyttsx3 / SAPI5 SUCCESS"
                    )

                    self.voice_available = True

                    try:
                        engine.stop()
                    except Exception:
                        pass

                    return

                except Exception as exc:

                    print(
                        "pyttsx3 / SAPI5 FAILED:"
                    )

                    print(
                        repr(exc)
                    )

                finally:

                    if engine is not None:

                        try:
                            engine.stop()
                        except Exception:
                            pass

                        try:
                            del engine
                        except Exception:
                            pass

            if os.name == "nt":

                try:

                    print(
                        "Trying Windows System.Speech..."
                    )

                    safe_text = speech_text.replace(
                        "'",
                        "''"
                    )

                    powershell_command = (
                        "Add-Type "
                        "-AssemblyName System.Speech; "
                        "$voice = New-Object "
                        "System.Speech.Synthesis.SpeechSynthesizer; "
                        "$voice.Rate = 0; "
                        "$voice.Volume = 100; "
                        f"$voice.Speak('{safe_text}'); "
                        "$voice.Dispose();"
                    )

                    result = subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-ExecutionPolicy",
                            "Bypass",
                            "-Command",
                            powershell_command
                        ],
                        creationflags=(
                            subprocess.CREATE_NO_WINDOW
                            if hasattr(
                                subprocess,
                                "CREATE_NO_WINDOW"
                            )
                            else 0
                        ),
                        capture_output=True,
                        text=True,
                        check=False
                    )

                    if result.returncode == 0:

                        print(
                            "Windows System.Speech SUCCESS"
                        )

                        self.voice_available = True

                    else:

                        print(
                            "Windows System.Speech FAILED"
                        )

                        print(
                            "STDOUT:",
                            result.stdout
                        )

                        print(
                            "STDERR:",
                            result.stderr
                        )

                except Exception as exc:

                    print(
                        "Windows voice failed:",
                        repr(exc)
                    )

            else:

                print(
                    "Windows voice is unavailable."
                )

    # =========================================================
    # TEST VOICE
    # =========================================================

    def _test_voice(self):

        test_messages = {

            "English":
                "Hello. This is the Biomedical Instrumentation Assistant. "
                "The Windows voice system is working.",

            "Français":
                "Bonjour. Je suis l'assistant en instrumentation biomédicale. "
                "Le système vocal Windows fonctionne.",

            "العربية":
                "مرحباً. أنا مساعد الأجهزة الطبية الحيوية. "
                "نظام الصوت في Windows يعمل."
        }

        test_text = test_messages.get(
            self.current_language,
            test_messages["English"]
        )

        self.avatar_panel.itemconfig(
            self.bubble_text,
            text=self._language_text("voice_test"),
            justify=(
                "right"
                if self._is_rtl()
                else "center"
            )
        )

        self.status.configure(
            text=self._language_text("testing_voice")
        )

        self._speak_async(
            test_text
        )

        self.root.after(
            5000,
            lambda: self.status.configure(
                text=self._language_text("ready")
            )
        )

    # =========================================================
    # SYSTEM MESSAGE
    # =========================================================

    def _append_system(
        self,
        text
    ):

        self._create_message_bubble(
            text=text,
            sender="system"
        )

    # =========================================================
    # USER MESSAGE
    # =========================================================

    def _append_user(
        self,
        text
    ):

        self._create_message_bubble(
            text=text,
            sender="user"
        )

    # =========================================================
    # EXPERT MESSAGE
    # =========================================================

    def _append_expert(
        self,
        text
    ):

        self._create_message_bubble(
            text=text,
            sender="expert"
        )

    # =========================================================
    # CREATE MESSAGE BUBBLE
    # =========================================================

    def _create_message_bubble(
        self,
        text,
        sender="expert"
    ):

        if sender == "user":

            bubble_color = getattr(
                self,
                "current_user_bubble",
                USER_BUBBLE
            )

            name = self._language_text(
                "user"
            )

            name_color = (
                "#78b8ed"
                if self.current_mode == "Dark"
                else "#0e5ba8"
            )

            min_width, max_width, side_pad = (
                80,
                430,
                75
            )

        elif sender == "expert":

            bubble_color = getattr(
                self,
                "current_expert_bubble",
                EXPERT_BUBBLE
            )

            name = self._language_text(
                "expert_name"
            )

            name_color = PRIMARY

            min_width, max_width, side_pad = (
                280,
                560,
                55
            )

        else:

            bubble_color = getattr(
                self,
                "current_system_bubble",
                SYSTEM_BUBBLE
            )

            name = self._language_text(
                "system"
            )

            name_color = (
                DARK_TEXT_MUTED
                if self.current_mode == "Dark"
                else TEXT_MUTED
            )

            min_width, max_width, side_pad = (
                100,
                500,
                100
            )

        clean_text = (
            self._clean_markdown_for_bubble(
                text
            )
            or " "
        )

        row = ctk.CTkFrame(
            self.chat_scroll,
            fg_color="transparent",
            corner_radius=0
        )

        row.pack(
            fill="x",
            padx=8,
            pady=(4, 5)
        )

        self.chat_scroll.update_idletasks()

        available_width = max(
            1,
            self.chat_scroll.winfo_width()
        )

        try:

            text_font = tkfont.Font(
                family="Segoe UI",
                size=12
            )

            name_font = tkfont.Font(
                family="Segoe UI",
                size=10,
                weight="bold"
            )

            lines = clean_text.split(
                "\n"
            )

            text_width = max(
                (
                    text_font.measure(line)
                    for line in lines
                ),
                default=0
            )

            name_width = name_font.measure(
                name
            )

        except Exception:

            text_width = max(
                (
                    len(line) * 8
                    for line in clean_text.split(
                        "\n"
                    )
                ),
                default=0
            )

            name_width = len(name) * 7

        if sender == "expert":

            bubble_width = min(
                560,
                max(
                    280,
                    available_width - 55
                )
            )

        else:

            content_width = max(
                text_width + 40,
                name_width + 30,
                min_width
            )

            max_allowed = min(
                max_width,
                max(
                    min_width,
                    available_width
                    - side_pad
                    - 20
                )
            )

            bubble_width = min(
                content_width,
                max_allowed
            )

        bubble = ctk.CTkFrame(
            row,
            fg_color=bubble_color,
            border_color=bubble_color,
            border_width=0,
            corner_radius=18,
            width=int(bubble_width),
            height=50
        )

        bubble.pack_propagate(
            False
        )

        if sender == "user":

            bubble.pack(
                side="right",
                padx=(side_pad, 4),
                anchor="e"
            )

        elif sender == "expert":

            bubble.pack(
                side="left",
                padx=(4, side_pad),
                anchor="w"
            )

        else:

            bubble.pack(
                side="top",
                padx=side_pad,
                anchor="center"
            )

        sender_label = ctk.CTkLabel(
            bubble,
            text=name,
            font=("Segoe UI", 10, "bold"),
            text_color=name_color,
            anchor=(
                "e"
                if self._is_rtl()
                else "w"
            )
        )

        sender_label.pack(
            fill="x",
            padx=14,
            pady=(5, 0)
        )

        message_box = tk.Text(
            bubble,
            wrap="word",
            font=("Segoe UI", 12),
            bg=bubble_color,
            fg=(
                self.current_text_normal
                if sender != "system"
                else self.current_text_muted
            ),
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=12,
            pady=0,
            cursor="arrow",
            insertwidth=0,
            height=1,
            width=1
        )

        message_box.pack(
            fill="x",
            expand=False,
            padx=1,
            pady=(0, 4)
        )

        message_box.insert(
            "1.0",
            clean_text
        )

        if self._is_rtl():

            message_box.tag_configure(
                "rtl",
                justify="right"
            )

            message_box.tag_add(
                "rtl",
                "1.0",
                "end"
            )

        self.root.update_idletasks()

        message_box.update_idletasks()

        try:

            display_lines = int(
                message_box.count(
                    "1.0",
                    "end-1c",
                    "displaylines"
                )[0]
            )

        except Exception:

            display_lines = max(
                1,
                clean_text.count("\n") + 1
            )

        display_lines = max(
            1,
            display_lines
        )

        message_box.configure(
            height=display_lines
        )

        self.root.update_idletasks()

        message_box.update_idletasks()

        sender_label.update_idletasks()

        label_height = (
            sender_label.winfo_reqheight()
        )

        message_height = (
            message_box.winfo_reqheight()
        )

        bubble_height = (
            label_height
            + message_height
            + 5
        )

        bubble.configure(
            height=max(
                45,
                int(bubble_height)
            )
        )

        message_box.configure(
            state="disabled"
        )

        self._configure_bubble_markdown(
            message_box
        )

        self.root.after_idle(
            lambda:
            self._finalize_bubble_size(
                bubble,
                message_box,
                sender_label
            )
        )

        self.root.after(
            60,
            self._scroll_chat_bottom
        )

    # =========================================================
    # FINALIZE BUBBLE SIZE
    # =========================================================

    def _finalize_bubble_size(
        self,
        bubble,
        message_box,
        sender_label
    ):

        try:

            self.root.update_idletasks()

            message_box.update_idletasks()

            sender_label.update_idletasks()

            bubble.configure(
                height=max(
                    45,
                    int(
                        sender_label.winfo_reqheight()
                        + message_box.winfo_reqheight()
                        + 5
                    )
                )
            )

        except Exception as exc:

            print(
                "Bubble resize error:",
                repr(exc)
            )

    # =========================================================
    # CLEAN MARKDOWN
    # =========================================================

    def _clean_markdown_for_bubble(
        self,
        text
    ):

        text = text.replace(
            "\r\n",
            "\n"
        )

        text = re.sub(
            r"```[a-zA-Z0-9_+-]*",
            "",
            text
        )

        text = text.replace(
            "```",
            ""
        )

        text = re.sub(
            r"^\s*#{1,6}\s+",
            "",
            text,
            flags=re.MULTILINE
        )

        text = re.sub(
            r"\*\*(.*?)\*\*",
            r"\1",
            text
        )

        text = re.sub(
            r"(?<!\*)\*([^*]+)\*(?!\*)",
            r"\1",
            text
        )

        text = re.sub(
            r"^\s*[-*•]\s+",
            "• ",
            text,
            flags=re.MULTILINE
        )

        # -----------------------------------------------------
        # PREVENT EXCESSIVE BLANK SPACE
        # -----------------------------------------------------

        text = re.sub(
            r"\n[ \t]*\n(?:[ \t]*\n)+",
            "\n\n",
            text
        )

        text = re.sub(
            r"[ \t]+\n",
            "\n",
            text
        )

        return text.strip()

    # =========================================================
    # BUBBLE MARKDOWN FORMATTING
    # =========================================================

    def _configure_bubble_markdown(
        self,
        widget
    ):

        text_dark = (
            DARK_TEXT_DARK
            if self.current_mode == "Dark"
            else TEXT_DARK
        )

        text_normal = (
            DARK_TEXT_NORMAL
            if self.current_mode == "Dark"
            else TEXT_NORMAL
        )

        code_bg = (
            "#263846"
            if self.current_mode == "Dark"
            else "#edf3f9"
        )

        code_fg = (
            "#d8e9f7"
            if self.current_mode == "Dark"
            else "#193b5e"
        )

        widget.tag_configure(
            "heading",
            font=("Segoe UI", 12, "bold"),
            foreground=text_dark
        )

        widget.tag_configure(
            "bold",
            font=("Segoe UI", 11, "bold"),
            foreground=text_dark
        )

        widget.tag_configure(
            "code",
            font=("Consolas", 10),
            background=code_bg,
            foreground=code_fg
        )

        widget.tag_configure(
            "bullet",
            foreground=text_normal
        )

    # =========================================================
    # SCROLL CHAT
    # =========================================================

    def _scroll_chat_bottom(self):

        try:

            self.chat_scroll._parent_canvas.yview_moveto(
                1.0
            )

        except Exception:

            try:

                self.chat_scroll.yview_moveto(
                    1.0
                )

            except Exception:

                pass

    # =========================================================
    # WORKFLOW YES / NO
    # =========================================================

    def _is_yes(
        self,
        text
    ):

        normalized = (
            text
            .strip()
            .lower()
            .rstrip(".!?")
        )

        yes_words = {
            "yes",
            "y",
            "oui",
            "o",
            "نعم",
            "نعم نعم",
            "yes please",
            "oui merci",
            "yes please search",
            "oui recherchez"
        }

        return normalized in yes_words

    def _is_no(
        self,
        text
    ):

        normalized = (
            text
            .strip()
            .lower()
            .rstrip(".!?")
        )

        no_words = {
            "no",
            "n",
            "non",
            "لا",
            "no thanks",
            "non merci"
        }

        return normalized in no_words

    # =========================================================
    # COMPONENT PARSER
    # =========================================================

    def _parse_lab_components(
        self,
        text
    ):

        parts = re.split(
            r",|\n|;",
            text
        )

        components = []

        for item in parts:

            item = item.strip()

            if item and item not in components:

                components.append(
                    item
                )

        return components

    # =========================================================
    # EXTRACT JSON OBJECT
    # =========================================================

    def _extract_json_object(
        self,
        text
    ):

        if not text:
            return None

        cleaned = text.strip()

        # -----------------------------------------------------
        # Remove Markdown code fences
        # -----------------------------------------------------

        cleaned = re.sub(
            r"^```(?:json)?",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"```$",
            "",
            cleaned
        )

        cleaned = cleaned.strip()

        try:

            return json.loads(
                cleaned
            )

        except Exception:
            pass

        # -----------------------------------------------------
        # Search for first JSON object
        # -----------------------------------------------------

        start = cleaned.find(
            "{"
        )

        end = cleaned.rfind(
            "}"
        )

        if (
            start >= 0
            and end > start
        ):

            candidate = cleaned[
                start:end + 1
            ]

            try:

                return json.loads(
                    candidate
                )

            except Exception:
                return None

        return None

    # =========================================================
    # PROJECT SUBAGENT
    # =========================================================

    def _run_project_agent(
        self,
        question,
        request_language
    ):

        if self.project_agent is None:

            raise RuntimeError(
                "Project subagent is not available."
            )

        context = LanguageContext(
            language=request_language
        )

        prompt = f"""
{PROJECT_AGENT_PROMPT}

CURRENT WORKFLOW STATE:
{self.workflow_state}

LABORATORY COMPONENTS:
{self.lab_components}

SELECTED PROJECT:
{self.selected_project}

REQUIRED COMPONENTS:
{self.required_components}

AVAILABLE COMPONENTS:
{self.available_components}

MISSING COMPONENTS:
{self.missing_components}

USER MESSAGE:
{question}

Respond in the selected user language.
"""

        response = self.project_agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=prompt
                    )
                ]
            },
            context=context
        )

        content = response[
            "messages"
        ][-1].content

        return self._extract_text(
            content
        )

    # =========================================================
    # PROJECT COMPONENT ANALYSIS
    # =========================================================

    def _analyze_selected_project(
        self,
        request_language
    ):

        if self.project_agent is None:

            raise RuntimeError(
                "Project subagent is not available."
            )

        context = LanguageContext(
            language=request_language
        )

        prompt = f"""
{PROJECT_AGENT_PROMPT}

The user selected this project:

{self.selected_project}

The laboratory components reported by the user are:

{self.lab_components}

Analyze the selected project and return ONLY valid JSON.

Use exactly this structure:

{{
    "project_title": "string",
    "required_components": [
        "component 1",
        "component 2"
    ],
    "available_components": [
        "component 1"
    ],
    "missing_components": [
        "component 2"
    ],
    "verification_message": "Ask the user to physically verify the required components in the laboratory."
}}

Do not use Markdown code fences.

Do not search for suppliers.

Answer the JSON values in the selected user language where appropriate.
"""

        response = self.project_agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=prompt
                    )
                ]
            },
            context=context
        )

        content = response[
            "messages"
        ][-1].content

        text = self._extract_text(
            content
        )

        data = self._extract_json_object(
            text
        )

        if not isinstance(
            data,
            dict
        ):

            raise RuntimeError(
                "The project subagent did not return valid "
                "structured component information."
            )

        self.selected_project = data.get(
            "project_title",
            self.selected_project
        )

        self.required_components = (
            data.get(
                "required_components",
                []
            )
            or []
        )

        self.available_components = (
            data.get(
                "available_components",
                []
            )
            or []
        )

        self.missing_components = (
            data.get(
                "missing_components",
                []
            )
            or []
        )

        verification_message = data.get(
            "verification_message",
            ""
        )

        if not verification_message:

            if request_language == "Français":

                verification_message = (
                    "Veuillez vérifier physiquement dans votre "
                    "laboratoire que les composants requis sont "
                    "disponibles. Répondez OUI ou NON."
                )

            elif request_language == "العربية":

                verification_message = (
                    "يرجى التحقق فعلياً من توفر المكونات المطلوبة "
                    "في المختبر. أجب بنعم أو لا."
                )

            else:

                verification_message = (
                    "Please physically verify that the required "
                    "components are available in your laboratory. "
                    "Answer YES or NO."
                )

        component_text = ""

        if self.required_components:

            component_text += (
                "\n\n**Required components:**\n"
            )

            for component in self.required_components:

                component_text += (
                    f"• {component}\n"
                )

        if self.available_components:

            component_text += (
                "\n**Components reported as available:**\n"
            )

            for component in self.available_components:

                component_text += (
                    f"• {component}\n"
                )

        if self.missing_components:

            component_text += (
                "\n**Components not currently confirmed:**\n"
            )

            for component in self.missing_components:

                component_text += (
                    f"• {component}\n"
                )

        return (
            f"**{self.selected_project}**\n"
            f"{component_text}\n\n"
            f"{verification_message}"
        )

    # =========================================================
    # SUPPLIER SUBAGENT
    # =========================================================

    def _run_supplier_agent(
        self,
        request_language
    ):

        # -----------------------------------------------------
        # HARD AUTHORIZATION GATE
        # -----------------------------------------------------

        if not self.supplier_search_explicitly_confirmed:

            raise RuntimeError(
                "Supplier search was not explicitly authorized "
                "by the user."
            )

        if self.supplier_agent is None:

            raise RuntimeError(
                "Supplier subagent is not available."
            )

        if not self.missing_components:

            return (
                "No missing components are currently identified, "
                "so there is no supplier search to perform."
            )

        context = LanguageContext(
            language=request_language
        )

        prompt = f"""
{SUPPLIER_AGENT_PROMPT}

USER HAS EXPLICITLY AUTHORIZED SUPPLIER SEARCH: YES

Selected project:
{self.selected_project}

Required components:
{self.required_components}

Components already available:
{self.available_components}

Missing components:
{self.missing_components}

Search for Algerian suppliers for ONLY the missing components.

Return a compact Markdown table:

| Supplier | Website | Components | Contact | Price |

Do not include unrelated suppliers or components.

Do not invent information.

Answer in the selected user language.
"""

        response = self.supplier_agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=prompt
                    )
                ]
            },
            context=context
        )

        content = response[
            "messages"
        ][-1].content

        return self._extract_text(
            content
        )

    # =========================================================
    # COMPLETE PROJECT
    # =========================================================

    def _generate_complete_project(
        self,
        request_language
    ):

        if self.project_agent is None:

            raise RuntimeError(
                "Project subagent is not available."
            )

        context = LanguageContext(
            language=request_language
        )

        prompt = f"""
{PROJECT_AGENT_PROMPT}

The user has confirmed YES that the required components
are available in the laboratory.

Generate the complete selected project.

Selected project:
{self.selected_project}

Laboratory components:
{self.lab_components}

Required components:
{self.required_components}

Available components:
{self.available_components}

Missing components:
{self.missing_components}

The user has explicitly confirmed that the required
components are available.

Generate a complete practical laboratory project.

Include:

1. Objective
2. Recommended architecture
3. System block diagram description
4. Circuit architecture
5. Components and values
6. Signal path
7. Circuit principles
8. Power supply
9. Signal acquisition
10. Signal conditioning
11. Filtering
12. ADC / embedded system
13. ESP32 or other controller if appropriate
14. Software implementation
15. Signal processing
16. Testing procedure
17. Expected results
18. Troubleshooting
19. Safety considerations
20. Practical implementation sequence

Do NOT search for suppliers.

Do NOT ask whether to search for suppliers.

The project is now authorized for complete generation.

Keep the answer technically detailed but avoid excessive blank lines.
"""

        response = self.project_agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=prompt
                    )
                ]
            },
            context=context
        )

        content = response[
            "messages"
        ][-1].content

        return self._extract_text(
            content
        )

    # =========================================================
    # WORKFLOW PROCESSOR
    # =========================================================

    def _process_workflow(
        self,
        question,
        request_language
    ):

        state = self.workflow_state

        print()
        print("=" * 70)
        print("WORKFLOW")
        print("State:", state)
        print("User:", question)
        print("=" * 70)

        # =====================================================
        # STATE 1
        # WAITING FOR LAB COMPONENTS
        # =====================================================

        if state == "WAITING_FOR_LAB_COMPONENTS":

            self.lab_components = (
                self._parse_lab_components(
                    question
                )
            )

            if not self.lab_components:

                return (
                    "Please provide the electronic components "
                    "available in your laboratory."
                )

            self.workflow_state = (
                "WAITING_FOR_PROJECT_SELECTION"
            )

            answer = self._run_project_agent(
                f"""
The user has provided these laboratory components:

{self.lab_components}

Propose several practical biomedical instrumentation
project options based primarily on these components.

Do not search for suppliers.

Clearly number the project options so the user can
select one.
""",
                request_language
            )

            return answer

        # =====================================================
        # STATE 2
        # WAITING FOR PROJECT SELECTION
        # =====================================================

        if state == "WAITING_FOR_PROJECT_SELECTION":

            self.selected_project = question

            self.workflow_state = (
                "WAITING_FOR_COMPONENT_VERIFICATION"
            )

            return self._analyze_selected_project(
                request_language
            )

        # =====================================================
        # STATE 3
        # VERIFY COMPONENTS
        # =====================================================

        if state == "WAITING_FOR_COMPONENT_VERIFICATION":

            if self._is_yes(question):

                self.supplier_search_explicitly_confirmed = (
                    False
                )

                self.workflow_state = (
                    "PROJECT_READY"
                )

                return self._generate_complete_project(
                    request_language
                )

            if self._is_no(question):

                self.workflow_state = (
                    "WAITING_FOR_SUPPLIER_DECISION"
                )

                self.supplier_search_explicitly_confirmed = (
                    False
                )

                if request_language == "Français":

                    return (
                        "Le projet ne peut pas encore être finalisé "
                        "car un ou plusieurs composants requis n’ont "
                        "pas été confirmés comme disponibles dans "
                        "le laboratoire.\n\n"
                        "Voulez-vous que je recherche des fournisseurs "
                        "algériens pour les composants manquants ? "
                        "Répondez OUI ou NON."
                    )

                if request_language == "العربية":

                    return (
                        "لا يمكن إنهاء المشروع حالياً لأن مكوناً واحداً "
                        "أو أكثر من المكونات المطلوبة لم يتم تأكيد توفره "
                        "في المختبر.\n\n"
                        "هل تريد مني البحث عن موردين في الجزائر "
                        "للمكونات الناقصة؟ أجب بنعم أو لا."
                    )

                return (
                    "The project cannot be finalized yet because "
                    "one or more required components have not been "
                    "confirmed as available in the laboratory.\n\n"
                    "Would you like me to search for Algerian suppliers "
                    "for the missing components? Please answer YES or NO."
                )

            if request_language == "Français":

                return (
                    "Veuillez répondre OUI si les composants requis "
                    "sont disponibles dans votre laboratoire, ou NON "
                    "si un ou plusieurs composants sont manquants."
                )

            if request_language == "العربية":

                return (
                    "يرجى الإجابة بنعم إذا كانت المكونات المطلوبة "
                    "متوفرة في المختبر، أو لا إذا كان هناك مكون "
                    "واحد أو أكثر غير متوفر."
                )

            return (
                "Please answer YES if the required components are "
                "available in your laboratory, or NO if one or more "
                "components are missing."
            )

        # =====================================================
        # STATE 4
        # SUPPLIER DECISION
        # =====================================================

        if state == "WAITING_FOR_SUPPLIER_DECISION":

            if self._is_yes(question):

                # -------------------------------------------------
                # EXPLICIT YES
                # -------------------------------------------------

                self.supplier_search_explicitly_confirmed = True

                self.workflow_state = (
                    "SUPPLIER_SEARCH"
                )

                return self._run_supplier_agent(
                    request_language
                )

            if self._is_no(question):

                self.supplier_search_explicitly_confirmed = (
                    False
                )

                self.workflow_state = (
                    "WAITING_FOR_COMPONENT_VERIFICATION"
                )

                if request_language == "Français":

                    return (
                        "Le projet ne peut pas être finalisé car "
                        "les composants requis n’ont pas été confirmés "
                        "comme disponibles et la recherche de "
                        "fournisseurs a été refusée."
                    )

                if request_language == "العربية":

                    return (
                        "لا يمكن إنهاء المشروع لأن المكونات المطلوبة "
                        "لم يتم تأكيد توفرها، كما تم رفض البحث عن "
                        "الموردين."
                    )

                return (
                    "The project cannot be finalized because the "
                    "required components have not been confirmed as "
                    "available and the supplier search was declined."
                )

            if request_language == "Français":

                return (
                    "Veuillez répondre OUI si vous souhaitez rechercher "
                    "des fournisseurs algériens, ou NON si vous ne "
                    "souhaitez pas effectuer cette recherche."
                )

            if request_language == "العربية":

                return (
                    "يرجى الإجابة بنعم إذا كنت تريد البحث عن موردين "
                    "في الجزائر، أو لا إذا كنت لا تريد إجراء البحث."
                )

            return (
                "Please answer YES if you want me to search for "
                "Algerian suppliers, or NO if you do not."
            )

        # =====================================================
        # STATE 5
        # SUPPLIER SEARCH COMPLETED
        # =====================================================

        if state == "SUPPLIER_SEARCH":

            # -------------------------------------------------
            # Supplier search has already happened.
            # Do NOT automatically search again.
            # -------------------------------------------------

            if request_language == "Français":

                return (
                    "La recherche des fournisseurs a déjà été effectuée. "
                    "Vous pouvez utiliser les informations du tableau "
                    "ci-dessus."
                )

            if request_language == "العربية":

                return (
                    "تم إجراء بحث الموردين بالفعل. يمكنك استخدام "
                    "معلومات الجدول أعلاه."
                )

            return (
                "The supplier search has already been completed. "
                "You can use the supplier information in the table above."
            )

        # =====================================================
        # STATE 6
        # PROJECT READY
        # =====================================================

        if state == "PROJECT_READY":

            return self._run_project_agent(
                question,
                request_language
            )

        # =====================================================
        # FALLBACK
        # =====================================================

        self.workflow_state = (
            "WAITING_FOR_LAB_COMPONENTS"
        )

        return (
            "The workflow has been reset. "
            "Please provide the electronic components "
            "available in your laboratory."
        )

    # =========================================================
    # SEND QUESTION
    # =========================================================

    def send_question(self):

        if self.busy:
            return

        question = self.input_box.get(
            "1.0",
            "end"
        ).strip()

        if not question:
            return

        if self.agent is None:

            messagebox.showwarning(
                "Gemini is not configured",
                "Please add GOOGLE_API_KEY or "
                "GEMINI_API_KEY to your .env file."
            )

            return

        self.input_box.delete(
            "1.0",
            "end"
        )

        self._append_user(
            question
        )

        self.busy = True

        self.send_btn.configure(
            state="disabled",
            text=self._language_text(
                "thinking_button"
            )
        )

        self.status.configure(
            text=self._language_text(
                "thinking"
            )
        )

        self._start_thinking_animation()

        request_language = (
            self.current_language
        )

        threading.Thread(
            target=self._ask_agent,
            args=(
                question,
                request_language
            ),
            daemon=True
        ).start()

    # =========================================================
    # THINKING ANIMATION
    # =========================================================

    def _start_thinking_animation(self):

        if self.thinking_animation:
            return

        self.thinking_animation = True

        self.thinking_step = 0

        self._set_waiting_visible(
            True
        )

        self._start_thinking_sound()

        self._animate_thinking()

    # =========================================================
    # THINKING ANIMATION LOOP
    # =========================================================

    def _animate_thinking(self):

        if not self.thinking_animation:
            return

        self.thinking_step = (
            self.thinking_step + 1
        ) % 4

        for index, dot in enumerate(
            self.waiting_labels
        ):

            if index < self.thinking_step:

                self.avatar_panel.itemconfigure(
                    dot,
                    fill=PRIMARY
                )

            else:

                self.avatar_panel.itemconfigure(
                    dot,
                    fill="#b7c9dc"
                )

        states = [
            "Thinking",
            "Thinking.",
            "Thinking..",
            "Thinking..."
        ]

        self.avatar_panel.itemconfig(
            self.bubble_text,
            text=states[
                self.thinking_step
            ]
        )

        self.root.after(
            350,
            self._animate_thinking
        )

    # =========================================================
    # ASK AGENT / WORKFLOW
    # =========================================================

    def _ask_agent(
        self,
        question,
        request_language
    ):

        try:

            answer = self._process_workflow(
                question,
                request_language
            )

            if not answer:

                raise RuntimeError(
                    "The workflow did not return a response."
                )

        except Exception as exc:

            print(
                "Workflow error:",
                repr(exc)
            )

            error_messages = {

                "English":
                    "I could not complete the current workflow step.",

                "Français":
                    "Je n’ai pas pu terminer cette étape du processus.",

                "العربية":
                    "تعذر عليّ إكمال هذه الخطوة من سير العمل."
            }

            answer = (
                "#### Error\n\n"
                + error_messages.get(
                    request_language,
                    error_messages["English"]
                )
                + "\n\n"
                + f"**Technical details:** {exc}"
            )

        self.root.after(
            0,
            lambda:
            self._finish_answer(
                answer,
                request_language
            )
        )

    # =========================================================
    # EXTRACT RESPONSE
    # =========================================================

    @staticmethod
    def _extract_text(
        content
    ):

        if isinstance(
            content,
            str
        ):

            return content.strip()

        if isinstance(
            content,
            list
        ):

            chunks = []

            for block in content:

                if (
                    isinstance(block, dict)
                    and block.get("type") == "text"
                ):

                    chunks.append(
                        block.get(
                            "text",
                            ""
                        )
                    )

                elif isinstance(
                    block,
                    str
                ):

                    chunks.append(
                        block
                    )

            return (
                "\n".join(
                    chunks
                ).strip()
                or str(content)
            )

        return str(content)

    # =========================================================
    # FINISH ANSWER
    # =========================================================

    def _finish_answer(
        self,
        answer,
        request_language
    ):

        self.thinking_animation = False

        self._set_waiting_visible(
            False
        )

        self._stop_thinking_sound()

        recommendation_messages = {

            "English":
                "Here is what I recommend.",

            "Français":
                "Voici ce que je vous recommande.",

            "العربية":
                "إليك ما أوصي به."
        }

        recommendation = (
            recommendation_messages.get(
                request_language,
                recommendation_messages["English"]
            )
        )

        self.avatar_panel.itemconfig(
            self.bubble_text,
            text=recommendation,
            justify=(
                "right"
                if SUPPORTED_LANGUAGES.get(
                    request_language,
                    {}
                ).get("rtl", False)
                else "center"
            )
        )

        self._speak_async(
            recommendation
        )

        self.current_language = request_language

        self.language_context = LanguageContext(
            language=request_language
        )

        self._append_expert(
            answer
        )

        self.busy = False

        self.send_btn.configure(
            state="normal",
            text=self._language_text(
                "send"
            )
        )

        self.status.configure(
            text=self._language_text("ready")
        )

        self.input_box.focus_set()

    # =========================================================
    # NEW CHAT
    # =========================================================

    def _new_chat(self):

        if self.busy:
            return

        print(
            "Starting a new biomedical project chat..."
        )

        # -----------------------------------------------------
        # RESET WORKFLOW STATE
        # -----------------------------------------------------

        self.workflow_state = (
            "WAITING_FOR_LAB_COMPONENTS"
        )

        self.lab_components = []
        self.project_options = []

        self.selected_project = None

        self.required_components = []
        self.available_components = []
        self.missing_components = []

        self.supplier_search_explicitly_confirmed = (
            False
        )

        self.workflow_context = {}

        # -----------------------------------------------------
        # CLEAR CHAT
        # -----------------------------------------------------

        for widget in self.chat_scroll.winfo_children():

            widget.destroy()

        # -----------------------------------------------------
        # CLEAR INPUT
        # -----------------------------------------------------

        self.input_box.delete(
            "1.0",
            "end"
        )

        # -----------------------------------------------------
        # RESET STATUS
        # -----------------------------------------------------

        self.status.configure(
            text=self._language_text(
                "ready"
            )
        )

        # -----------------------------------------------------
        # RESET AVATAR MESSAGE
        # -----------------------------------------------------

        self.avatar_panel.itemconfig(
            self.bubble_text,
            text=""
        )

        # -----------------------------------------------------
        # NEW WELCOME
        # -----------------------------------------------------

        self._animate_welcome()

        welcome_text = (
            f"{self._language_text('hello')} "
            f"{self._language_text('expert')} "
            f"{self._language_text('help')}"
        )

        self._speak_async(
            welcome_text
        )

        self.input_box.focus_set()

    # =========================================================
    # CUSTOMTKINTER CHAT
    # =========================================================

    def _build_customtkinter_chat(
        self,
        main
    ):

        # =====================================================
        # OUTER CHAT PANEL
        # =====================================================

        self.chat_panel = ctk.CTkFrame(
            main,
            fg_color=BG_CHAT,
            corner_radius=22,
            border_width=1,
            border_color="#d6e4f2"
        )

        self.chat_panel.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.chat_panel.grid_columnconfigure(
            0,
            weight=1
        )

        self.chat_panel.grid_rowconfigure(
            1,
            weight=1
        )

        # =====================================================
        # CHAT HEADER
        # =====================================================

        self.chat_header = ctk.CTkFrame(
            self.chat_panel,
            fg_color="transparent",
            height=55,
            corner_radius=0
        )

        self.chat_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=(8, 0)
        )

        self.chat_header.grid_propagate(
            False
        )

        self.chat_title = ctk.CTkLabel(
            self.chat_header,
            text=self._language_text(
                "chat_title"
            ),
            font=("Segoe UI", 13, "bold"),
            text_color=TEXT_DARK
        )

        self.chat_title.pack(
            side="left",
            padx=(12, 0),
            pady=10
        )

        # =====================================================
        # NEW CHAT
        # =====================================================

        self.new_chat_btn = ctk.CTkButton(
            self.chat_header,
            text=self._language_text(
                "new_chat"
            ),
            command=self._new_chat,
            font=("Segoe UI", 9, "bold"),
            text_color=TEXT_DARK,
            fg_color="#e9f3ff",
            hover_color="#d5e9ff",
            corner_radius=12,
            height=30,
            width=105
        )

        self.new_chat_btn.pack(
            side="right",
            padx=8
        )

        # =====================================================
        # TEST VOICE
        # =====================================================

        self.voice_test_btn = ctk.CTkButton(
            self.chat_header,
            text=self._language_text(
                "voice"
            ),
            command=self._test_voice,
            font=("Segoe UI", 9, "bold"),
            text_color=TEXT_DARK,
            fg_color="#e9f3ff",
            hover_color="#d5e9ff",
            corner_radius=12,
            height=30,
            width=105
        )

        self.voice_test_btn.pack(
            side="right",
            padx=8
        )

        # =====================================================
        # CHAT SCROLLABLE AREA
        # =====================================================

        self.chat_scroll = ctk.CTkScrollableFrame(
            self.chat_panel,
            fg_color=BG_CHAT_AREA,
            corner_radius=18,
            scrollbar_button_color="#c9d8e8",
            scrollbar_button_hover_color="#a9bfd5"
        )

        self.chat_scroll.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(2, 8)
        )

        self.chat_scroll.grid_columnconfigure(
            0,
            weight=1
        )

        # =====================================================
        # INPUT AREA
        # =====================================================

        input_area = ctk.CTkFrame(
            self.chat_panel,
            fg_color="transparent",
            corner_radius=0
        )

        input_area.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 5)
        )

        input_area.grid_columnconfigure(
            0,
            weight=1
        )

        # =====================================================
        # INPUT BOX
        # =====================================================

        self.input_box = ctk.CTkTextbox(
            input_area,
            height=72,
            wrap="word",
            font=("Segoe UI", 11),
            fg_color=BG_INPUT,
            text_color=TEXT_NORMAL,
            border_width=1,
            border_color="#d5e3f0",
            corner_radius=16
        )

        self.input_box.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 10)
        )

        self.input_box.bind(
            "<Return>",
            self._enter_pressed
        )

        # =====================================================
        # BUTTON AREA
        # =====================================================

        button_frame = ctk.CTkFrame(
            input_area,
            fg_color="transparent"
        )

        button_frame.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        # =====================================================
        # SEND
        # =====================================================

        self.send_btn = ctk.CTkButton(
            button_frame,
            text=self._language_text(
                "send"
            ),
            command=self.send_question,
            font=("Segoe UI", 11, "bold"),
            text_color="white",
            fg_color=PRIMARY,
            hover_color=PRIMARY_DARK,
            corner_radius=14,
            height=42,
            width=120
        )

        self.send_btn.pack(
            pady=(15, 0)
        )

        # =====================================================
        # STATUS
        # =====================================================

        self.status = ctk.CTkLabel(
            self.chat_panel,
            text=self._language_text(
                "ready"
            ),
            anchor="w",
            text_color=TEXT_MUTED,
            font=("Segoe UI", 9)
        )

        self.status.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 8)
        )

    # =========================================================
    # ENTER KEY
    # =========================================================

    def _enter_pressed(
        self,
        event
    ):

        if event.state & 0x0001:
            return

        self.send_question()

        return "break"

    # =========================================================
    # CLOSE APPLICATION
    # =========================================================

    def _on_close(self):

        print(
            "Closing Biomedical Instrumentation Assistant..."
        )

        self.thinking_animation = False

        self._stop_thinking_sound()

        try:
            self.root.destroy()
        except Exception:
            pass


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    if not CUSTOMTKINTER_AVAILABLE:

        print(
            "\nCustomTkinter is not installed.\n"
            "Install it with:\n\n"
            "pip install customtkinter\n"
        )

    elif not LANGCHAIN_AVAILABLE:

        print(
            "\nLangChain/Gemini middleware is not installed.\n"
            "Install/update the required packages.\n"
        )

    else:

        root = tk.Tk()

        app = BiomedicalExpertApp(
            root
        )

        root.mainloop()