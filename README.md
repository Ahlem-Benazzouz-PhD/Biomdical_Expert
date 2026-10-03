# 🧬 Biomedical Expert Assistant

**An AI-powered desktop assistant for biomedical instrumentation, project design, laboratory component analysis, and technical guidance.**

Built with **Python, CustomTkinter, LangChain, Google Gemini, and optional Tavily web search**, the Biomedical Expert Assistant provides an interactive environment for students, researchers, and biomedical engineers to explore, design, and develop biomedical instrumentation projects.

---

## ✨ Overview

The **Biomedical Expert Assistant** is a Windows desktop application that combines biomedical engineering expertise with modern AI agent technology.

The application can answer biomedical instrumentation questions, analyze available laboratory components, propose realistic project ideas, guide users through project selection, verify required components, and—when explicitly requested—search for missing components from suppliers.

The system is designed around a **multi-agent workflow**, where specialized agents handle different stages of the project-development process.

---

## 🚀 Key Features

* 🧬 **Biomedical Instrumentation Expert** — technical assistance in biomedical engineering and instrumentation
* 🤖 **Multi-Agent Architecture** — specialized project and supplier agents
* 🔬 **Laboratory Component Analysis** — transforms available components into potential biomedical projects
* 💡 **Project Proposal & Development** — generates structured and technically detailed project concepts
* 🔄 **Interactive Project Workflow** — project selection, component verification, and project completion
* 🌍 **Multilingual AI** — English, French, and Arabic
* 🔎 **Optional Web Search** — Tavily-powered supplier research
* 🎙️ **Voice Interaction** — speech output for assistant responses
* 💬 **Interactive Chat Interface** — conversational biomedical assistance
* 🌙 **Light & Dark Modes**
* 🆕 **New Chat Workflow** — resets the current project conversation without changing application preferences
* 🖥️ **Windows Desktop Application**
* 📦 **Standalone Executable** — packaged with PyInstaller

---

## 🤖 Multi-Agent Workflow

The assistant uses specialized agents to separate biomedical project reasoning from supplier research.

### 1. Biomedical Expert Agent

The main expert provides assistance with:

* Biomedical instrumentation
* Biomedical sensors and transducers
* ECG, EEG, EMG, EOG, and PPG
* Analog front-end design
* Signal acquisition
* Biomedical signal processing
* Microcontrollers and embedded systems
* Machine learning and AI for healthcare
* Experimental methodology
* Biomedical project development

### 2. Project Subagent

The Project Subagent analyzes the laboratory components provided by the user and proposes suitable biomedical engineering projects.

For example:

```text
User:
I have an AD620 instrumentation amplifier.

        ↓

Project Subagent

        ↓

Possible projects:
• ECG acquisition system
• EMG acquisition system
• EOG-based interface
• Biomedical signal conditioning system
```

The user then selects the project they want to develop.

### 3. Supplier Subagent

If required components are missing, the assistant **does not automatically search for suppliers**.

It first asks the user whether they want to search for suppliers.

Only after explicit confirmation does the Supplier Subagent perform web-based research.

Supplier results may include:

| Supplier | Website | Components Needed   | Contact           | Price        |
| -------- | ------- | ------------------- | ----------------- | ------------ |
| Supplier | Website | Required components | Available contact | If available |

The system is designed to avoid inventing supplier information, contact details, or prices.

---

## 🔄 Project Development Workflow

```text
                  ┌──────────────────────┐
                  │   Laboratory Inputs  │
                  │   Available Parts    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Project Subagent   │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Project Suggestions │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  User Selects Project│
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Component Verification│
                  └──────────┬───────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                  YES                  NO
                   │                   │
                   ▼                   ▼
          ┌─────────────────┐   ┌──────────────────┐
          │ Complete Project│   │ Ask Permission   │
          │ Development     │   │ for Supplier     │
          └─────────────────┘   │ Search           │
                                └────────┬─────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │ Supplier Subagent│
                                │  + Tavily Search │
                                └──────────────────┘
```

This workflow ensures that supplier searches occur **only after the user explicitly requests them**.

---

## 🌍 Multilingual Support

The assistant supports:

* 🇬🇧 **English**
* 🇫🇷 **Français**
* 🇩🇿 **العربية**

Language selection is integrated into the agent runtime using a **dataclass-based language context and dynamic prompt middleware**.

The selected language is dynamically passed to the AI agent so that responses are generated in the user's preferred language while preserving appropriate biomedical terminology.

---

## 🖥️ Graphical User Interface

The application provides a modern **CustomTkinter** desktop interface featuring:

* Biomedical expert avatar
* Conversational chat area
* Speech bubbles
* User input field
* Ask/Send controls
* Voice output
* Language selector
* Light/Dark theme
* New Chat control
* Responsive background processing

AI requests are handled in a background thread so that the graphical interface remains responsive while the model generates a response.

---

## 🛠️ Technology Stack

| Component              | Technology                              |
| ---------------------- | --------------------------------------- |
| Programming Language   | Python                                  |
| GUI                    | CustomTkinter / Tkinter                 |
| LLM                    | Google Gemini                           |
| AI Framework           | LangChain                               |
| Agent Architecture     | LangChain Agents / Multi-Agent Workflow |
| Web Search             | Tavily                                  |
| Environment Management | `.env`                                  |
| Packaging              | PyInstaller                             |
| Target Platform        | Windows 10/11                           |

---

## 📋 Installation Prerequisites

Before installing the application, ensure that you have:

* **Windows 10 or Windows 11**
* **Python 3.11 or newer**
* A **Google Gemini API key**
* An internet connection for AI services
* **Tavily API key** — optional, required only for web/supplier search

> Python 3.13 can work with the current dependencies. Python 3.11/3.12 may be preferable for desktop packaging compatibility.

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

Create the environment file from the provided template:

```bash
copy .env.example .env
```

Add your Gemini API key to `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

For optional web-based supplier searches:

```env
TAVILY_API_KEY=your_tavily_api_key
```

Run the application:

```bash
python biomedical_expert_gui.py
```

---

## 📦 Build the Windows Application

The repository includes a Windows build script.

Run:

```bash
build_exe.bat
```

The packaged application will be generated under:

```text
dist\
└── BiomedicalExpertAssistant\
    └── BiomedicalExpertAssistant.exe
```

The executable can then be launched directly on Windows.

---

## 📁 Repository Structure

```text
BiomedicalExpertAssistant/
│
├── biomedical_expert_gui.py      # Main desktop application
├── requirements.txt              # Python dependencies
├── .env.example                  # API key template
├── .gitignore                    # Ignored files
├── build_exe.bat                 # Windows build script
├── README.md                     # Project documentation
│
├── assets/
│   ├── icon.ico
│   ├── biomedical_expert3.png
│   ├── image_1.png
│   ├── image_2.png
│   └── thinking_chime.wav
│
└── dist/                         # Generated during packaging
    └── BiomedicalExpertAssistant/
        └── BiomedicalExpertAssistant.exe
```

---

## 🔐 Security & API Keys

API keys are loaded from the local `.env` file and are **not hard-coded into the source code**.

Never commit `.env` or expose your API keys publicly.

Your repository should contain:

```text
.env.example
```

but **not**:

```text
.env
```

Make sure `.env` is included in `.gitignore`.

> **Important:** The Windows executable still requires access to the `.env` file containing the API key. The key should not be embedded directly into the executable.

---

## 🎯 Intended Applications

The Biomedical Expert Assistant can support:

* Biomedical engineering education
* Student projects
* Laboratory project development
* Biomedical instrumentation research
* Sensor and signal acquisition projects
* AI-assisted biomedical engineering
* Laboratory resource exploration
* Early-stage prototype development

---

## 🔬 Example

A user enters:

```text
I have an AD620 instrumentation amplifier.
```

The assistant can analyze the component and propose biomedical applications such as:

```text
1. ECG acquisition system
2. EMG acquisition system
3. EOG-based human-computer interface
4. Biomedical signal conditioning system
```

After the user selects a project, the assistant verifies the required components and guides the user toward project implementation.

---

## 📌 Project Status

**Active Development**

The project is continuously being improved with additional biomedical capabilities, AI-agent workflows, interface features, and deployment options.

---

## 👩‍🔬 Author

**Dr. Ahlem BENAZZOUZ**
Research Associate Professor
Biomedical Instrumentation & Biomedical Engineering
University of Science and Technology of Oran – USTO-MB
Algeria
