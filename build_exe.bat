@echo off
setlocal
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --name BiomedicalExpertAssistant --add-data "assets;assets" biomedical_expert_gui.py
 echo.
echo EXE created in: dist\BiomedicalExpertAssistant\BiomedicalExpertAssistant.exe
pause
