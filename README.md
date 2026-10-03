# Biomedical Instrumentation Assistant

AI-powered assistant for biomedical instrumentation projects and laboratory component analysis.

## Overview

Biomedical Instrumentation Assistant is an AI-powered desktop application designed to help students, researchers, and biomedical engineers transform available laboratory components into realistic biomedical engineering projects.

The application uses **LangChain, Google Gemini, multi-agent workflows, dynamic language support, and optional Tavily web search** to provide technical guidance, project proposals, component analysis, and supplier information.

## Key Features

* 🧬 Biomedical instrumentation expertise
* 🤖 Multi-agent project workflow
* 🔬 Laboratory component analysis
* 💡 Biomedical project generation
* 🌍 English, French, and Arabic support
* 🔎 Optional supplier search
* 🖥️ Windows desktop application
* 🎙️ Voice interaction
* 🌙 Light and dark modes

## Setup

Install **Python 3.11+**. Python 3.13 can work with the current packages, while Python 3.11/3.12 is often recommended for desktop packaging.

Open Command Prompt in the project folder and install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Gemini API key:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

For optional web-based supplier searches, add:

```env
TAVILY_API_KEY=your_tavily_api_key
```

Run the application:

```bash
python biomedical_expert_gui.py
```

## Build Windows Executable

To create the Windows executable, run:

```bash
build_exe.bat
```

The executable will be generated in:

```text
dist\BiomedicalExpertAssistant\BiomedicalExpertAssistant.exe
```

## Workflow

The assistant analyzes the laboratory components provided by the user, proposes suitable biomedical projects, guides the user through project selection and component verification, and can search for missing components from suppliers when explicitly requested.

```text
Lab Components
      ↓
Project Suggestions
      ↓
Project Selection
      ↓
Component Verification
      ↓
Complete Project
      │
      └── Missing Components
              ↓
       Supplier Search
```

## Technologies

**Python · CustomTkinter · LangChain · Google Gemini · Tavily · PyInstaller**

## Security

API keys should be stored locally in `.env` and **must not be committed to GitHub**. Add `.env` to `.gitignore` and provide only `.env.example` in the repository.

----
### Author

**Dr. Ahlem BENAZZOUZ**
Research Associate Professor
Biomedical Instrumentation & Biomedical Engineering
University of Science and Technology of Oran – USTO-MB
Algeria
