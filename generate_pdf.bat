@echo off
echo Generating PDF from cv.html...
echo.
echo Please open cv.html in your browser and use Print to PDF:
echo   File: %cd%\cv.html
echo   1. Open cv.html in Chrome/Edge
echo   2. Press Ctrl+P (Print)
echo   3. Select "Save as PDF" as destination
echo   4. Click "More settings"
echo   5. Enable "Background graphics"
echo   6. Set margins to "Default"
echo   7. Save as cv.pdf
echo.
echo Alternatively, opening in browser now...
start chrome.exe --headless --disable-gpu --print-to-pdf=cv.pdf "%cd%\cv.html"
echo.
echo If Chrome is not found, you can manually open cv.html and print to PDF.
pause
