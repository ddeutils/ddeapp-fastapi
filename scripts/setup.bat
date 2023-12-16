:: Turn off command display and allows environmental variables to be overridden
:: for the current session
:: ---
@echo off
if exist ".\.env" (
    del ".\.env"
)
echo f | xcopy /f /y ".{demo}.env" ".dev.env"
ren ".dev.env" ".env"

:: Set up NSSM package
:: ---
:: if exist ".\nssm" (
::     rmdir /s /q ".\nssm"
:: ) else (
::     echo Folder '.\nssm' doesn't exist, it will automate unzip ...
:: )
:: powershell Expand-Archive ".\assets\nssm-2.24.zip" -DestinationPath "."
:: powershell Rename-Item ".\nssm-2.24" "nssm"

if not exist ".\logs" (
    mkdir ".\logs"
)

:: Setup python virtual environment
:: ---
call python -m venv venv
call .\venv\Scripts\activate

:: Pip install python dependencies
:: ---
::call pip install -r .\requirements.txt --no-cache
call pip install --no-index --find-links=wheels/ -r requirements.txt
