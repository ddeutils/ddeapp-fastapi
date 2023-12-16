if exist ".\.env" (
    del ".\.env"
)
if exist ".\nssm" (
    rmdir /s /q ".\nssm"
)
if exist ".\logs" (
    rmdir /s /q ".\logs"
)
