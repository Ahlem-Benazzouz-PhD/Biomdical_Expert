# Biomedical Expert Assistant

A Tkinter desktop GUI for a biomedical instrumentation AI assistant powered by LangChain + Google Gemini.

## Features
- Biomedical expert cartoon panel on the left
- Startup speech bubble with the requested introduction
- Input and output chat areas on the right
- Ask button + Send button
- Background thread so the GUI remains responsive while Gemini answers
- Optional Tavily web search
- API keys stored in `.env`, not hard-coded
- Windows `.bat` build script for a standalone executable

## Setup
1. Install Python 3.11+ (Python 3.13 can work with current packages, but 3.11/3.12 is often the safest choice for desktop packaging).
2. Open Command Prompt in this folder.
3. Run:
   `python -m pip install -r requirements.txt`
4. Copy `.env.example` to `.env`.
5. Put your Gemini API key in `.env` as `GOOGLE_API_KEY=...`.
6. Optional: add `TAVILY_API_KEY=...` for web search.
7. Test with:
   `python biomedical_expert_gui.py`
8. Build the Windows executable:
   `build_exe.bat`

The executable will be under `dist\\BiomedicalExpertAssistant\\BiomedicalExpertAssistant.exe`.

## Important
The executable still needs the `.env` file next to it because the Gemini key should not be embedded in the application. Do not publish the `.env` file or your API key.
