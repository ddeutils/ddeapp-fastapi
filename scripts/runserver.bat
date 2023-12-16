@echo off
goto :init

:usage
    echo USAGE:
    echo   %__bat_filename% [flags] "release argument"
    echo.
    echo.  -h, --help           shows this help
    echo.  -p, --port value     specifies a port number value
    echo.  --reload             enable auto-reload
    goto :eof

:missing_args
    call :usage
    echo.
    echo ****
    echo MISSING RELEASE ARGUMENT !!!
    goto :eof

:port
    echo Port does set from argument and port changes from 8000 to %__port% ...
    goto :eof

:version
    if "%~1"=="full" call :usage & goto :eof
    echo %__version%
    goto :eof

:init
    set "__name=%~n0"
    set "__port=8000"

    set "__bat_filepath=%~0"
    set "__bat_path=%~dp0"
    set "__bat_filename=%~nx0"

    set "__version=0.1.0"
    set "__reload="
    set "__release="

:parse
    if "%~1"==""                goto :validate

    if /i "%~1"=="-h"           call :usage "%~2" & goto :end
    if /i "%~1"=="--help"       call :usage "%~2" & goto :end

    if /i "%~1"=="-v"           call :version      & goto :end
    if /i "%~1"=="--version"    call :version full & goto :end

    if /i "%~1"=="-p"           set "__port=%~2" & shift & shift & call :port & goto :parse
    if /i "%~1"=="--port"       set "__port=%~2" & shift & shift & call :port & goto :parse

    if /i "%~1"=="--reload"     set "__reload=--reload" & shift & goto :parse

    if not defined __release    set "__release=%~1" & shift & goto :parse

    shift
    goto :parse

:validate
    if not defined __release call :missing_args & goto :end

:main
    echo INFO: Start running server with release "%__release%" ...
    call .\venv\Scripts\activate
    call uvicorn main:app --port %__port% %__reload%

:end
    echo.
    echo End and Clean Up
    call :cleanup
    exit /B

:cleanup
    REM The cleanup function is only really necessary if you
    REM are _not_ using SETLOCAL.

    set "__name="
    set "__port="

    set "__bat_filepath="
    set "__bat_path="
    set "__bat_filename="

    set "__release="
    set "__version="
    set "__reload="

    goto :eof
