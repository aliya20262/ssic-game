from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json, asyncio, random, string, time
from typing import Dict

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

EVENTS = [
    {"type":"Crisis","title":"Global market crash","desc":"Equity markets plunge 20%+ as recession fears explode. Credit markets seize and investors flee to safety assets.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"Stocks -28%","c":"badge-red"},{"t":"ETFs -16%","c":"badge-red"},{"t":"Bonds +5%","c":"badge-green"},{"t":"Cash safe","c":"badge-gray"}],
     "m":{"stocks":-.28,"bonds":.05,"etf":-.16,"deposit":.03,"cash":0}},
    {"type":"Macro","title":"Inflation surges to 9%","desc":"Consumer prices hit 40-year highs. Rate hike cycle begins and fixed income reprices sharply.",
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
     "pills":[{"t":"Tech -18%","c":"badge-red"},{"t":"Bonds +4%","c":"badge-green"},{"t":"Cash safe","c":"badge-gray"},{"t":"Deposits ok","c":"badge-green"}],
     "m":{"stocks":-.18,"bonds":.04,"etf":-.12,"deposit":.02,"cash":0}},
    {"type":"Growth","title":"Green energy revolution","desc":"Historic climate bill passes. Renewable energy stocks surge. Fossil fuel divestment accelerates worldwide.",
     "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
     "pills":[{"t":"Green stocks +35%","c":"badge-green"},{"t":"ETFs +12%","c":"badge-green"},{"t":"Oil sector -15%","c":"badge-red"},{"t":"Bonds steady","c":"badge-gray"}],
     "m":{"stocks":.22,"bonds":.01,"etf":.13,"deposit":.02,"cash":0}},
    {"type":"Crisis","title":"Trade war escalates","desc":"Major economies impose sweeping tariffs. Supply chains collapse. Global trade volumes drop 15%.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"Stocks -19%","c":"badge-red"},{"t":"ETFs -11%","c":"badge-red"},{"t":"Bonds +3%","c":"badge-green"},{"t":"Cash safe","c":"badge-gray"}],
     "m":{"stocks":-.19,"bonds":.03,"etf":-.11,"deposit":.02,"cash":.01}},
    {"type":"Growth","title":"Biotech breakthrough","desc":"Revolutionary cancer treatment approved. Pharmaceutical stocks surge. Healthcare sector leads global rally.",
     "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
     "pills":[{"t":"Biotech +40%","c":"badge-green"},{"t":"ETFs +14%","c":"badge-green"},{"t":"Bonds flat","c":"badge-gray"},{"t":"Economy grows","c":"badge-green"}],
     "m":{"stocks":.28,"bonds":.01,"etf":.15,"deposit":.02,"cash":0}},
    {"type":"Macro","title":"Unemployment hits 12%","desc":"Mass layoffs sweep tech and manufacturing. Consumer confidence collapses. Spending contracts sharply.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"Stocks -16%","c":"badge-red"},{"t":"Bonds +5%","c":"badge-green"},{"t":"ETFs -10%","c":"badge-red"},{"t":"Cash stable","c":"badge-gray"}],
     "m":{"stocks":-.16,"bonds":.05,"etf":-.10,"deposit":.03,"cash":0}},
    {"type":"Policy","title":"Central bank cuts rates -2%","desc":"Emergency rate cuts to fight recession. Bond prices surge. Banks increase lending aggressively.",
     "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
     "pills":[{"t":"Bonds +15%","c":"badge-green"},{"t":"Stocks +8%","c":"badge-green"},{"t":"ETFs +10%","c":"badge-green"},{"t":"Deposits -3%","c":"badge-red"}],
     "m":{"stocks":.08,"bonds":.15,"etf":.10,"deposit":-.03,"cash":0}},
    {"type":"Geopolitical","title":"Regional war breaks out","desc":"Armed conflict erupts in a major oil-producing region. Defense stocks surge. Energy prices spike.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"Defense +25%","c":"badge-green"},{"t":"Oil +40%","c":"badge-green"},{"t":"Markets -14%","c":"badge-red"},{"t":"Bonds +4%","c":"badge-green"}],
     "m":{"stocks":-.08,"bonds":.04,"etf":-.06,"deposit":.02,"cash":.01}},
    {"type":"Growth","title":"Space economy takes off","desc":"First commercial space station launches. Satellite internet reaches 3 billion users. Space ETFs explode.",
     "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
     "pills":[{"t":"Tech +28%","c":"badge-green"},{"t":"ETFs +16%","c":"badge-green"},{"t":"Bonds flat","c":"badge-gray"},{"t":"Economy booms","c":"badge-green"}],
     "m":{"stocks":.28,"bonds":.01,"etf":.16,"deposit":.02,"cash":0}},
    {"type":"Crisis","title":"Sovereign debt default","desc":"Major emerging market defaults on $500B debt. Contagion spreads to European bond markets.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"EM stocks -30%","c":"badge-red"},{"t":"Bonds -8%","c":"badge-red"},{"t":"ETFs -12%","c":"badge-red"},{"t":"Cash safe","c":"badge-gray"}],
     "m":{"stocks":-.24,"bonds":-.08,"etf":-.12,"deposit":.01,"cash":.02}},
    {"type":"Macro","title":"Supply chain crisis","desc":"Global shipping disrupted by simultaneous port strikes. Inflation spikes. Production halts worldwide.",
     "col":"#fffbeb","brd":"#fcd34d","tc":"#92400e",
     "pills":[{"t":"Stocks -8%","c":"badge-red"},{"t":"ETFs -5%","c":"badge-red"},{"t":"Commodities +20%","c":"badge-green"},{"t":"Deposits ok","c":"badge-gray"}],
     "m":{"stocks":-.08,"bonds":-.03,"etf":-.05,"deposit":.03,"cash":-.01}},
    {"type":"Growth","title":"Electric vehicle revolution","desc":"EV sales overtake combustion engines. Battery costs collapse 80%. Auto and energy sectors transform.",
     "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
     "pills":[{"t":"EV stocks +45%","c":"badge-green"},{"t":"ETFs +18%","c":"badge-green"},{"t":"Oil down","c":"badge-red"},{"t":"Bonds steady","c":"badge-gray"}],
     "m":{"stocks":.25,"bonds":.01,"etf":.18,"deposit":.02,"cash":0}},
    {"type":"Crisis","title":"Cyberattack on banks","desc":"Coordinated attack hits 50 major banks. ATMs go dark. Online payments freeze for 48 hours.",
     "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
     "pills":[{"t":"Banks -22%","c":"badge-red"},{"t":"Stocks -10%","c":"badge-red"},{"t":"Cash king","c":"badge-green"},{"t":"Bonds +3%","c":"badge-green"}],
     "m":{"stocks":-.15,"bonds":.03,"etf":-.10,"deposit":-.04,"cash":.03}},
]

AVATAR_COLORS = [
    "#2563eb","#059669","#dc2626","#d97706","#7c3aed","#0891b2",
    "#db2777","#65a30d","#ea580c","#0f766e","#7c2d12","#1e40af",
    "#166534","#991b1b","#92400e","#4c1d95","#164e63","#881337",
    "#3f6212","#78350f","#1d4ed8","#047857","#b91c1c","#b45309",
    "#6d28d9","#0e7490","#be185d","#4d7c0f","#c2410c","#0f766e",
    "#312e81","#064e3b","#7f1d1d","#451a03","#1e1b4b","#022c22",
    "#4a1942","#0c4a6e","#14532d","#431407"
]

rooms: Dict[str, dict] = {}
connections: Dict[str, Dict[str, WebSocket]] = {}
host_connections: Dict[str, WebSocket] = {}

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

def new_room(host_password, total_rounds, diff):
    code = gen_code()
    while code in rooms:
        code = gen_code()
    evs = random.sample(EVENTS, min(total_rounds, len(EVENTS)))
    return {
        "code": code, "host_password": host_password,
        "phase": "lobby", "round": 0, "total_rounds": total_rounds, "diff": diff,
        "event_queue": evs, "players": {}, "created_at": time.time(),
    }

def new_player(name, color):
    return {
        "name": name, "color": color,
        "initials": ''.join([w[0] for w in name.strip().split() if w])[:2].upper() or "?",
        "capital": 10000, "history": [10000], "best_round": 0, "worst_round": 0,
        "alloc": {"stocks":0,"bonds":0,"etf":0,"deposit":0,"cash":0},
        "round_done": False, "decisions": [], "confirmed_alloc": False,
        "badge": None,
    }

async def broadcast_room(code, msg):
    dead = []
    for pid, ws in connections.get(code, {}).items():
        try:
            await ws.send_text(json.dumps(msg))
        except:
            dead.append(pid)
    for pid in dead:
        connections.get(code, {}).pop(pid, None)

async def send_host(code, msg):
    ws = host_connections.get(code)
    if ws:
        try:
            await ws.send_text(json.dumps(msg))
        except:
            host_connections.pop(code, None)

async def broadcast_state(code):
    room = rooms.get(code)
    if not room:
        return
    state = room_state(room)
    await broadcast_room(code, {"type": "state", "data": state})
    await send_host(code, {"type": "state", "data": state})

def room_state(room):
    ev_idx = room["round"] - 1
    current_event = None
    if 0 <= ev_idx < len(room["event_queue"]):
        current_event = room["event_queue"][ev_idx]
    return {
        "code": room["code"], "phase": room["phase"],
        "round": room["round"], "total_rounds": room["total_rounds"],
        "diff": room["diff"], "current_event": current_event,
        "players": room["players"],
    }

def assign_badges(room):
    players = list(room["players"].values())
    if not players:
        return
    sorted_p = sorted(players, key=lambda p: p["capital"], reverse=True)
    for i, p in enumerate(sorted_p):
        ret = (p["capital"] - 10000) / 10000
        if i == 0:
            p["badge"] = "champion"
        elif ret > 0.15:
            p["badge"] = "bull"
        elif ret < -0.15:
            p["badge"] = "bear"
        elif abs(ret) < 0.03:
            p["badge"] = "steady"
        else:
            p["badge"] = "learner"

@app.post("/api/create-room")
async def create_room(body: dict):
    password = body.get("password", "").strip()
    total_rounds = max(3, min(15, int(body.get("total_rounds", 6))))
    diff = body.get("diff", "medium")
    if not password:
        raise HTTPException(400, "Password required")
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
    if len(room["players"]) >= 100:
        raise HTTPException(400, "Room is full (100 max)")
    if name.lower() in [p["name"].lower() for p in room["players"].values()]:
        raise HTTPException(400, "Name already taken")
    color = AVATAR_COLORS[len(room["players"]) % len(AVATAR_COLORS)]
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
            assign_badges(room)
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
        asyncio.create_task(watch_round(code))
    elif action == "end":
        assign_badges(room)
        room["phase"] = "final"
        await broadcast_state(code)
    return {"ok": True}

async def watch_round(code):
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
        if all(p["round_done"] for p in room["players"].values()):
            room["phase"] = "result"
            await broadcast_state(code)
            return
    room = rooms.get(code)
    if room and room["phase"] == "event":
        for p in room["players"].values():
            if not p["round_done"]:
                apply_action(room, p, "hold")
        room["phase"] = "result"
        await broadcast_state(code)

def apply_action(room, player, action):
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
    nc += player["capital"] * (1 - total_alloc / 100)
    nc = max(100, round(nc))
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
        if sum(alloc.values()) > 100:
            raise HTTPException(400, "Allocation exceeds 100%")
        player["alloc"] = alloc
        player["confirmed_alloc"] = True
        await broadcast_state(code)
    elif action_type in ("sell", "hold", "buy"):
        if player["round_done"]:
            raise HTTPException(400, "Already acted")
        if room["phase"] != "event":
            raise HTTPException(400, "Not in event phase")
        apply_action(room, player, action_type)
        if all(p["round_done"] for p in room["players"].values()):
            room["phase"] = "result"
        await broadcast_state(code)
    return {"ok": True, "capital": player.get("capital", 10000)}

@app.get("/api/room/{code}")
async def get_room(code: str):
    room = rooms.get(code.upper())
    if not room:
        raise HTTPException(404, "Room not found")
    return room_state(room)

@app.websocket("/ws/{code}/{pid}")
async def ws_player(websocket: WebSocket, code: str, pid: str):
    code = code.upper()
    await websocket.accept()
    if code not in connections:
        connections[code] = {}
    connections[code][pid] = websocket
    room = rooms.get(code)
    if room:
        await websocket.send_text(json.dumps({"type": "state", "data": room_state(room)}))
    try:
        while True:
            await websocket.receive_text()
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

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
