# =========================================================
# Authentication & user memory (JSON file storage)
# =========================================================
import json, hashlib
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USER_FILE = DATA_DIR / "arc_users.json"
XP_PER_LEVEL = 100

def hash_password(p):
    return hashlib.sha256((p + "arc_salt_42").encode()).hexdigest()

def load_users():
    if USER_FILE.exists():
        try: return json.load(open(USER_FILE))
        except: return []
    return []

def save_users(users):
    json.dump(users, open(USER_FILE, "w"), indent=2)

def get_user(u):
    for x in load_users():
        if x["username"] == u: return x
    return None

def create_user(u, p, role="user"):
    if get_user(u): raise ValueError("Username exists")
    users = load_users()
    users.append({"username": u, "password_hash": hash_password(p),
                  "role": role, "level": 1, "xp": 0, "badges": [],
                  "created": datetime.now().isoformat()})
    save_users(users)
    return users[-1]

def authenticate(u, p):
    user = get_user(u)
    if user and user["password_hash"] == hash_password(p):
        return user
    return None

def xp_for_level(lvl):
    return lvl * XP_PER_LEVEL

def add_xp(username, amount):
    user = get_user(username)
    if not user: return False
    user["xp"] += amount
    old = user["level"]
    while user["xp"] >= xp_for_level(user["level"]):
        user["xp"] -= xp_for_level(user["level"])
        user["level"] += 1
    if user["level"] > old:
        badge = f"level_{user['level']}"
        if user["level"] % 5 == 0 and badge not in user["badges"]:
            user["badges"].append(badge)
        update_users = load_users()
        for u in update_users:
            if u["username"] == username:
                u.update(user)
                break
        save_users(update_users)
        return True
    return False

def load_memory(username):
    path = DATA_DIR / f"{username}_arc_memory.json"
    if path.exists():
        try: return json.load(open(path, "r", encoding="utf-8"))
        except: pass
    return {"designs": [], "concepts": [], "logs": []}

def save_memory(username, mem):
    json.dump(mem, open(DATA_DIR / f"{username}_arc_memory.json", "w", encoding="utf-8"), indent=2)

def log_event(username, mem, msg):
    mem["logs"].append({"time": datetime.now().isoformat(), "msg": msg})
    save_memory(username, mem)