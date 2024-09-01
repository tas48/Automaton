set -e

cd backend

if [ -d "venv/bin" ]; then
    echo "Virtual env found"
else
    echo "Virtual env not found! Creating it..."
    python3 -m venv venv
    echo "Virtual env created."
fi

source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo "Initializing the app..."
fastapi dev main.py

deactivate
