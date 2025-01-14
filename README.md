# Create venv
python -m venv venv

# Activate venv
## Windows
venv\Scripts\activate

## macOS/Linux
source venv/bin/activate

# Deactivate venv
deactivate

# Install dependencies
pip install -r requirements.txt


# Run server
fastapi dev main.py

# Specify FastAPI's Port 8080
uvicorn main:app --host 127.0.0.1 --port 8080 --reload


# Check port to not have conflicts
## macOS/Linux
netstat -tuln | grep 8080
## Windows
netstat -ano | find "8080"
