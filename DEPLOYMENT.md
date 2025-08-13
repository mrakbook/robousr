# Deployment (systemd)

These units are included in the repo:

- `robousr-llama.service` – runs the local llama.cpp HTTP server
- `robousr.service` – runs the FastAPI app (starts Telethon userbot)

## 1) Create a dedicated user

```bash
sudo adduser --system --group --home /home/robousr robousr
sudo usermod -aG robousr $USER
```

## 2) Install the app

```bash
sudo -u robousr -H bash -lc '
  cd ~
  git clone <your-fork-or-repo-url> robousr
  cd robousr
  python3 -m venv venv
  source venv/bin/activate
  pip install -U pip fastapi uvicorn telethon SQLAlchemy PyMySQL pydantic openai "llama-cpp-python[server]"
  cp .env.example .env && $EDITOR .env
  mysql -u root -p telegram_bot < db/schema.sql
  PYTHONPATH=./src python -m telegram.login
'
```

Place your model file at the path referenced by `LLAMA_MODEL_PATH` (default `./models/model-q4_K.gguf`).

## 3) Install systemd units

Edit the units so `User=`, `Group=`, `WorkingDirectory=`, and absolute paths match your install.

```bash
sudo cp robousr-llama.service /etc/systemd/system/
sudo cp robousr.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now robousr-llama.service
sudo systemctl enable --now robousr.service
```

Check logs:

```bash
sudo journalctl -u robousr-llama.service -f
sudo journalctl -u robousr.service -f
```

## Reverse proxy (optional)

Terminate TLS and basic IP filtering at a proxy (e.g., NGINX or Caddy) and only expose `/status` or admin endpoints as needed. All API endpoints require HTTP Basic credentials.

## Upgrading

```bash
sudo systemctl stop robousr.service
sudo -u robousr -H bash -lc 'cd ~/robousr && git pull && source venv/bin/activate && pip install -U -r requirements.txt || true'
sudo systemctl start robousr.service
```
