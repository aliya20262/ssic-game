from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json, asyncio, random, string, time, os
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─── GAME DATA ───────────────────────────────────────────────
EVENTS = [
    {"type":"Crisis","title":"Global market crash","desc":"Equity markets plunge 20%+ as recession fears explode. Credit markets seize and investors flee to safety assets.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"Stocks -28%","c":"badge-red"},{"t":"ETFs -16%","c":"badge-red"},{"t":"Bonds +5%","c":"badge-green"},{"t":"Cash safe","c":"badge-gray"}],
     "m":{"stocks":-.28,"bonds":.05,"etf":-.16,"deposit":.03,"cash":0}},
    {"type":"Macro","title":"Inflation surges to 9%","desc":"Consumer prices hit 40-year highs. Rate hike cycle begins and fixed income reprices sharply downward.",
     "col":"#fffbeb","brd":"#fcd34d","tc":"#92400e",
     "pills":[{"t":"Bonds -12%","c":"badge-red"},{"t":"Cash erodes","c":"badge-amber"},{"t":"Deposits +4%","c":"badge-green"},{"t":"Stocks flat","c":"badge-gray"}],
     "m":{"stocks":.02,"bonds":-.12,"etf":-.03,"deposit":.04,"cash":-.02}},
    {"type":"Commodity","title":"Oil price spikes +60%","desc":"Geopolitical tensions slash global supply. Energy names surge while transport and consumer sectors suffer.",
     "col":"#fffbeb","brd":"#fbbf24","tc":"#92400e",
     "pills":[{"t":"Energy +30%","c":"badge-green"},{"t":"ETFs +9%","c":"badge-green"},{"t":"Bonds flat","c":"badge-gray"},{"t":"Consumer down","c":"badge-red"}],
     "m":{"stocks":.09,"bonds":.01,"etf":.10,"deposit":.02,"cash":0}},
    {"type":"Growth","title":"AI technology boom","desc":"Breakthrough AI product goes viral. Tech earnings explode and investors flood equities and index funds.",
     "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
     "pills":[{"t":"Stocks +32%","c":"badge-green"},{"t":"ETFs +19%","c":"badge-green"},{"t":"Bonds hold","c":"badge-gray"},{"t":"Economy up","c":"badge-green"}],
     "m":{"stocks":.33,"bonds":.01,"etf":.20,"deposit":.02,"cash":0}},
    {"type":"Crisis","title":"Banking sector collapse","desc":"Three major banks fail overnight. Deposit insurance triggers and market-wide panic spreads rapidly.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"Banks -35%","c":"badge-red"},{"t":"Bonds +8%","c":"badge-green"},{"t":"Deposits risky","c":"badge-amber"},{"t":"Cash is king","c":"badge-gray"}],
     "m":{"stocks":-.20,"bonds":.08,"etf":-.13,"deposit":-.06,"cash":.01}},
    {"type":"Policy","title":"Interest rates jump +3%","desc":"Central bank delivers a surprise jumbo rate hike. Bond prices crater and mortgage costs spike.",
     "col":"#eff6ff","brd":"#93c5fd","tc":"#1e40af",
     "pills":[{"t":"Bonds -14%","c":"badge-red"},{"t":"Deposits +7%","c":"badge-green"},{"t":"Stocks -6%","c":"badge-red"},{"t":"Cash ok","c":"badge-gray"}],
     "m":{"stocks":-.06,"bonds":-.14,"etf":-.05,"deposit":.07,"cash":.01}},
    {"type":"Macro","title":"Sudden recession hits","desc":"GDP contracts two consecutive quarters. Unemployment surges to 8% and consumer spending collapses.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"Stocks -22%","c":"badge-red"},{"t":"ETFs -14%","c":"badge-red"},{"t":"Bonds +6%","c":"badge-green"},{"t":"Cash stable","c":"badge-gray"}],
     "m":{"stocks":-.22,"bonds":.06,"etf":-.14,"deposit":.03,"cash":0}},
    {"type":"Geopolitical","title":"Political crisis erupts","desc":"Constitutional crisis triggers snap elections. Foreign capital flees and currency devalues sharply.",
     "col":"#fffbeb","brd":"#fcd34d","tc":"#92400e",
     "pills":[{"t":"Markets -12%","c":"badge-red"},{"t":"Bonds volatile","c":"badge-amber"},{"t":"Cash -2%","c":"badge-amber"},{"t":"Safe havens up","c":"badge-green"}],
     "m":{"stocks":-.12,"bonds":-.07,"etf":-.10,"deposit":.01,"cash":-.02}},
    {"type":"Tech","title":"Crypto market meltdown","desc":"Major stablecoin depegs. Crypto contagion spreads to tech stocks and risk assets globally.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"Tech -18%","c":"badge-red"},{"t":"Bonds +4%","c":"badge-green"},{"t":"Cash +0%","c":"badge-gray"},{"t":"Deposits safe","c":"badge-green"}],
     "m":{"stocks":-.18,"bonds":.04,"etf":-.12,"deposit":.02,"cash":0}},
    {"type":"Growth","title":"Green energy revolution","desc":"Historic climate bill passes. Renewable energy stocks surge 40%. Fossil fuel divestment accelerates.",
     "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
     "pills":[{"t":"Green stocks +35%","c":"badge-green"},{"t":"ETFs +12%","c":"badge-green"},{"t":"Oil sector -15%","c":"badge-red"},{"t":"Bonds steady","c":"badge-gray"}],
     "m":{"stocks":.22,"bonds":.01,"etf":.13,"deposit":.02,"cash":0}},
]

AVATAR_COLORS = [
    "#2563eb","#059669","#dc2626","#d97706","#7c3aed","#0891b2",
    "#db2777","#65a30d","#ea580c","#0f766e","#7c2d12","#1e40af",
    "#166534","#991b1b","#92400e","#4c1d95","#164e63","#881337",
    "#3f6212","#78350f","#1d4ed8","#047857","#b91c1c","#b45309",
    "#6d28d9","#0e7490","#be185d","#4d7c0f","#c2410c","#0f766e"
]

# ─── ROOM STATE ──────────────────────────────────────────────
rooms: Dict[str, dict] = {}
connections: Dict[str, Dict[str, WebSocket]] = {}  # room_code -> {player_id: ws}
host_connections: Dict[str, WebSocket] = {}  # room_code -> host_ws

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

def new_room(host_password: str, total_rounds: int, diff: str) -> dict:
    code = gen_code()
    while code in rooms:
        code = gen_code()
    evs = random.sample(EVENTS, min(total_rounds, len(EVENTS)))
    return {
        "code": code,
        "host_password": host_password,
        "phase": "lobby",  # lobby | alloc | event | result | final
        "round": 0,
        "total_rounds": total_rounds,
        "diff": diff,
        "event_queue": evs,
        "players": {},  # pid -> player dict
        "created_at": time.time(),
        "timer_task": None,
    }

def new_player(name: str, color: str) -> dict:
    return {
        "name": name,
        "color": color,
        "initials": ''.join([w[0] for w in name.strip().split() if w])[:2].upper() or "?",
        "capital": 10000,
        "history": [10000],
        "alloc": {"stocks": 0, "bonds": 0, "etf": 0, "deposit": 0, "cash": 0},
        "round_done": False,
        "decisions": [],
        "confirmed_alloc": False,
    }

# ─── BROADCAST HELPERS ───────────────────────────────────────
async def broadcast_room(code: str, msg: dict):
    if code not in connections:
        return
    dead = []
    for pid, ws in connections[code].items():
        try:
            await ws.send_text(json.dumps(msg))
        except:
            dead.append(pid)
    for pid in dead:
        connections[code].pop(pid, None)

async def send_host(code: str, msg: dict):
    ws = host_connections.get(code)
    if ws:
        try:
            await ws.send_text(json.dumps(msg))
        except:
            host_connections.pop(code, None)

async def send_player(code: str, pid: str, msg: dict):
    ws = connections.get(code, {}).get(pid)
    if ws:
        try:
            await ws.send_text(json.dumps(msg))
        except:
            pass

async def broadcast_state(code: str):
    room = rooms.get(code)
    if not room:
        return
    state = room_state(room)
    await broadcast_room(code, {"type": "state", "data": state})
    await send_host(code, {"type": "state", "data": state})

def room_state(room: dict) -> dict:
    ev_idx = room["round"] - 1
    current_event = None
    if 0 <= ev_idx < len(room["event_queue"]):
        current_event = room["event_queue"][ev_idx]
    return {
        "code": room["code"],
        "phase": room["phase"],
        "round": room["round"],
        "total_rounds": room["total_rounds"],
        "diff": room["diff"],
        "current_event": current_event,
        "players": room["players"],
    }

# ─── HTTP ENDPOINTS ──────────────────────────────────────────
@app.post("/api/create-room")
async def create_room(body: dict):
    password = body.get("password", "").strip()
    total_rounds = int(body.get("total_rounds", 6))
    diff = body.get("diff", "medium")
    if not password:
        raise HTTPException(400, "Password required")
    total_rounds = max(3, min(10, total_rounds))
    room = new_room(password, total_rounds, diff)
    rooms[room["code"]] = room
    connections[room["code"]] = {}
    return {"code": room["code"]}

@app.post("/api/join-room")
async def join_room(body: dict):
    code = body.get("code", "").strip().upper()
    name = body.get("name", "").strip()
    if not code or not name:
        raise HTTPException(400, "Code and name required")
    room = rooms.get(code)
    if not room:
        raise HTTPException(404, "Room not found")
    if room["phase"] == "final":
        raise HTTPException(400, "Game already ended")
    if len(room["players"]) >= 40:
        raise HTTPException(400, "Room is full (40 max)")
    names_taken = [p["name"].lower() for p in room["players"].values()]
    if name.lower() in names_taken:
        raise HTTPException(400, "Name already taken")
    color_idx = len(room["players"]) % len(AVATAR_COLORS)
    color = AVATAR_COLORS[color_idx]
    pid = f"p_{int(time.time()*1000)}_{random.randint(1000,9999)}"
    room["players"][pid] = new_player(name, color)
    await broadcast_state(code)
    return {"pid": pid, "color": color, "name": name}

@app.post("/api/host-action")
async def host_action(body: dict):
    code = body.get("code", "").upper()
    password = body.get("password", "")
    action = body.get("action", "")
    room = rooms.get(code)
    if not room:
        raise HTTPException(404, "Room not found")
    if room["host_password"] != password:
        raise HTTPException(403, "Wrong password")

    if action == "start":
        if room["phase"] != "lobby":
            raise HTTPException(400, "Already started")
        if not room["players"]:
            raise HTTPException(400, "No players")
        room["phase"] = "alloc"
        room["round"] = 1
        for p in room["players"].values():
            p["round_done"] = False
            p["confirmed_alloc"] = False
        await broadcast_state(code)

    elif action == "next_round":
        if room["round"] >= room["total_rounds"]:
            room["phase"] = "final"
        else:
            room["round"] += 1
            room["phase"] = "alloc"
            for p in room["players"].values():
                p["round_done"] = False
                p["confirmed_alloc"] = False
        await broadcast_state(code)

    elif action == "start_event":
        room["phase"] = "event"
        for p in room["players"].values():
            p["round_done"] = False
        await broadcast_state(code)
        # Auto-progress if all done (also handle timer)
        asyncio.create_task(watch_round(code))

    elif action == "end":
        room["phase"] = "final"
        await broadcast_state(code)

    return {"ok": True}

async def watch_round(code: str):
    """Auto-advance round to result when all players are done."""
    room = rooms.get(code)
    if not room:
        return
    diff_times = {"easy": 62, "medium": 32, "hard": 17}
    wait = diff_times.get(room.get("diff", "medium"), 32)
    for _ in range(wait * 2):
        await asyncio.sleep(0.5)
        room = rooms.get(code)
        if not room or room["phase"] != "event":
            return
        players = list(room["players"].values())
        if players and all(p["round_done"] for p in players):
            room["phase"] = "result"
            await broadcast_state(code)
            return
    # Timer expired — force all undone players to hold
    room = rooms.get(code)
    if room and room["phase"] == "event":
        for p in room["players"].values():
            if not p["round_done"]:
                apply_action(room, p, "hold")
        room["phase"] = "result"
        await broadcast_state(code)

def apply_action(room: dict, player: dict, action: str):
    ev_idx = room["round"] - 1
    if ev_idx < 0 or ev_idx >= len(room["event_queue"]):
        return
    ev = room["event_queue"][ev_idx]
    mod = 0.45 if action == "sell" else 1.55 if action == "buy" else 1.0
    alloc = player["alloc"]
    total_alloc = sum(alloc.values())
    nc = 0
    for asset_id, pct in alloc.items():
        share = player["capital"] * pct / 100
        nc += share * (1 + ev["m"][asset_id] * mod)
    unalloc = player["capital"] * (1 - total_alloc / 100)
    nc += unalloc
    nc = round(nc)
    delta = nc - player["capital"]
    player["capital"] = nc
    player["history"].append(nc)
    player["round_done"] = True
    player["decisions"].append({"round": room["round"], "action": action, "delta": delta})

@app.post("/api/player-action")
async def player_action(body: dict):
    code = body.get("code", "").upper()
    pid = body.get("pid", "")
    action_type = body.get("action", "")
    room = rooms.get(code)
    if not room:
        raise HTTPException(404, "Room not found")
    player = room["players"].get(pid)
    if not player:
        raise HTTPException(404, "Player not found")

    if action_type == "set_alloc":
        alloc = body.get("alloc", {})
        total = sum(alloc.values())
        if total > 100:
            raise HTTPException(400, "Allocation exceeds 100%")
        player["alloc"] = alloc
        player["confirmed_alloc"] = True
        await broadcast_state(code)

    elif action_type in ("sell", "hold", "buy"):
        if player["round_done"]:
            raise HTTPException(400, "Already acted this round")
        if room["phase"] != "event":
            raise HTTPException(400, "Not in event phase")
        apply_action(room, player, action_type)
        # Check if all done
        all_done = all(p["round_done"] for p in room["players"].values())
        if all_done:
            room["phase"] = "result"
        await broadcast_state(code)

    return {"ok": True, "capital": player.get("capital", 10000)}

@app.get("/api/room/{code}")
async def get_room(code: str):
    room = rooms.get(code.upper())
    if not room:
        raise HTTPException(404, "Room not found")
    return room_state(room)

# ─── WEBSOCKET ───────────────────────────────────────────────
@app.websocket("/ws/{code}/{pid}")
async def ws_player(websocket: WebSocket, code: str, pid: str):
    code = code.upper()
    await websocket.accept()
    if code not in connections:
        connections[code] = {}
    connections[code][pid] = websocket
    # Send current state immediately
    room = rooms.get(code)
    if room:
        await websocket.send_text(json.dumps({"type": "state", "data": room_state(room)}))
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        connections.get(code, {}).pop(pid, None)

@app.websocket("/ws-host/{code}")
async def ws_host(websocket: WebSocket, code: str):
    code = code.upper()
    await websocket.accept()
    host_connections[code] = websocket
    room = rooms.get(code)
    if room:
        await websocket.send_text(json.dumps({"type": "state", "data": room_state(room)}))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        host_connections.pop(code, None)

# ─── SERVE FRONTEND ──────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r") as f:
        return f.read()

@app.get("/host", response_class=HTMLResponse)
async def host_page():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
