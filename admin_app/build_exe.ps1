Write-Host "Installing PyInstaller and requirements..."
pip install -r requirements.txt
pip install pyinstaller requests

Write-Host "Building standalone executable..."
python -m PyInstaller --noconfirm --onefile --windowed --name "ParulDiagnosticDashboard" "main.py"

Write-Host ""
Write-Host "============================"
Write-Host "Build finished. Standalone executable is at: dist\ParulDiagnosticDashboard.exe"
Write-Host "You can share this single .exe file with any Windows PC. No Python installation required."
Write-Host "============================"
