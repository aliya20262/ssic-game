# Smart Spendings Investment Challenge
## Multiplayer real-time investment game for up to 40 players

---

## Quick Start (local)

```bash
pip install -r requirements.txt
python main.py
# Open: http://localhost:8000
```

---

## Deploy FREE in 5 minutes — Railway

1. Go to https://railway.app → sign up free
2. New Project → Deploy from GitHub repo
   OR: New Project → "Deploy from template" → Python
3. Upload these files (main.py, index.html, requirements.txt, Dockerfile)
4. Railway auto-detects Dockerfile and deploys
5. Go to Settings → Networking → Generate Domain
6. Your game URL: https://your-app.railway.app

---

## Deploy FREE — Render

1. Go to https://render.com → sign up free
2. New → Web Service → connect GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy → get public URL

---

## Deploy FREE — Fly.io

```bash
# Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
fly auth login
fly launch    # follow prompts, select free tier
fly deploy
fly open
```

---

## How to run the game

### HOST (YOU):
1. Open the game URL
2. Click "Host Game"
3. Set your secret password
4. Choose rounds (4/6/8) and difficulty
5. Click "Create Room"
6. Share the 4-letter room code OR the join URL with players
7. Control buttons:
   - **Start Game** → players see allocation screen
   - **Launch Event** → shows market event, timer starts
   - **Next Round** → after all players respond
   - **End & Results** → final podium

### PLAYERS:
1. Open the game URL (same link)
2. Click "Join Game"  
3. Enter 4-letter room code + their name
4. Wait for host to start
5. Allocate portfolio → respond to events → see leaderboard

---

## Architecture

- **Backend**: FastAPI + WebSocket (Python)
- **Real-time sync**: WebSocket broadcast to all clients
- **Frontend**: Pure HTML/CSS/JS + Chart.js
- **State**: In-memory (rooms reset on server restart)
- **Capacity**: 40 players per room, multiple rooms simultaneously

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI backend + WebSocket server |
| `index.html` | Full frontend (host + player UI) |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container for cloud deployment |
| `README.md` | This file |
