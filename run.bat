@echo off
setlocal

cd backend

if exist venv\Scripts\activate (
    echo Virtual env found
) else (
    echo Virtual env not found! Creating it...
    python -m venv venv

    echo Virtual env ok.
)

call venv\Scripts\activate

if exist requirements.txt (
    echo Instaling dependencies...
    pip install -r requirements.txt
)
echo Initializing the app...
fastapi dev main.py

endlocal