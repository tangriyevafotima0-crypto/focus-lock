#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║          FocusLock  v4.0  —  UFQ Productivity System        ║
║  Focus | Tasks | YouTube | Journal | Vault | AI | Planning  ║
╚══════════════════════════════════════════════════════════════╝
"""

# ════════════════════════════════════════════════════════
#  IMPORTS
# ════════════════════════════════════════════════════════

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading, time, os, sys, json, re, random
import subprocess, atexit, ctypes, hashlib, base64
import urllib.request, urllib.error
from datetime import datetime

# ════════════════════════════════════════════════════════
#  PATHS
# ════════════════════════════════════════════════════════

if getattr(sys, 'frozen', False):
    APP_DIR  = os.path.dirname(sys.executable)
    APP_PATH = sys.executable
else:
    APP_DIR  = os.path.dirname(os.path.abspath(__file__))
    APP_PATH = os.path.abspath(__file__)

CFG_FILE    = os.path.join(APP_DIR, "fl_config.json")
TASKS_FILE  = os.path.join(APP_DIR, "fl_tasks.json")
JOUR_FILE   = os.path.join(APP_DIR, "fl_journal.json")
NOTES_FILE  = os.path.join(APP_DIR, "fl_notes.enc")
LOG_FILE    = os.path.join(APP_DIR, "fl_log.txt")
HOSTS_FILE  = r"C:\Windows\System32\drivers\etc\hosts"
HOSTS_BK    = os.path.join(APP_DIR, ".fl_hosts_bk")

# ════════════════════════════════════════════════════════
#  COLORS
# ════════════════════════════════════════════════════════

C = {
    'bg':    '#07070f', 'card':  '#0d0d1a', 'card2': '#111122',
    'inp':   '#141426', 'brd':   '#1e1e38', 'hov':   '#1a1a32',
    'acc':   '#6d28d9', 'acc2':  '#8b5cf6', 'acc3':  '#a78bfa',
    'grn':   '#10b981', 'grn2':  '#059669', 'grn3':  '#d1fae5',
    'red':   '#ef4444', 'red2':  '#dc2626', 'redfg': '#fee2e2',
    'yel':   '#f59e0b', 'yel2':  '#d97706', 'yelfg': '#fef3c7',
    'blu':   '#3b82f6', 'blu2':  '#2563eb',
    'txt':   '#f0f0ff', 'sub':   '#6b6b90', 'mut':   '#2e2e50',
    'wht':   '#ffffff',
}

# ════════════════════════════════════════════════════════
#  BLOCKED SITES  (YouTube removed — yt-dlp uchun)
# ════════════════════════════════════════════════════════

BLOCKED = [
    "instagram.com","www.instagram.com",
    "tiktok.com","www.tiktok.com",
    "m.tiktok.com",
    "facebook.com","www.facebook.com","fb.com","m.facebook.com",
    "snapchat.com","www.snapchat.com",
    "twitter.com","www.twitter.com","x.com","www.x.com",
    "reddit.com","www.reddit.com","old.reddit.com",
    "twitch.tv","www.twitch.tv",
    "pinterest.com","www.pinterest.com",
    "vk.com","www.vk.com","ok.ru","www.ok.ru",
    "9gag.com","www.9gag.com","buzzfeed.com",
    "pornhub.com","www.pornhub.com","xvideos.com","www.xvideos.com",
    "xnxx.com","www.xnxx.com","xhamster.com","www.xhamster.com",
    "redtube.com","youporn.com","spankbang.com",
    "livejasmin.com","chaturbate.com","stripchat.com",
    "cam4.com","camsoda.com","bongacams.com",
]

# ════════════════════════════════════════════════════════
#  MOTIVATIONAL QUOTES
# ════════════════════════════════════════════════════════

QUOTES = [
    ("🛡️","HIMOYALANGAN!",
     "{date} sanada eng xavfli chalg'ituvchidan\nqutulgansan! Endi orqaga qaytmaysan! 💪"),
    ("⚡","MUHIM ESLATMA!",
     "Sen PRODUCT bo'lib qo'lasan!\nSocial mediani entertainment uchun\nishlatayotgan bo'lsang — STOP! 🚫"),
    ("🔥","FOCUS ZONE",
     "Har bir o'tgan daqiqa sening\nkelajagingga investitsiya!\nChalg'ima — davom et! 🚀"),
    ("🏆","G'OLIBLAR FIKRI",
     "Deep Work > Shallow Scroll!\nBugun siz g'olib bo'lyapsiz!\nTo'xtamang! 💎"),
    ("🚀","COMPOUND EFFECT",
     "Har bir soatlik FOCUS\n= Kelajakdagi ulkan natija!\nCompound Effect ishlayapti! 📈"),
    ("💎","DISCIPLINE = FREEDOM",
     "Muvaffaqiyatli odamlar hamma\nnarsani ham ko'rmaydi.\nSen to'g'ri tanlov qilding! ✅"),
    ("🎯","MISSION MODE",
     "TikTok: 30 sekund mazza.\nSening MISSIONINGIZ: Butun umr.\nQaysi biri muhimroq? 🤔"),
    ("⏳","VAQT OLTIN!",
     "Hozir o'tkazilayotgan har bir soat\nkelajakdagi sen uchun sovg'a!\nBugun o'zgarish boshlanadi! 🌟"),
]

# ════════════════════════════════════════════════════════
#  DEFAULT CONFIG
# ════════════════════════════════════════════════════════

DEF_CFG = {
    "password":       "UFQ2024",
    "vault_pw_hash":  hashlib.sha256("VAULT2024".encode()).hexdigest(),
    "notif_min":      15,
    "pomo_work":      25,
    "pomo_break":     5,
    "block_sites":    True,
    "dl_path":        os.path.join(os.path.expanduser("~"), "Downloads"),
    "ai_api_key":     "",
    "ai_model":       "claude-haiku-4-5-20251001",
}

# ════════════════════════════════════════════════════════
#  ENCRYPTION  (PBKDF2 + XOR stream)
# ════════════════════════════════════════════════════════

def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)

def vault_encrypt(data: dict, password: str) -> str:
    raw   = json.dumps(data, ensure_ascii=False).encode('utf-8')
    salt  = os.urandom(32)
    key   = _derive_key(password, salt)
    # Extend key to cover full data length
    full_key = b''
    seed = key
    while len(full_key) < len(raw):
        seed = hashlib.sha256(seed).digest()
        full_key += seed
    full_key = full_key[:len(raw)]
    enc = bytes(a ^ b for a, b in zip(raw, full_key))
    return base64.urlsafe_b64encode(salt + enc).decode('ascii')

def vault_decrypt(enc_str: str, password: str) -> dict:
    raw   = base64.urlsafe_b64decode(enc_str.encode('ascii'))
    salt  = raw[:32]
    enc   = raw[32:]
    key   = _derive_key(password, salt)
    full_key = b''
    seed = key
    while len(full_key) < len(enc):
        seed = hashlib.sha256(seed).digest()
        full_key += seed
    full_key = full_key[:len(enc)]
    plain = bytes(a ^ b for a, b in zip(enc, full_key))
    return json.loads(plain.decode('utf-8'))

def pw_hash(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

# ════════════════════════════════════════════════════════
#  UTILITY
# ════════════════════════════════════════════════════════

def is_admin():
    try:    return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except: return False

def req_admin():
    if not is_admin():
        try:
            exe  = sys.executable
            args = " ".join(f'"{a}"' for a in sys.argv)
            ret  = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", exe, args, None, 1)
            if int(ret) > 32:
                sys.exit(0)
        except Exception:
            pass

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def log(msg):
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass

def fmt_time(secs):
    secs = max(0, int(secs))
    h, r = divmod(secs, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def now_str():  return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def date_str(): return datetime.now().strftime("%d.%m.%Y")

def register_startup():
    try:
        import winreg
        cmd = (f'"{APP_PATH}"' if getattr(sys,'frozen',False) else
               f'"{sys.executable.replace("python.exe","pythonw.exe")}" "{APP_PATH}"')
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "FocusLock", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(k)
    except Exception as e:
        log(f"Startup: {e}")

def block_sites():
    if not is_admin():
        log("No admin — skip blocking")
        return False
    try:
        with open(HOSTS_FILE,'r',encoding='utf-8',errors='ignore') as f:
            orig = f.read()
        with open(HOSTS_BK,'w',encoding='utf-8') as f:
            f.write(orig)
        clean = re.sub(r'\n?# ==FL_START==.*?# ==FL_END==\n?',
                       '', orig, flags=re.DOTALL)
        block_str = "\n# ==FL_START==\n"
        for s in BLOCKED:
            block_str += f"0.0.0.0  {s}\n"
        block_str += "# ==FL_END==\n"
        with open(HOSTS_FILE,'w',encoding='utf-8') as f:
            f.write(clean + block_str)
        subprocess.run(["ipconfig","/flushdns"],
                       capture_output=True, creationflags=0x08000000)
        log(f"Blocked {len(BLOCKED)} sites")
        return True
    except Exception as e:
        log(f"Block error: {e}")
        return False

def unblock_sites():
    try:
        if os.path.exists(HOSTS_BK):
            with open(HOSTS_BK,'r',encoding='utf-8') as f:
                orig = f.read()
            with open(HOSTS_FILE,'w',encoding='utf-8') as f:
                f.write(orig)
            try: os.remove(HOSTS_BK)
            except: pass
        else:
            with open(HOSTS_FILE,'r',encoding='utf-8',errors='ignore') as f:
                content = f.read()
            content = re.sub(r'\n?# ==FL_START==.*?# ==FL_END==\n?',
                             '', content, flags=re.DOTALL)
            with open(HOSTS_FILE,'w',encoding='utf-8') as f:
                f.write(content)
        subprocess.run(["ipconfig","/flushdns"],
                       capture_output=True, creationflags=0x08000000)
        log("Sites unblocked")
    except Exception as e:
        log(f"Unblock error: {e}")

def do_shutdown():
    unblock_sites()
    try: subprocess.Popen(["shutdown","/s","/t","5"])
    except Exception: pass

# ════════════════════════════════════════════════════════
#  DATA MANAGERS
# ════════════════════════════════════════════════════════

class ConfigMgr:
    def __init__(self):
        self.data = {**DEF_CFG, **load_json(CFG_FILE, {})}
    def get(self, k, d=None):
        return self.data.get(k, d)
    def set(self, k, v):
        self.data[k] = v
        save_json(CFG_FILE, self.data)
    def save(self):
        save_json(CFG_FILE, self.data)

class TaskMgr:
    def __init__(self):
        self.sessions = load_json(TASKS_FILE, [])
        self.cur      = None

    def new(self, goal="", hours=0):
        self.cur = {
            "session_id":  datetime.now().strftime("%Y%m%d_%H%M%S"),
            "date":        datetime.now().strftime("%Y-%m-%d"),
            "start_time":  now_str(),
            "hours":       hours,
            "goal":        goal,
            "tasks":       [],
        }

    def add(self, text):
        if self.cur and text.strip():
            self.cur["tasks"].append({
                "text":    text.strip(),
                "done":    False,
                "added":   now_str(),
                "done_at": None,
            })
            self._save()

    def complete(self, i):
        if self.cur and 0 <= i < len(self.cur["tasks"]):
            t = self.cur["tasks"][i]
            t["done"]    = True
            t["done_at"] = now_str()
            self._save()

    def uncomplete(self, i):
        if self.cur and 0 <= i < len(self.cur["tasks"]):
            t = self.cur["tasks"][i]
            t["done"]    = False
            t["done_at"] = None
            self._save()

    def end(self):
        if self.cur:
            self.cur["end_time"] = now_str()
            done  = sum(1 for t in self.cur["tasks"] if t["done"])
            total = len(self.cur["tasks"])
            self.cur["summary"] = f"{done}/{total}"
            self.sessions.append(self.cur)
            save_json(TASKS_FILE, self.sessions)
            self.cur = None

    def _save(self):
        data = self.sessions + ([self.cur] if self.cur else [])
        save_json(TASKS_FILE, data)

class JournalMgr:
    def __init__(self):
        self.entries = load_json(JOUR_FILE, [])

    def add(self, content, goal="", hours=0):
        if not content.strip():
            return False
        e = {
            "id":       len(self.entries) + 1,
            "datetime": now_str(),
            "date":     datetime.now().strftime("%Y-%m-%d"),
            "time":     datetime.now().strftime("%H:%M"),
            "hours":    hours,
            "goal":     goal,
            "content":  content.strip(),
        }
        self.entries.append(e)
        save_json(JOUR_FILE, self.entries)
        log(f"Journal #{e['id']} saved")
        return True

    def recent(self, n=5):
        return self.entries[-n:]

class VaultMgr:
    def __init__(self):
        self._notes = None
        self._pw    = None

    def unlock(self, password):
        """Unlock vault, returns True/False."""
        if not os.path.exists(NOTES_FILE):
            self._pw    = password
            self._notes = {"notes": [], "plans": []}
            return True
        try:
            with open(NOTES_FILE, 'r', encoding='ascii') as f:
                enc = f.read().strip()
            self._notes = vault_decrypt(enc, password)
            self._pw    = password
            return True
        except Exception:
            return False

    def lock(self):
        self._save()
        self._notes = None
        self._pw    = None

    def is_open(self):
        return self._notes is not None

    def add_note(self, title, category, content):
        n = {
            "id":       len(self._notes["notes"]) + 1,
            "title":    title,
            "category": category,
            "content":  content,
            "created":  now_str(),
            "updated":  now_str(),
        }
        self._notes["notes"].append(n)
        self._save()
        return n["id"]

    def update_note(self, idx, title, category, content):
        if 0 <= idx < len(self._notes["notes"]):
            n = self._notes["notes"][idx]
            n["title"]   = title
            n["category"]= category
            n["content"] = content
            n["updated"] = now_str()
            self._save()

    def delete_note(self, idx):
        if 0 <= idx < len(self._notes["notes"]):
            self._notes["notes"].pop(idx)
            self._save()

    def get_notes(self):
        return self._notes.get("notes", []) if self._notes else []

    def save_plan(self, title, content):
        p = {"title": title, "content": content, "saved": now_str()}
        self._notes.setdefault("plans", []).append(p)
        self._save()

    def get_plans(self):
        return self._notes.get("plans", []) if self._notes else []

    def _save(self):
        if self._notes and self._pw:
            enc = vault_encrypt(self._notes, self._pw)
            with open(NOTES_FILE, 'w', encoding='ascii') as f:
                f.write(enc)

# ════════════════════════════════════════════════════════
#  AI CALLS  (urllib — hech qanday paket shart emas)
# ════════════════════════════════════════════════════════

def ai_call(api_key: str, messages: list, system: str = "",
            model: str = "claude-haiku-4-5-20251001",
            max_tokens: int = 1500) -> str:
    """Claude API ga so'rov yuborish (bloklangan — threadda chaqiring)."""
    if not api_key:
        return ("❌ API kalit kiritilmagan.\n\n"
                "Vault → AI tab → ⚙ Sozlamalar → API kalitingizni kiriting.\n"
                "Kalit olish: https://console.anthropic.com")

    payload = {
        "model":      model,
        "max_tokens": max_tokens,
        "messages":   messages,
    }
    if system:
        payload["system"] = system

    data = json.dumps(payload).encode('utf-8')
    req  = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data, method='POST')
    req.add_header('Content-Type',     'application/json')
    req.add_header('anthropic-version','2023-06-01')
    req.add_header('x-api-key',        api_key)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['content'][0]['text']
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            err = json.loads(body)['error']['message']
        except Exception:
            err = body[:200]
        return f"❌ API xato ({e.code}): {err}"
    except Exception as e:
        return f"❌ Ulanish xatosi: {e}"

# ════════════════════════════════════════════════════════
#  YT-DLP  AUTO-INSTALL + DOWNLOAD
# ════════════════════════════════════════════════════════

def ensure_ytdlp() -> bool:
    try:
        import yt_dlp   # noqa
        return True
    except ImportError:
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install',
                 'yt-dlp', '--quiet', '--disable-pip-version-check'],
                check=True, capture_output=True, timeout=120)
            return True
        except Exception as e:
            log(f"yt-dlp install failed: {e}")
            return False

def yt_download(url: str, fmt: str, out_dir: str,
                progress_cb, status_cb, done_cb, error_cb):
    """yt-dlp download (threadda chaqiriladi)."""
    try:
        import yt_dlp

        ydl_opts = {
            'quiet':           True,
            'no_warnings':     True,
            'outtmpl':         os.path.join(out_dir, '%(title)s.%(ext)s'),
        }

        if fmt == "audio":
            ydl_opts.update({
                'format':         'bestaudio/best',
                'postprocessors': [{
                    'key':            'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif fmt == "1080":
            ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        elif fmt == "720":
            ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        elif fmt == "480":
            ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
        else:
            ydl_opts['format'] = 'best'

        def progress_hook(d):
            if d['status'] == 'downloading':
                total     = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                downloaded= d.get('downloaded_bytes', 0)
                pct       = min(99.0, downloaded / total * 100)
                speed     = d.get('speed')
                spd_str   = (f"{speed/1_048_576:.1f} MB/s"
                             if speed and speed > 1_048_576 else
                             f"{speed/1024:.0f} KB/s" if speed else "")
                progress_cb(pct)
                status_cb(f"⬇  {pct:.0f}%  {spd_str}")
            elif d['status'] == 'finished':
                progress_cb(99)
                status_cb("⚙  Qayta ishlanmoqda...")

        ydl_opts['progress_hooks'] = [progress_hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Video')

        progress_cb(100)
        done_cb(title)

    except Exception as e:
        error_cb(str(e))

# ════════════════════════════════════════════════════════
#  UI HELPERS
# ════════════════════════════════════════════════════════

def mk_btn(parent, text, cmd, bg, fg=C['wht'],
           fs=10, bold=True, px=16, py=8):
    fw  = 'bold' if bold else 'normal'
    hbg = {
        C['acc']:  C['acc2'], C['grn']:  C['grn2'],
        C['red']:  C['red2'], C['inp']:  C['hov'],
        C['mut']:  C['hov'],  C['card']: C['hov'],
        C['blu']:  C['blu2'],
    }.get(bg, bg)
    b = tk.Button(parent, text=text, command=cmd,
                  font=('Segoe UI', fs, fw), bg=bg, fg=fg,
                  activebackground=hbg, activeforeground=fg,
                  relief='flat', padx=px, pady=py,
                  cursor='hand2', bd=0)
    b.bind('<Enter>', lambda e: b.config(bg=hbg))
    b.bind('<Leave>', lambda e: b.config(bg=bg))
    return b

def mk_entry(parent, var, **kw):
    brd = tk.Frame(parent, bg=C['brd'], padx=1, pady=1)
    e   = tk.Entry(brd, textvariable=var,
                   font=kw.get('font', ('Segoe UI', 11)),
                   bg=C['inp'], fg=C['txt'],
                   insertbackground=C['acc3'],
                   relief='flat',
                   width=kw.get('width', 30),
                   justify=kw.get('justify', 'left'),
                   show=kw.get('show', ''))
    e.pack(ipady=kw.get('ipy', 8), ipadx=kw.get('ipx', 6))
    return brd, e

def mk_label(parent, text, fs=11, fg=None, bold=False, **kw):
    return tk.Label(parent, text=text,
                    font=('Segoe UI', fs, 'bold' if bold else 'normal'),
                    bg=kw.get('bg', C['bg']),
                    fg=fg or C['txt'], **{k: v for k,v in kw.items()
                                          if k not in ('bg',)})

def ttk_style():
    s = ttk.Style()
    s.theme_use('clam')
    s.configure('FL.TNotebook',
                 background=C['card'], bordercolor=C['brd'],
                 tabmargins=[2,4,2,0])
    s.configure('FL.TNotebook.Tab',
                 background=C['inp'], foreground=C['sub'],
                 font=('Segoe UI',9,'bold'), padding=[10,6])
    s.map('FL.TNotebook.Tab',
          background=[('selected', C['acc']), ('active', C['hov'])],
          foreground=[('selected', C['wht']), ('active', C['txt'])])
    s.configure("FL.Horizontal.TProgressbar",
                 troughcolor=C['inp'], background=C['acc'],
                 lightcolor=C['acc2'], darkcolor=C['acc'])
    s.configure("G.Horizontal.TProgressbar",
                 troughcolor=C['inp'], background=C['grn'],
                 lightcolor=C['grn2'], darkcolor=C['grn'])
    return s

# ════════════════════════════════════════════════════════
#  MINI CHART  (Canvas-da, matplotlib kerak emas)
# ════════════════════════════════════════════════════════

def draw_bar_chart(canvas, data: list, width: int, height: int,
                   title="", bar_color=C['acc'], label_color=C['sub']):
    """data = [(label, value), ...]"""
    canvas.delete('all')
    if not data:
        canvas.create_text(width//2, height//2,
                           text="Ma'lumot yo'q",
                           fill=C['sub'], font=('Segoe UI',10))
        return

    pad_l, pad_r, pad_t, pad_b = 42, 12, 28, 40
    chart_w = width  - pad_l - pad_r
    chart_h = height - pad_t - pad_b

    max_val = max(v for _, v in data) or 1
    n = len(data)
    bar_w = max(6, (chart_w - (n-1)*4) // n)
    total_w = n * bar_w + (n-1)*4

    # Background
    canvas.create_rectangle(0, 0, width, height, fill=C['card'], outline='')

    if title:
        canvas.create_text(width//2, 14, text=title,
                           fill=C['sub'], font=('Segoe UI',8))

    # Y-axis grid lines
    for ratio in (0.25, 0.5, 0.75, 1.0):
        y = pad_t + chart_h - int(chart_h * ratio)
        canvas.create_line(pad_l-4, y, pad_l+total_w+4, y,
                           fill=C['mut'], dash=(3,4))
        val = max_val * ratio
        lbl = f"{val:.0f}h" if val >= 1 else f"{val*60:.0f}m"
        canvas.create_text(pad_l-6, y, text=lbl,
                           fill=label_color, font=('Segoe UI',7),
                           anchor='e')

    # Bars
    for i, (label, val) in enumerate(data):
        x0 = pad_l + i * (bar_w + 4)
        x1 = x0 + bar_w
        bar_h2 = max(2, int(chart_h * val / max_val))
        y0 = pad_t + chart_h - bar_h2
        y1 = pad_t + chart_h

        # Bar shadow
        canvas.create_rectangle(x0+2, y0+2, x1+2, y1+2,
                                 fill=C['mut'], outline='')
        # Bar
        canvas.create_rectangle(x0, y0, x1, y1,
                                 fill=bar_color, outline='')
        # Value on top
        if val > 0:
            txt = f"{val:.1f}h" if val >= 1 else f"{int(val*60)}m"
            canvas.create_text((x0+x1)//2, y0-5, text=txt,
                                fill=C['acc3'], font=('Segoe UI',7))
        # Label
        canvas.create_text((x0+x1)//2, y1+8, text=label[:4],
                            fill=label_color, font=('Segoe UI',7))

# ════════════════════════════════════════════════════════
#  MAIN APP
# ════════════════════════════════════════════════════════

class FocusLock:

    def __init__(self):
        self.cfg   = ConfigMgr()
        self.tm    = TaskMgr()
        self.jm    = JournalMgr()
        self.vm    = VaultMgr()

        # Session state
        self.running    = False
        self.paused     = False
        self.end_ts     = 0.0
        self.total_s    = 0.0
        self.s_hours    = 0.0
        self.s_goal     = ""
        self.pomo       = False
        self.pomo_ph    = "work"
        self.pomo_end   = 0.0
        self.p_start    = 0.0
        self._pending   = []    # tasks before session
        self._notifs    = []
        self._task_vars = []

        atexit.register(unblock_sites)
        register_startup()

        self.root = tk.Tk()
        self.root.title("FocusLock")
        self.root.configure(bg=C['bg'])
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        ttk_style()

        log("=== FocusLock v4.0 started ===")
        self.cfg.save()

        self._screen_lock()
        self.root.mainloop()

    # ─── helpers ───────────────────────────────────────

    def _clear(self):
        for w in self.root.winfo_children():
            try: w.destroy()
            except: pass

    def _fullscreen(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)

    # ════════════════════════════════════════════════════
    #  SCREEN 1: LOCK
    # ════════════════════════════════════════════════════

    def _screen_lock(self):
        self._clear()
        self._fullscreen()
        self.root.bind('<Alt-F4>', lambda e: "break")
        self.root.bind('<Escape>', lambda e: "break")
        self.root.bind('<Return>', lambda e: self._check_pw())

        c = tk.Frame(self.root, bg=C['bg'])
        c.place(relx=.5, rely=.5, anchor='center')

        tk.Label(c, text="🔒",
                 font=('Segoe UI Emoji',64), bg=C['bg'], fg=C['acc3']).pack()
        mk_label(c,"FocusLock",38,bold=True).pack()
        mk_label(c,"UFQ  Productivity  System  v4.0",
                 12, C['sub']).pack(pady=(2,0))
        tk.Frame(c, bg=C['acc'], height=2, width=360).pack(pady=26)
        mk_label(c,"Parolni kiriting",12, C['sub']).pack(pady=(0,8))

        brd = tk.Frame(c, bg=C['acc2'], padx=1, pady=1)
        brd.pack()
        self._pw_var = tk.StringVar()
        self._pw_ent = tk.Entry(brd, textvariable=self._pw_var,
                                show='●', font=('Consolas',18),
                                bg=C['inp'], fg=C['txt'],
                                insertbackground=C['acc3'],
                                relief='flat', width=26, justify='center')
        self._pw_ent.pack(ipady=12, ipadx=8)
        self._pw_ent.focus_set()

        self._pw_err = mk_label(c,"",12,C['red'])
        self._pw_err.pack(pady=6)

        mk_btn(c,"  KIRISH  →",self._check_pw,
               C['acc'],fs=13,px=40,py=14).pack(pady=4)

        self._clk = mk_label(c,"",10,C['mut'])
        self._clk.pack(pady=(22,0))
        self._tick_clock()

        mk_label(c,"⚠  Noto'g'ri parol → kompyuter darhol o'chadi",
                 10, C['mut']).pack(pady=(4,0))

    def _tick_clock(self):
        if self._clk.winfo_exists():
            self._clk.config(
                text=datetime.now().strftime("%A, %d %B %Y    %H:%M:%S"))
            self.root.after(1000, self._tick_clock)

    def _check_pw(self):
        if self._pw_var.get() == self.cfg.get('password'):
            log("Password OK")
            self._screen_tasks()
        else:
            log("WRONG PW — shutdown")
            self._pw_err.config(
                text="❌  Noto'g'ri parol!  Kompyuter o'chirilmoqda...")
            self._pw_ent.config(state='disabled')
            self.root.update()
            for i in (3,2,1):
                self._pw_err.config(
                    text=f"❌  Noto'g'ri parol!  {i} soniyada o'chadi...")
                self.root.update()
                time.sleep(1)
            do_shutdown()
            self.root.after(7000, self.root.destroy)

    # ════════════════════════════════════════════════════
    #  SCREEN 2: TASKS INPUT
    # ════════════════════════════════════════════════════

    def _screen_tasks(self):
        self._clear()
        self._fullscreen()
        self.root.unbind('<Return>')
        self.root.bind('<Alt-F4>', lambda e: "break")
        self.root.bind('<Escape>', lambda e: "break")
        self._pending = []

        c = tk.Frame(self.root, bg=C['bg'])
        c.place(relx=.5, rely=.5, anchor='center')

        tk.Label(c, text="📋",
                 font=('Segoe UI Emoji',52), bg=C['bg'], fg=C['acc3']).pack()
        mk_label(c,"Bugungi Vazifalar",28,bold=True).pack()
        mk_label(c,"Ixtiyoriy — o'tkazib yuborish mumkin",
                 12, C['sub']).pack(pady=(2,0))
        tk.Frame(c, bg=C['acc'], height=2, width=500).pack(pady=20)

        # Input row
        row = tk.Frame(c, bg=C['bg'])
        row.pack()
        self._te_var = tk.StringVar()
        brd, te = mk_entry(row, self._te_var, width=38, ipy=10)
        brd.pack(side='left')
        te.focus_set()

        def add_t(e=None):
            t = self._te_var.get().strip()
            if t:
                self._pending.append(t)
                self._te_var.set("")
                refresh()
                te.focus_set()

        te.bind('<Return>', add_t)
        mk_btn(row,"+ Qo'sh",add_t,C['acc'],
               fs=11,px=16,py=10).pack(side='left',padx=(8,0))

        # List frame
        lf = tk.Frame(c, bg=C['card'], width=500, height=220)
        lf.pack(pady=12)
        lf.pack_propagate(False)
        cv = tk.Canvas(lf, bg=C['card'], highlightthickness=0)
        sb = tk.Scrollbar(lf, orient='vertical', command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        cv.pack(side='left', fill='both', expand=True)
        inner = tk.Frame(cv, bg=C['card'])
        cv.create_window((0,0), window=inner, anchor='nw')
        inner.bind('<Configure>',
                   lambda e: cv.configure(scrollregion=cv.bbox('all')))

        def refresh():
            for w in inner.winfo_children(): w.destroy()
            if not self._pending:
                mk_label(inner,"Hali vazifa qo'shilmagan",
                         10, C['mut'], bg=C['card']).pack(pady=20)
                return
            for i, t in enumerate(self._pending):
                r2 = tk.Frame(inner, bg=C['card'])
                r2.pack(fill='x', padx=12, pady=3)
                mk_label(r2,f"{i+1}.",10,C['sub'],
                         bg=C['card']).pack(side='left',padx=4)
                mk_label(r2,t,11,bg=C['card']).pack(
                    side='left',fill='x',expand=True)
                idx = i
                mk_btn(r2,"✕",
                       lambda ii=idx: (self._pending.pop(ii), refresh()),
                       C['card'],fg=C['red'],fs=9,px=4,py=2).pack(
                           side='right',padx=4)

        refresh()
        mk_label(c,"↵ Enter — vazifa qo'shish",9,C['mut']).pack()

        br = tk.Frame(c, bg=C['bg'])
        br.pack(pady=18)
        mk_btn(br,"O'TKAZIB YUBORISH",self._screen_duration,
               C['mut'],fs=11,px=22,py=12).pack(side='left',padx=8)
        mk_btn(br,"  ✅  DAVOM ETISH  →",self._screen_duration,
               C['grn'],fs=12,px=28,py=13).pack(side='left',padx=8)

    # ════════════════════════════════════════════════════
    #  SCREEN 3: DURATION
    # ════════════════════════════════════════════════════

    def _screen_duration(self):
        self._clear()
        self._fullscreen()
        self.root.bind('<Alt-F4>', lambda e: "break")
        self.root.bind('<Return>', lambda e: self._start())

        c = tk.Frame(self.root, bg=C['bg'])
        c.place(relx=.5, rely=.5, anchor='center')

        tk.Label(c, text="⚡",
                 font=('Segoe UI Emoji',48), bg=C['bg'], fg=C['yel']).pack()
        mk_label(c,"Ish Sessiyasi",30,bold=True).pack()
        mk_label(c,"Vaqt va maqsadingizni belgilang",
                 12, C['sub']).pack(pady=(2,0))
        tk.Frame(c, bg=C['acc'], height=2, width=420).pack(pady=22)

        mk_label(c,"Necha soat ishlamoqchisiz?",13,C['sub']).pack()
        brd1 = tk.Frame(c, bg=C['acc2'], padx=1, pady=1)
        brd1.pack(pady=8)
        self._h_var = tk.StringVar(value="2")
        h_ent = tk.Entry(brd1, textvariable=self._h_var,
                         font=('Consolas',34,'bold'),
                         bg=C['inp'], fg=C['acc3'],
                         insertbackground=C['acc3'],
                         relief='flat', width=8, justify='center')
        h_ent.pack(ipady=10)
        h_ent.focus_set()
        mk_label(c,"soat  (masalan: 1   1.5   3)",
                 11, C['mut']).pack()

        mk_label(c,"\nBugungi maqsad (ixtiyoriy):",
                 13, C['sub']).pack()
        self._g_var = tk.StringVar()
        brd2, _ = mk_entry(c, self._g_var, width=42, ipy=9)
        brd2.pack(pady=6)

        opt = tk.Frame(c, bg=C['bg'])
        opt.pack(pady=10)
        self._pomo_v  = tk.BooleanVar(value=False)
        self._blk_v   = tk.BooleanVar(value=self.cfg.get('block_sites', True))

        for text, var in [
            ("🍅  Pomodoro rejimi  (25 min ish / 5 min tanaffus)", self._pomo_v),
            ("🚫  Ijtimoiy tarmoq va 18+ saytlarni bloklash", self._blk_v),
        ]:
            tk.Checkbutton(opt, text=f"  {text}", variable=var,
                           font=('Segoe UI',12), bg=C['bg'], fg=C['sub'],
                           activebackground=C['bg'], selectcolor=C['inp'],
                           relief='flat', cursor='hand2').pack(
                               pady=3, anchor='w')

        mk_btn(c,"   🚀  ISHNI BOSHLASH   ",self._start,
               C['grn'],fs=14,px=36,py=15).pack(pady=16)
        mk_label(c,"↵ Enter — boshlash",9,C['mut']).pack()

        if self._pending:
            tk.Frame(c, bg=C['brd'], height=1, width=420).pack(pady=12)
            mk_label(c,f"📋  {len(self._pending)} ta vazifa qo'shilgan",
                     11, C['acc3']).pack()

    def _start(self):
        try:
            h = float(self._h_var.get().replace(',','.'))
            if h <= 0 or h > 24: raise ValueError
        except ValueError:
            messagebox.showerror("Xato",
                "To'g'ri soat kiriting!\nMasalan: 1  yoki  1.5",
                parent=self.root)
            return
        goal     = self._g_var.get().strip()
        do_block = self._blk_v.get()
        self.cfg.set('block_sites', do_block)

        self.tm.new(goal=goal, hours=h)
        for t in self._pending:
            self.tm.add(t)

        self.s_hours  = h
        self.s_goal   = goal
        self.pomo     = self._pomo_v.get()
        self.running  = True
        self.paused   = False
        self.total_s  = h * 3600
        self.end_ts   = time.time() + self.total_s
        self.pomo_ph  = "work"
        self.pomo_end = time.time() + self.cfg.get('pomo_work',25) * 60

        if do_block: block_sites()
        log(f"Session: {h}h goal='{goal}' pomo={self.pomo}")

        self._screen_dashboard()
        threading.Thread(target=self._timer_loop, daemon=True).start()
        threading.Thread(target=self._notif_loop, daemon=True).start()

    # ════════════════════════════════════════════════════
    #  SCREEN 4: DASHBOARD  (tabbed corner widget)
    # ════════════════════════════════════════════════════

    def _screen_dashboard(self):
        self._clear()
        sw = self.root.winfo_screenwidth()
        W, H = 500, 680
        self.root.geometry(f"{W}x{H}+{sw-W-12}+10")
        self.root.attributes('-fullscreen', False)
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)
        self.root.configure(bg=C['card'])
        self.root.protocol("WM_DELETE_WINDOW", self._close_guard)
        self.root.unbind('<Return>')
        self.root.unbind('<Alt-F4>')
        self.root.unbind('<Escape>')

        # Header
        hdr = tk.Frame(self.root, bg=C['acc'], pady=7)
        hdr.pack(fill='x')
        tk.Label(hdr, text="🔒  FocusLock  •  FOCUS MODE ON",
                 font=('Segoe UI',11,'bold'),
                 bg=C['acc'], fg=C['wht']).pack()

        # Notebook
        self._nb = ttk.Notebook(self.root, style='FL.TNotebook')
        self._nb.pack(fill='both', expand=True, padx=6, pady=4)

        self._tab_focus    = tk.Frame(self._nb, bg=C['card2'])
        self._tab_tasks    = tk.Frame(self._nb, bg=C['card2'])
        self._tab_yt       = tk.Frame(self._nb, bg=C['card2'])
        self._tab_journal  = tk.Frame(self._nb, bg=C['card2'])

        self._nb.add(self._tab_focus,   text="⏱  Focus")
        self._nb.add(self._tab_tasks,   text="📋  Vazifalar")
        self._nb.add(self._tab_yt,      text="📥  YouTube")
        self._nb.add(self._tab_journal, text="📔  Journal")

        self._build_focus_tab()
        self._build_tasks_tab()
        self._build_yt_tab()
        self._build_journal_tab()

        # Bottom action bar
        bar = tk.Frame(self.root, bg=C['card'], pady=6)
        bar.pack(fill='x', padx=8)

        self._pause_btn = mk_btn(bar,"⏸  Pauza",self._toggle_pause,
                                  C['inp'],fg=C['txt'],fs=9,px=10,py=7)
        self._pause_btn.pack(side='left',expand=True,fill='x',padx=2)

        mk_btn(bar,"🔐  Vault",self._open_vault,
               C['inp'],fg=C['acc3'],fs=9,px=10,py=7).pack(
                   side='left',expand=True,fill='x',padx=2)

        mk_btn(bar,"✔  Tugatish",self._ask_done,
               C['acc'],fs=9,px=10,py=7).pack(
                   side='right',expand=True,fill='x',padx=2)

    # ─── Focus Tab ────────────────────────────────────

    def _build_focus_tab(self):
        p = self._tab_focus
        tk.Frame(p, bg=C['card2'], height=12).pack()

        mk_label(p,"⏱  Qolgan vaqt",9,C['sub'],bg=C['card2']).pack()
        self._timer_lbl = tk.Label(p, text="00:00:00",
                                   font=('Consolas',44,'bold'),
                                   bg=C['card2'], fg=C['acc3'])
        self._timer_lbl.pack()

        self._prog_var = tk.DoubleVar(value=0)
        ttk.Progressbar(p, variable=self._prog_var,
                        maximum=100,
                        style='FL.Horizontal.TProgressbar',
                        length=420).pack(pady=(6,2))
        self._pct_lbl = mk_label(p,"0%  tamamlandi",8,C['mut'],bg=C['card2'])
        self._pct_lbl.pack()

        if self.s_goal:
            gf = tk.Frame(p, bg=C['inp'], padx=12, pady=8)
            gf.pack(fill='x', padx=16, pady=10)
            mk_label(gf,"🎯  Bugungi maqsad:",9,C['sub'],
                     bold=True,bg=C['inp']).pack(anchor='w')
            mk_label(gf,self.s_goal,10,bold=True,bg=C['inp']).pack(
                anchor='w',pady=2)

        if self.pomo:
            self._pomo_lbl = mk_label(p,"🍅  ...",10,C['yel'],
                                       bold=True,bg=C['card2'])
            self._pomo_lbl.pack(pady=4)

        blk_txt = ("✅  Saytlar bloklangan" if self.cfg.get('block_sites')
                   else "⚠  Bloklash o'chirilgan")
        self._status_lbl = mk_label(p, blk_txt, 9,
            C['grn'] if self.cfg.get('block_sites') else C['yel'],
            bg=C['card2'])
        self._status_lbl.pack(pady=(8,2))

        st = datetime.now().strftime("%H:%M")
        et = datetime.fromtimestamp(self.end_ts).strftime("%H:%M")
        mk_label(p,f"Sessiya: {self.s_hours}h  •  {st} → {et}",
                 8,C['mut'],bg=C['card2']).pack()

        self._ticker = mk_label(p,"",8,C['sub'],bg=C['card2'])
        self._ticker.config(wraplength=440, justify='center')
        self._ticker.pack(pady=8)
        self._spin_ticker()

    def _spin_ticker(self):
        if hasattr(self,'_ticker') and self._ticker.winfo_exists():
            q = random.choice(QUOTES)
            self._ticker.config(
                text=f"{q[0]}  {q[2].split(chr(10))[0]}")
            self.root.after(9000, self._spin_ticker)

    # ─── Tasks Tab ────────────────────────────────────

    def _build_tasks_tab(self):
        p = self._tab_tasks
        mk_label(p,"📋  Vazifalar",11,C['acc3'],bold=True,
                 bg=C['card2']).pack(anchor='w',padx=12,pady=(10,4))

        # Scroll area
        outer = tk.Frame(p, bg=C['card2'])
        outer.pack(fill='both', expand=True, padx=8)
        cv = tk.Canvas(outer, bg=C['card2'], highlightthickness=0)
        sb = tk.Scrollbar(outer, orient='vertical', command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        cv.pack(side='left', fill='both', expand=True)
        self._task_inner = tk.Frame(cv, bg=C['card2'])
        cv.create_window((0,0), window=self._task_inner, anchor='nw')
        self._task_inner.bind('<Configure>',
                              lambda e: cv.configure(
                                  scrollregion=cv.bbox('all')))

        self._render_tasks()

        # Add new task input
        add_fr = tk.Frame(p, bg=C['card2'])
        add_fr.pack(fill='x', padx=8, pady=6)
        self._nt_var = tk.StringVar()
        brd = tk.Frame(add_fr, bg=C['brd'], padx=1, pady=1)
        brd.pack(side='left', fill='x', expand=True)
        nt = tk.Entry(brd, textvariable=self._nt_var,
                      font=('Segoe UI',10), bg=C['inp'], fg=C['txt'],
                      insertbackground=C['acc3'], relief='flat')
        nt.pack(fill='x', ipady=6, ipadx=4)

        def _add(e=None):
            t = self._nt_var.get().strip()
            if t:
                self.tm.add(t)
                self._nt_var.set("")
                self._render_tasks()

        nt.bind('<Return>', _add)
        mk_btn(add_fr,"+",_add,C['acc'],
               fs=10,px=10,py=6).pack(side='left',padx=(4,0))

    def _render_tasks(self):
        for w in self._task_inner.winfo_children():
            try: w.destroy()
            except: pass
        self._task_vars = []

        tasks = (self.tm.cur or {}).get("tasks", [])
        if not tasks:
            mk_label(self._task_inner,"Vazifa yo'q — pastda qo'shing",
                     9,C['mut'],bg=C['card2']).pack(pady=12)
            return

        for i, t in enumerate(tasks):
            bv  = tk.BooleanVar(value=t['done'])
            self._task_vars.append(bv)
            idx = i
            row = tk.Frame(self._task_inner, bg=C['card2'])
            row.pack(fill='x', padx=4, pady=2)

            def toggle(ii=idx, var=bv):
                if var.get(): self.tm.complete(ii)
                else:          self.tm.uncomplete(ii)
                self._render_tasks()

            tk.Checkbutton(row, variable=bv, command=toggle,
                           bg=C['card2'], activebackground=C['card2'],
                           selectcolor=C['inp'],
                           relief='flat', cursor='hand2').pack(side='left')

            fc = C['grn2'] if t['done'] else C['txt']
            ff = ('Segoe UI',9,'overstrike') if t['done'] else ('Segoe UI',9)
            lbl = tk.Label(row, text=t['text'], font=ff,
                           bg=C['card2'], fg=fc,
                           wraplength=380, justify='left', cursor='hand2')
            lbl.pack(side='left', fill='x', expand=True)
            lbl.bind('<Button-1>',
                     lambda e, ii=idx, v=bv: (v.set(not v.get()),
                                               toggle(ii, v)))

    # ─── YouTube Tab ──────────────────────────────────

    def _build_yt_tab(self):
        p = self._tab_yt
        p.configure(bg=C['card2'])

        # Auto-install notice
        info_fr = tk.Frame(p, bg=C['inp'], padx=10, pady=6)
        info_fr.pack(fill='x', padx=10, pady=(10,6))
        mk_label(info_fr,
                 "📥  YouTube Video Yuklovchi (yt-dlp)",
                 10, C['acc3'], bold=True, bg=C['inp']).pack(anchor='w')
        mk_label(info_fr,
                 "YouTube BLOKLANMAGAN — bu tab uchun!",
                 8, C['grn'], bg=C['inp']).pack(anchor='w')

        # URL
        mk_label(p,"YouTube URL:",10,C['sub'],bg=C['card2']).pack(
            anchor='w',padx=12,pady=(8,2))
        url_fr = tk.Frame(p, bg=C['card2'])
        url_fr.pack(fill='x', padx=10)
        self._yt_url = tk.StringVar()
        brd = tk.Frame(url_fr, bg=C['brd'], padx=1, pady=1)
        brd.pack(fill='x')
        tk.Entry(brd, textvariable=self._yt_url,
                 font=('Segoe UI',10), bg=C['inp'], fg=C['txt'],
                 insertbackground=C['acc3'], relief='flat').pack(
                     fill='x', ipady=8, ipadx=6)

        # Quality + Path
        opt_fr = tk.Frame(p, bg=C['card2'])
        opt_fr.pack(fill='x', padx=10, pady=8)

        # Quality
        ql = tk.Frame(opt_fr, bg=C['card2'])
        ql.pack(side='left')
        mk_label(ql,"Sifat:",9,C['sub'],bg=C['card2']).pack(anchor='w')
        self._yt_fmt = tk.StringVar(value="720")
        for val, txt in [("1080","1080p HD"),("720","720p"),
                         ("480","480p"),("audio","🎵 MP3")]:
            tk.Radiobutton(ql, text=txt, variable=self._yt_fmt, value=val,
                           font=('Segoe UI',9), bg=C['card2'], fg=C['sub'],
                           activebackground=C['card2'],
                           selectcolor=C['inp'], relief='flat').pack(
                               anchor='w', pady=1)

        # Path
        ph = tk.Frame(opt_fr, bg=C['card2'])
        ph.pack(side='left', padx=(20,0))
        mk_label(ph,"Papka:",9,C['sub'],bg=C['card2']).pack(anchor='w')
        self._yt_path = tk.StringVar(value=self.cfg.get('dl_path',''))
        brd2 = tk.Frame(ph, bg=C['brd'], padx=1, pady=1)
        brd2.pack(fill='x')
        tk.Entry(brd2, textvariable=self._yt_path,
                 font=('Segoe UI',8), bg=C['inp'], fg=C['txt'],
                 insertbackground=C['acc3'], relief='flat',
                 width=22).pack(ipady=5,ipadx=4)

        def choose_dir():
            d = filedialog.askdirectory(parent=self.root,
                                        initialdir=self._yt_path.get())
            if d:
                self._yt_path.set(d)
                self.cfg.set('dl_path', d)

        mk_btn(ph,"📁 Tanlash",choose_dir,C['inp'],
               fg=C['acc3'],fs=8,px=8,py=4).pack(pady=4)

        # Download button
        mk_btn(p,"  ⬇  YUKLAB OLISH  ",self._yt_download_start,
               C['acc'],fs=11,px=24,py=10).pack(pady=6)

        # Progress
        self._yt_prog = tk.DoubleVar(value=0)
        ttk.Progressbar(p, variable=self._yt_prog,
                        maximum=100,
                        style='FL.Horizontal.TProgressbar',
                        length=450).pack(padx=12)
        self._yt_status = mk_label(p,"Yuklash uchun URL kiriting va tugmani bosing",
                                    8, C['sub'], bg=C['card2'])
        self._yt_status.pack(pady=4)

        # History
        mk_label(p,"— So'nggi yuklamalar —",8,C['mut'],
                 bg=C['card2']).pack(pady=(4,2))
        self._yt_hist_fr = tk.Frame(p, bg=C['card2'])
        self._yt_hist_fr.pack(fill='x', padx=12)
        self._yt_history = []

    def _yt_download_start(self):
        url = self._yt_url.get().strip()
        if not url:
            messagebox.showwarning("URL yo'q","YouTube URL kiriting!",
                                   parent=self.root)
            return

        path = self._yt_path.get().strip()
        if not os.path.isdir(path):
            messagebox.showerror("Papka yo'q",
                f"Papka topilmadi:\n{path}", parent=self.root)
            return

        self._yt_prog.set(0)
        self._yt_status.config(text="⚙  yt-dlp tekshirilmoqda...",
                               fg=C['yel'])
        self.root.update()

        def run():
            if not ensure_ytdlp():
                self.root.after(0, lambda: self._yt_status.config(
                    text="❌  yt-dlp o'rnatilmadi! pip check qiling.",
                    fg=C['red']))
                return

            self.root.after(0, lambda: self._yt_status.config(
                text="⬇  Yuklanmoqda...", fg=C['acc3']))

            fmt = self._yt_fmt.get()

            yt_download(
                url=url,
                fmt=fmt,
                out_dir=path,
                progress_cb=lambda p: self.root.after(
                    0, lambda pp=p: self._yt_prog.set(pp)),
                status_cb=lambda s: self.root.after(
                    0, lambda ss=s: self._yt_status.config(
                        text=ss, fg=C['acc3'])),
                done_cb=self._yt_done,
                error_cb=self._yt_error,
            )

        threading.Thread(target=run, daemon=True).start()

    def _yt_done(self, title):
        self._yt_history.append(f"✅  {title[:45]}")
        if len(self._yt_history) > 5:
            self._yt_history = self._yt_history[-5:]

        def update():
            self._yt_prog.set(100)
            self._yt_status.config(
                text=f"✅  Yuklandi: {title[:40]}", fg=C['grn'])
            self._yt_url.set("")
            for w in self._yt_hist_fr.winfo_children(): w.destroy()
            for h in reversed(self._yt_history):
                mk_label(self._yt_hist_fr, h, 8, C['sub'],
                         bg=C['card2']).pack(anchor='w')

        self.root.after(0, update)

    def _yt_error(self, err):
        self.root.after(0, lambda: self._yt_status.config(
            text=f"❌  {err[:80]}", fg=C['red']))
        log(f"yt-dlp error: {err}")

    # ─── Journal Tab ──────────────────────────────────

    def _build_journal_tab(self):
        p = self._tab_journal
        p.configure(bg=C['card2'])

        mk_label(p,
                 f"📔  Journal  —  {datetime.now().strftime('%d %B %Y')}",
                 11, C['acc3'], bold=True, bg=C['card2']).pack(
                     anchor='w', padx=12, pady=(10,4))

        if self.s_goal:
            gf = tk.Frame(p, bg=C['inp'], padx=10, pady=5)
            gf.pack(fill='x', padx=10, pady=(0,6))
            mk_label(gf,f"Maqsad: {self.s_goal}",9,C['sub'],
                     bg=C['inp']).pack(anchor='w')

        # Prompts
        pf = tk.Frame(p, bg=C['card2'])
        pf.pack(fill='x', padx=10, pady=(0,4))
        mk_label(pf,"💡  Tez qo'shish:",8,C['mut'],
                 bg=C['card2']).pack(side='left')
        self._j_ta = None  # will be set below

        def insert_prompt(q):
            if self._j_ta:
                self._j_ta.insert('end', f"\n• {q}\n")
                self._j_ta.see('end')
                self._j_ta.focus_set()

        for q in ["Bugun nima yaxshi bo'ldi?",
                  "Nima chalg'itdi?","Ertaga reja?"]:
            mk_btn(pf, f"+ {q.split('?')[0]}",
                   lambda qq=q: insert_prompt(qq),
                   C['inp'], fg=C['acc3'],
                   fs=7, px=6, py=3).pack(side='left', padx=2)

        # Text area
        brd = tk.Frame(p, bg=C['brd'], padx=1, pady=1)
        brd.pack(fill='both', expand=True, padx=10, pady=4)
        self._j_ta = scrolledtext.ScrolledText(
            brd, font=('Segoe UI',10),
            bg=C['inp'], fg=C['txt'],
            insertbackground=C['acc3'],
            wrap='word', relief='flat', padx=10, pady=8)
        self._j_ta.pack(fill='both', expand=True)
        self._j_ta.focus_set()

        mk_btn(p,"  💾  JURNALNI SAQLASH  ",
               self._save_journal_dash, C['grn'],
               fs=11, px=24, py=10).pack(pady=8)

    def _save_journal_dash(self):
        content = self._j_ta.get("1.0","end-1c").strip()
        if not content:
            messagebox.showwarning("Bo'sh","Iltimos journal yozing!",
                                   parent=self.root)
            return
        self.jm.add(content, goal=self.s_goal, hours=self.s_hours)
        self._j_ta.delete("1.0","end")
        messagebox.showinfo("Saqlandi! ✅",
            f"Journal saqlandi!\nVaqt: {datetime.now().strftime('%H:%M')}\n"
            f"#{len(self.jm.entries)} ta yozuv",
            parent=self.root)

    # ════════════════════════════════════════════════════
    #  TIMER & NOTIFICATION LOOPS
    # ════════════════════════════════════════════════════

    def _timer_loop(self):
        while self.running:
            if not self.paused:
                rem = max(0.0, self.end_ts - time.time())
                pct = min(100.0, (self.total_s-rem)/self.total_s*100
                          if self.total_s>0 else 0)
                col = (C['red'] if rem<300 else
                       C['yel'] if rem<900 else C['acc3'])
                try:
                    self._timer_lbl.config(text=fmt_time(rem), fg=col)
                    self._prog_var.set(pct)
                    self._pct_lbl.config(text=f"{pct:.0f}%  tamamlandi")
                except Exception:
                    break

                if self.pomo and hasattr(self,'_pomo_lbl'):
                    pr = max(0.0, self.pomo_end - time.time())
                    pn = "ISH 🔥" if self.pomo_ph=="work" else "TANAFFUS ☕"
                    pc = C['grn'] if self.pomo_ph=="work" else C['yel']
                    try:
                        self._pomo_lbl.config(
                            text=f"🍅  {pn}  |  {fmt_time(pr)}", fg=pc)
                    except Exception:
                        pass
                    if pr <= 0:
                        self._switch_pomo()

                if rem <= 0:
                    self.running = False
                    self.root.after(0, self._screen_done)
                    break
            time.sleep(0.5)

    def _switch_pomo(self):
        if self.pomo_ph == "work":
            self.pomo_ph  = "break"
            self.pomo_end = time.time() + self.cfg.get('pomo_break',5)*60
            self.root.after(0, lambda: self._show_notif(
                "☕  Pomodoro — TANAFFUS",
                "25 daqiqa tugadi!\n5 daqiqa tanaffus.\nKo'zingizni dam oldiring! 👀"))
        else:
            self.pomo_ph  = "work"
            self.pomo_end = time.time() + self.cfg.get('pomo_work',25)*60
            self.root.after(0, lambda: self._show_notif(
                "🔥  Pomodoro — ISH",
                "Yangi 25 daqiqa!\nFocus! 🎯"))

    def _notif_loop(self):
        iv = self.cfg.get('notif_min',15) * 60
        while self.running:
            time.sleep(iv)
            if not self.running or self.paused: continue
            q = random.choice(QUOTES)
            body = q[2].format(date=date_str())
            self.root.after(0, lambda t=f"{q[0]}  {q[1]}", b=body:
                            self._show_notif(t, b))

    def _show_notif(self, title, message):
        try:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            W, H = 380, 185
            pop = tk.Toplevel(self.root)
            pop.attributes('-topmost', True)
            pop.overrideredirect(True)
            pop.configure(bg=C['card'])
            pop.geometry(f"{W}x{H}+{sw-W-10}+{sh-H-55}")

            brd = tk.Frame(pop, bg=C['acc2'], padx=2, pady=2)
            brd.pack(fill='both', expand=True)
            inn = tk.Frame(brd, bg=C['card'], padx=14, pady=10)
            inn.pack(fill='both', expand=True)

            top = tk.Frame(inn, bg=C['card'])
            top.pack(fill='x')
            tk.Label(top, text=title,
                     font=('Segoe UI',11,'bold'),
                     bg=C['card'], fg=C['acc3']).pack(side='left')
            tk.Button(top, text="✕", font=('Segoe UI',9),
                      bg=C['card'], fg=C['sub'],
                      activebackground=C['card'], activeforeground=C['red'],
                      relief='flat', bd=0, cursor='hand2',
                      command=pop.destroy).pack(side='right')

            tk.Frame(inn, bg=C['brd'], height=1).pack(fill='x', pady=4)
            tk.Label(inn, text=message,
                     font=('Segoe UI',9), bg=C['card'], fg=C['txt'],
                     justify='left', wraplength=340).pack(anchor='w')
            mk_btn(inn,"OK — davom etaman! 💪",pop.destroy,
                   C['acc'],fs=8,px=10,py=5).pack(anchor='e',pady=(6,0))

            pop.after(10000, lambda: pop.destroy() if pop.winfo_exists() else None)
            self._notifs.append(pop)
        except Exception as e:
            log(f"Notif error: {e}")

    # ─── Controls ──────────────────────────────────────

    def _toggle_pause(self):
        if not self.paused:
            self.paused  = True
            self.p_start = time.time()
            self._pause_btn.config(text="▶  Davom et")
            self._status_lbl.config(
                text="⏸  PAUZA — taymer to'xtatildi", fg=C['yel'])
        else:
            self.paused  = False
            dur          = time.time() - self.p_start
            self.end_ts += dur
            self._pause_btn.config(text="⏸  Pauza")
            self._status_lbl.config(
                text="✅  Saytlar bloklangan" if self.cfg.get('block_sites')
                     else "⚠  Bloklash o'chirilgan",
                fg=C['grn'] if self.cfg.get('block_sites') else C['yel'])

    def _ask_done(self):
        rem = fmt_time(max(0, self.end_ts - time.time()))
        if messagebox.askyesno("Tugatish",
                f"Ishingiz tugadimi?\n\nQolgan: {rem}\n\n"
                "HA → Kompyuter o'chadi\nYO'Q → Davom etadi",
                parent=self.root):
            self.running = False
            self.tm.end()
            self.root.after(0, self._screen_done)

    def _close_guard(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Yopish")
        dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost', True)
        dlg.resizable(False, False)
        W2,H2 = 380,220
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        dlg.geometry(f"{W2}x{H2}+{(sw-W2)//2}+{(sh-H2)//2}")

        mk_label(dlg,"🔒  FocusLock — Yopish",14,bold=True).pack(pady=(18,4))
        mk_label(dlg,"Yopish uchun parolni kiriting:",11,C['sub']).pack()
        var = tk.StringVar()
        brd = tk.Frame(dlg, bg=C['brd'], padx=1, pady=1)
        brd.pack(pady=8)
        ent = tk.Entry(brd, textvariable=var, show='●',
                       font=('Consolas',14), bg=C['inp'], fg=C['txt'],
                       insertbackground=C['wht'],
                       relief='flat', width=24, justify='center')
        ent.pack(ipady=9)
        ent.focus_set()

        def confirm():
            if var.get() == self.cfg.get('password'):
                self.running = False
                unblock_sites()
                dlg.destroy()
                try: self.root.destroy()
                except: pass
                sys.exit(0)
            else:
                messagebox.showwarning("Xato","Noto'g'ri parol!",parent=dlg)
                dlg.destroy()

        mk_btn(dlg,"Tasdiqlash",confirm,C['acc'],fs=11,px=24,py=9).pack(pady=4)
        ent.bind('<Return>', lambda e: confirm())
        dlg.grab_set()
        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

    # ════════════════════════════════════════════════════
    #  VAULT WINDOW
    # ════════════════════════════════════════════════════

    def _open_vault(self):
        # Parol so'rash
        dlg = tk.Toplevel(self.root)
        dlg.title("🔐 Vault")
        dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost', True)
        dlg.resizable(False, False)
        W2, H2 = 400, 260
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        dlg.geometry(f"{W2}x{H2}+{(sw-W2)//2}+{(sh-H2)//2}")

        mk_label(dlg,"🔐  VAULT",22,C['acc3'],bold=True).pack(pady=(22,4))
        mk_label(dlg,"Shaxsiy ma'lumotlaringiz himoyalangan",
                 11, C['sub']).pack()
        mk_label(dlg,"Vault parolini kiriting:",10,C['mut']).pack(pady=(10,4))

        brd = tk.Frame(dlg, bg=C['acc2'], padx=1, pady=1)
        brd.pack()
        vvar = tk.StringVar()
        vent = tk.Entry(brd, textvariable=vvar, show='●',
                        font=('Consolas',15), bg=C['inp'], fg=C['txt'],
                        insertbackground=C['acc3'],
                        relief='flat', width=24, justify='center')
        vent.pack(ipady=10, ipadx=8)
        vent.focus_set()

        err_lbl = mk_label(dlg,"",10,C['red'])
        err_lbl.pack(pady=4)

        def try_open():
            pw = vvar.get()
            h  = pw_hash(pw)
            if h != self.cfg.get('vault_pw_hash'):
                err_lbl.config(text="❌  Vault paroli noto'g'ri!")
                return
            if not self.vm.unlock(pw):
                err_lbl.config(text="❌  Shifrlash xatosi!")
                return
            dlg.destroy()
            self._vault_window()

        mk_btn(dlg,"  🔓  OCHISH  ",try_open,
               C['acc'],fs=12,px=30,py=12).pack(pady=8)
        vent.bind('<Return>', lambda e: try_open())
        dlg.grab_set()
        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

        mk_label(dlg,
                 "Default: VAULT2024  |  fl_config.json da o'zgartiring",
                 8, C['mut']).pack(pady=(0,4))

    def _vault_window(self):
        vw = tk.Toplevel(self.root)
        vw.title("🔐  FocusLock Vault")
        vw.configure(bg=C['bg'])
        vw.attributes('-topmost', True)
        vw.resizable(True, True)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        W2, H2 = min(900, sw-40), min(650, sh-80)
        vw.geometry(f"{W2}x{H2}+{(sw-W2)//2}+{(sh-H2)//2}")

        # Header
        hdr = tk.Frame(vw, bg=C['acc'], pady=8)
        hdr.pack(fill='x')
        tk.Label(hdr, text="🔐  VAULT  —  Himoyalangan Ma'lumotlar Xonasi",
                 font=('Segoe UI',12,'bold'),
                 bg=C['acc'], fg=C['wht']).pack(side='left', padx=16)
        mk_btn(hdr,"🔒  Yopish",
               lambda: (self.vm.lock(), vw.destroy()),
               C['acc2'],fs=9,px=12,py=5).pack(side='right',padx=10)

        # Notebook
        nb = ttk.Notebook(vw, style='FL.TNotebook')
        nb.pack(fill='both', expand=True, padx=8, pady=6)

        t_journals = tk.Frame(nb, bg=C['bg'])
        t_sessions = tk.Frame(nb, bg=C['bg'])
        t_notes    = tk.Frame(nb, bg=C['bg'])
        t_ai       = tk.Frame(nb, bg=C['bg'])
        t_plan     = tk.Frame(nb, bg=C['bg'])

        nb.add(t_journals, text="📖  Jurnallar")
        nb.add(t_sessions, text="📊  Sessiyalar")
        nb.add(t_notes,    text="📝  Shaxsiy")
        nb.add(t_ai,       text="🤖  AI Yordamchi")
        nb.add(t_plan,     text="📐  Rejalashtirish")

        self._build_vault_journals(t_journals)
        self._build_vault_sessions(t_sessions)
        self._build_vault_notes(t_notes)
        self._build_vault_ai(t_ai)
        self._build_vault_plan(t_plan)

        vw.protocol("WM_DELETE_WINDOW",
                    lambda: (self.vm.lock(), vw.destroy()))

    # ─── Vault: Journals ──────────────────────────────

    def _build_vault_journals(self, parent):
        entries = self.jm.entries

        top = tk.Frame(parent, bg=C['bg'])
        top.pack(fill='x', padx=12, pady=10)
        mk_label(top,f"📖  Barcha Jurnallar  ({len(entries)} ta yozuv)",
                 12, C['acc3'], bold=True).pack(side='left')

        # Search
        sv = tk.StringVar()
        brd, se = mk_entry(top, sv, width=22, ipy=5)
        brd.pack(side='right')
        se.bind('<KeyRelease>', lambda e: refresh_list(sv.get()))

        # Splitter: list (left) + detail (right)
        paned = tk.PanedWindow(parent, orient='horizontal',
                               bg=C['bg'], sashwidth=4,
                               sashrelief='flat', sashpad=2)
        paned.pack(fill='both', expand=True, padx=8, pady=4)

        # Left: list
        left_fr = tk.Frame(paned, bg=C['card'], width=220)
        paned.add(left_fr, minsize=180)

        lf_cv = tk.Canvas(left_fr, bg=C['card'], highlightthickness=0)
        lf_sb = tk.Scrollbar(left_fr, orient='vertical', command=lf_cv.yview)
        lf_cv.configure(yscrollcommand=lf_sb.set)
        lf_sb.pack(side='right', fill='y')
        lf_cv.pack(fill='both', expand=True)
        lf_inner = tk.Frame(lf_cv, bg=C['card'])
        lf_cv.create_window((0,0), window=lf_inner, anchor='nw')
        lf_inner.bind('<Configure>',
                      lambda e: lf_cv.configure(
                          scrollregion=lf_cv.bbox('all')))

        # Right: detail
        right_fr = tk.Frame(paned, bg=C['card'])
        paned.add(right_fr, minsize=300)

        detail_hdr = mk_label(right_fr,"← Chapdan journal tanlang",
                              10, C['mut'], bg=C['card'])
        detail_hdr.pack(anchor='w', padx=12, pady=8)

        detail_fr = tk.Frame(right_fr, bg=C['card'])
        detail_fr.pack(fill='both', expand=True, padx=10)

        detail_ta = scrolledtext.ScrolledText(
            detail_fr, font=('Segoe UI',10),
            bg=C['inp'], fg=C['txt'],
            insertbackground=C['acc3'],
            wrap='word', relief='flat', state='disabled')
        detail_ta.pack(fill='both', expand=True)

        def show_detail(entry):
            detail_ta.config(state='normal')
            detail_ta.delete("1.0","end")
            header_txt = (
                f"📅  {entry['datetime']}\n"
                f"⏱  {entry.get('hours',0)} soat  •  "
                f"🎯  {entry.get('goal','—')}\n"
                f"{'─'*50}\n\n"
            )
            detail_ta.insert("end", header_txt, "hdr")
            detail_ta.insert("end", entry["content"])
            detail_ta.tag_config("hdr", foreground=C['sub'],
                                 font=('Segoe UI',9))
            detail_ta.config(state='disabled')
            detail_hdr.config(
                text=f"📅  {entry['date']}  {entry['time']}")

        selected_btn = [None]

        def refresh_list(query=""):
            for w in lf_inner.winfo_children(): w.destroy()
            filtered = [e for e in reversed(entries)
                        if query.lower() in e.get('content','').lower()
                        or query.lower() in e.get('date','').lower()]
            if not filtered:
                mk_label(lf_inner,"Yozuv topilmadi",9,C['mut'],
                         bg=C['card']).pack(pady=10)
                return
            for e in filtered:
                row = tk.Frame(lf_inner, bg=C['card'], padx=8, pady=6,
                               cursor='hand2')
                row.pack(fill='x')
                snippet = e['content'][:40].replace('\n',' ')
                mk_label(row,f"📅  {e['date']}  {e['time']}",
                         8, C['acc3'], bg=C['card']).pack(anchor='w')
                mk_label(row,snippet+"...",8,C['sub'],
                         bg=C['card']).pack(anchor='w')
                tk.Frame(row, bg=C['mut'], height=1).pack(fill='x')
                entry_ref = e
                row.bind('<Enter>', lambda ev, r=row: r.config(bg=C['hov']))
                row.bind('<Leave>', lambda ev, r=row: r.config(bg=C['card']))
                row.bind('<Button-1>', lambda ev, r=entry_ref: show_detail(r))
                for ch in row.winfo_children():
                    ch.bind('<Button-1>',
                            lambda ev, r=entry_ref: show_detail(r))

        refresh_list()

    # ─── Vault: Sessions ──────────────────────────────

    def _build_vault_sessions(self, parent):
        sessions = load_json(TASKS_FILE, [])

        top = tk.Frame(parent, bg=C['bg'])
        top.pack(fill='x', padx=12, pady=10)
        mk_label(top,f"📊  Sessiya Statistikasi  ({len(sessions)} ta)",
                 12, C['acc3'], bold=True).pack(side='left')

        # Summary stats
        total_h = sum(s.get('hours',0) for s in sessions)
        total_d = len(set(s.get('date','') for s in sessions))
        all_tasks= sum(len(s.get('tasks',[])) for s in sessions)
        done_t   = sum(sum(1 for t in s.get('tasks',[]) if t.get('done'))
                       for s in sessions)

        sf = tk.Frame(parent, bg=C['card'], padx=16, pady=12)
        sf.pack(fill='x', padx=12, pady=(0,8))

        for lbl, val, col in [
            ("⏱  Jami ish vaqti",f"{total_h:.1f} soat",C['acc3']),
            ("📅  Ish kunlari",f"{total_d} kun",C['grn']),
            ("📋  Jami vazifalar",f"{all_tasks} ta",C['yel']),
            ("✅  Bajarilgan",f"{done_t} ta ({int(done_t/max(all_tasks,1)*100)}%)",C['grn']),
        ]:
            col_f = tk.Frame(sf, bg=C['card'])
            col_f.pack(side='left', expand=True)
            mk_label(col_f,val,16,col,bold=True,bg=C['card']).pack()
            mk_label(col_f,lbl,8,C['sub'],bg=C['card']).pack()

        # Chart: last 14 days
        mk_label(parent,"📈  So'nggi 14 kun (ish soatlari)",
                 9, C['sub']).pack(anchor='w', padx=14)

        chart_cv = tk.Canvas(parent, bg=C['card'],
                             height=160, highlightthickness=0)
        chart_cv.pack(fill='x', padx=12, pady=4)

        # Build daily data
        from datetime import timedelta, date as ddate
        today   = ddate.today()
        day_map = {}
        for s in sessions:
            try:
                d = ddate.fromisoformat(s.get('date',''))
                day_map[d] = day_map.get(d, 0) + s.get('hours', 0)
            except Exception:
                pass

        chart_data = []
        for i in range(13, -1, -1):
            d     = today - timedelta(days=i)
            lbl   = d.strftime("%d/%m")
            chart_data.append((lbl, day_map.get(d, 0)))

        chart_cv.update_idletasks()
        chart_cv.bind('<Configure>',
                      lambda e: draw_bar_chart(
                          chart_cv, chart_data,
                          e.width, 160,
                          title="So'nggi 14 kun ish soatlari"))
        self.root.after(300, lambda: draw_bar_chart(
            chart_cv, chart_data,
            chart_cv.winfo_width() or 800, 160,
            title="So'nggi 14 kun ish soatlari"))

        # Session list
        mk_label(parent,"— Barcha sessiyalar —",8,C['mut']).pack(pady=(4,2))
        lf = tk.Frame(parent, bg=C['card'])
        lf.pack(fill='both', expand=True, padx=12, pady=4)

        cv = tk.Canvas(lf, bg=C['card'], highlightthickness=0)
        sb = tk.Scrollbar(lf, orient='vertical', command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        cv.pack(fill='both', expand=True)
        inner = tk.Frame(cv, bg=C['card'])
        cv.create_window((0,0), window=inner, anchor='nw')
        inner.bind('<Configure>',
                   lambda e: cv.configure(scrollregion=cv.bbox('all')))

        if not sessions:
            mk_label(inner,"Hali sessiya yo'q",9,C['mut'],
                     bg=C['card']).pack(pady=12)
        else:
            for s in reversed(sessions[-30:]):
                row = tk.Frame(inner, bg=C['card'], padx=10, pady=5)
                row.pack(fill='x')
                task_info = s.get("summary","")
                goal      = s.get("goal","")
                info = (f"📅  {s.get('date','')}  "
                        f"⏱  {s.get('hours',0)}h  "
                        f"📋  {task_info}  "
                        + (f"🎯  {goal[:30]}" if goal else ""))
                mk_label(row,info,9,C['sub'],bg=C['card']).pack(anchor='w')
                tk.Frame(row, bg=C['mut'], height=1).pack(fill='x')

    # ─── Vault: Personal Notes ────────────────────────

    def _build_vault_notes(self, parent):
        CATS = ["💼 Ish","🎯 Maqsadlar","💡 G'oyalar",
                "🏥 Salomatlik","💰 Moliya","👥 Munosabatlar","📝 Boshqa"]

        top = tk.Frame(parent, bg=C['bg'])
        top.pack(fill='x', padx=12, pady=10)
        mk_label(top,"📝  Shaxsiy Eslatmalar  (Shifrlangan)",
                 12, C['acc3'], bold=True).pack(side='left')
        mk_btn(top,"+ Yangi",lambda: self._note_editor(parent,None,None,None,
                                                        lambda: self._refresh_notes(notes_fr)),
               C['acc'],fs=9,px=12,py=5).pack(side='right')

        notes_fr = tk.Frame(parent, bg=C['bg'])
        notes_fr.pack(fill='both', expand=True, padx=12, pady=4)

        self._refresh_notes(notes_fr)

    def _refresh_notes(self, notes_fr):
        for w in notes_fr.winfo_children(): w.destroy()
        notes = self.vm.get_notes()

        if not notes:
            info = tk.Frame(notes_fr, bg=C['card'], padx=20, pady=30)
            info.pack(expand=True)
            mk_label(info,"🔒  Xavfsiz saqlangan joy",14,C['sub'],
                     bg=C['card']).pack()
            mk_label(info,
                     "Bu yerda shaxsiy fikrlaringiz, maqsadlaringiz\n"
                     "va maxfiy ma'lumotlaringizni saqlang.\n"
                     "Hammasi shifrlangan — faqat siz ko'rasiz.",
                     11, C['mut'], bg=C['card']).pack(pady=8)
            mk_btn(info,"+ Birinchi eslatma qo'shish",
                   lambda: self._note_editor(
                       notes_fr, None, None, None,
                       lambda: self._refresh_notes(notes_fr)),
                   C['acc'], fs=11, px=20, py=10).pack(pady=6)
            return

        # Grid layout
        cv = tk.Canvas(notes_fr, bg=C['bg'], highlightthickness=0)
        sb = tk.Scrollbar(notes_fr, orient='vertical', command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        cv.pack(fill='both', expand=True)
        grid = tk.Frame(cv, bg=C['bg'])
        cv.create_window((0,0), window=grid, anchor='nw')
        grid.bind('<Configure>',
                  lambda e: cv.configure(scrollregion=cv.bbox('all')))

        cols = 3
        for i, note in enumerate(notes):
            row_n, col_n = divmod(i, cols)
            card = tk.Frame(grid, bg=C['card'],
                            padx=12, pady=10,
                            relief='flat', bd=0)
            card.grid(row=row_n, column=col_n,
                      padx=5, pady=5, sticky='nsew')
            grid.columnconfigure(col_n, weight=1)

            cat_col = {
                "💼": C['blu'], "🎯": C['acc3'],
                "💡": C['yel'], "🏥": C['grn'],
                "💰": C['ora'] if 'ora' in C else C['yel2'],
                "👥": C['acc2'], "📝": C['sub'],
            }.get(note['category'][:2], C['sub'])

            mk_label(card, note['category'],
                     9, cat_col, bold=True, bg=C['card']).pack(anchor='w')
            mk_label(card, note['title'],
                     11, C['txt'], bold=True, bg=C['card']).pack(anchor='w')
            snippet = note['content'][:80].replace('\n',' ')
            mk_label(card, snippet + ("..." if len(note['content'])>80 else ""),
                     9, C['sub'], bg=C['card']).pack(anchor='w', pady=2)
            mk_label(card, note['updated'][:10],
                     7, C['mut'], bg=C['card']).pack(anchor='e')

            btn_row = tk.Frame(card, bg=C['card'])
            btn_row.pack(fill='x', pady=(4,0))
            ii = i
            mk_btn(btn_row,"✏ Tahrirlash",
                   lambda ii=ii, n=note: self._note_editor(
                       notes_fr, ii, n['title'],
                       n['category'] + " " + n['content']
                       if False else n,
                       lambda: self._refresh_notes(notes_fr)),
                   C['inp'], fg=C['acc3'],
                   fs=7, px=6, py=3).pack(side='left', padx=2)
            mk_btn(btn_row,"🗑",
                   lambda ii=ii: (
                       self.vm.delete_note(ii),
                       self._refresh_notes(notes_fr)),
                   C['inp'], fg=C['red'],
                   fs=7, px=6, py=3).pack(side='right', padx=2)

    def _note_editor(self, parent_fr, idx, title_init, note_obj, on_save):
        dlg = tk.Toplevel()
        dlg.title("Eslatma")
        dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost', True)
        dlg.resizable(True, True)
        dlg.geometry("600x480")

        mk_label(dlg,"✏  Eslatma yozish",14,C['acc3'],
                 bold=True).pack(pady=(16,8))

        CATS = ["💼 Ish","🎯 Maqsadlar","💡 G'oyalar",
                "🏥 Salomatlik","💰 Moliya","👥 Munosabatlar","📝 Boshqa"]

        # Title
        tf = tk.Frame(dlg, bg=C['bg'])
        tf.pack(fill='x', padx=16, pady=4)
        mk_label(tf,"Sarlavha:",10,C['sub']).pack(anchor='w')
        tv = tk.StringVar(value=note_obj['title'] if note_obj else "")
        brd, _ = mk_entry(tf, tv, width=50, ipy=8)
        brd.pack(fill='x')

        # Category
        cf = tk.Frame(dlg, bg=C['bg'])
        cf.pack(fill='x', padx=16, pady=4)
        mk_label(cf,"Kategoriya:",10,C['sub']).pack(anchor='w')
        cv2 = tk.StringVar(value=note_obj['category'] if note_obj else CATS[0])
        cat_combo = ttk.Combobox(cf, textvariable=cv2,
                                 values=CATS, state='readonly',
                                 font=('Segoe UI',10), width=30)
        cat_combo.pack(anchor='w', pady=2)

        # Content
        cont_f = tk.Frame(dlg, bg=C['bg'])
        cont_f.pack(fill='both', expand=True, padx=16, pady=4)
        mk_label(cont_f,"Mazmun:",10,C['sub']).pack(anchor='w')
        brd2 = tk.Frame(cont_f, bg=C['brd'], padx=1, pady=1)
        brd2.pack(fill='both', expand=True)
        ta = scrolledtext.ScrolledText(brd2, font=('Segoe UI',10),
                                        bg=C['inp'], fg=C['txt'],
                                        insertbackground=C['acc3'],
                                        wrap='word', relief='flat')
        ta.pack(fill='both', expand=True, padx=2, pady=2)
        if note_obj:
            ta.insert('end', note_obj['content'])
        ta.focus_set()

        def do_save():
            t = tv.get().strip()
            ct = cv2.get()
            cont = ta.get("1.0","end-1c").strip()
            if not t or not cont:
                messagebox.showwarning("Bo'sh","Sarlavha va mazmunni kiriting!",
                                       parent=dlg)
                return
            if idx is None:
                self.vm.add_note(t, ct, cont)
            else:
                self.vm.update_note(idx, t, ct, cont)
            dlg.destroy()
            if on_save: on_save()

        br = tk.Frame(dlg, bg=C['bg'])
        br.pack(fill='x', padx=16, pady=8)
        mk_btn(br,"💾  Saqlash",do_save,C['grn'],
               fs=11,px=20,py=9).pack(side='right',padx=4)
        mk_btn(br,"Bekor",dlg.destroy,C['mut'],
               fs=10,px=14,py=9).pack(side='right',padx=4)

        dlg.grab_set()
        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

    # ─── Vault: AI Assistant ──────────────────────────

    def _build_vault_ai(self, parent):
        # AI chat state
        self._ai_history = []
        ai_sys = (
            "Sen UFQ tizimining shaxsiy AI yordamchisisiz. "
            "Foydalanuvchi bilan O'zbek tilida muloqot qilasiz. "
            "Productivity, focus, maqsadlar, self-development mavzularida "
            "chuqur va foydali maslahatlar berасиз. "
            "Javoblar aniq, tuzilgan va amaliy bo'lsin."
        )

        # Top bar
        top = tk.Frame(parent, bg=C['bg'])
        top.pack(fill='x', padx=12, pady=(10,4))
        mk_label(top,"🤖  Claude AI Yordamchi",12,C['acc3'],bold=True).pack(
            side='left')

        # API key setup button
        def open_settings():
            sdlg = tk.Toplevel()
            sdlg.title("AI Sozlamalar")
            sdlg.configure(bg=C['bg'])
            sdlg.attributes('-topmost', True)
            sdlg.resizable(False, False)
            sdlg.geometry("480x280")

            mk_label(sdlg,"⚙  AI API Sozlamalar",13,C['acc3'],
                     bold=True).pack(pady=(16,8))
            mk_label(sdlg,"API kalitini oling: console.anthropic.com",
                     9,C['sub']).pack()
            mk_label(sdlg,"Yangi hisob = bepul kredit bilan boshlanadi!",
                     9,C['grn']).pack(pady=(2,10))

            mv = tk.StringVar(value=self.cfg.get('ai_model',''))
            brd1, _ = mk_entry(sdlg, mv, width=40, ipy=7)
            mk_label(sdlg,"Model (tavsiya: claude-haiku-4-5-20251001):",
                     9,C['sub']).pack(anchor='w',padx=20)
            brd1.pack(padx=20, fill='x')

            mk_label(sdlg,"API kalit:",9,C['sub']).pack(
                anchor='w',padx=20,pady=(8,0))
            kv = tk.StringVar(value=self.cfg.get('ai_api_key',''))
            brd2, ke = mk_entry(sdlg, kv, width=40, ipy=7)
            ke.config(show='●')
            brd2.pack(padx=20, fill='x')

            def save_ai():
                self.cfg.set('ai_model', mv.get().strip())
                self.cfg.set('ai_api_key', kv.get().strip())
                sdlg.destroy()
                messagebox.showinfo("Saqlandi","AI sozlamalari saqlandi!")

            mk_btn(sdlg,"Saqlash",save_ai,C['grn'],
                   fs=11,px=24,py=9).pack(pady=12)
            sdlg.grab_set()
            sdlg.protocol("WM_DELETE_WINDOW", sdlg.destroy)

        mk_btn(top,"⚙ Sozlamalar",open_settings,C['inp'],
               fg=C['acc3'],fs=8,px=10,py=5).pack(side='right')

        # Chat display
        chat_brd = tk.Frame(parent, bg=C['brd'], padx=1, pady=1)
        chat_brd.pack(fill='both', expand=True, padx=12, pady=4)
        self._ai_chat = scrolledtext.ScrolledText(
            chat_brd, font=('Segoe UI',10),
            bg=C['inp'], fg=C['txt'],
            insertbackground=C['acc3'],
            wrap='word', relief='flat', state='disabled')
        self._ai_chat.pack(fill='both', expand=True, padx=2, pady=2)
        self._ai_chat.tag_config('user',
                                  foreground=C['acc3'],
                                  font=('Segoe UI',10,'bold'))
        self._ai_chat.tag_config('ai',
                                  foreground=C['txt'],
                                  font=('Segoe UI',10))
        self._ai_chat.tag_config('sys',
                                  foreground=C['mut'],
                                  font=('Segoe UI',8,'italic'))
        self._ai_chat.tag_config('err',
                                  foreground=C['red'])

        # Quick prompts
        qp_fr = tk.Frame(parent, bg=C['bg'])
        qp_fr.pack(fill='x', padx=12, pady=(4,0))
        mk_label(qp_fr,"💬  Tez savollar:",8,C['mut']).pack(side='left')
        for q in ["Bugungi ish rejasi","Focus qilish usullari",
                  "Maqsad tahlili","Qanday yaxshilana olaman?"]:
            mk_btn(qp_fr,q,
                   lambda qq=q: self._ai_send(qq, ai_sys),
                   C['inp'],fg=C['acc3'],
                   fs=7,px=7,py=4).pack(side='left',padx=2)

        # Input
        inp_fr = tk.Frame(parent, bg=C['bg'])
        inp_fr.pack(fill='x', padx=12, pady=8)
        self._ai_inp_var = tk.StringVar()
        brd, ai_ent = mk_entry(inp_fr, self._ai_inp_var, width=55, ipy=9)
        brd.pack(side='left', fill='x', expand=True)
        ai_ent.bind('<Return>', lambda e: self._ai_send(
            self._ai_inp_var.get(), ai_sys))

        self._ai_send_btn = mk_btn(
            inp_fr, "  ↑ Yuborish  ",
            lambda: self._ai_send(self._ai_inp_var.get(), ai_sys),
            C['acc'], fs=10, px=14, py=9)
        self._ai_send_btn.pack(side='left', padx=(8,0))

        # Welcome
        self._ai_append("🤖  Salom! Men sizning AI yordamchingizman.\n"
                        "Productivity, focus, maqsadlar haqida "
                        "savollaringizni bering!\n\n"
                        "⚙  Sozlamalar → API kalit kiriting (yangi hisob = bepul kredit)\n",
                        'sys')

    def _ai_append(self, text, tag='ai'):
        self._ai_chat.config(state='normal')
        self._ai_chat.insert('end', text + "\n", tag)
        self._ai_chat.config(state='disabled')
        self._ai_chat.see('end')

    def _ai_send(self, text, system):
        text = text.strip()
        if not text: return
        self._ai_inp_var.set("")
        self._ai_append(f"\n👤  Sen:\n{text}\n", 'user')
        self._ai_history.append({"role":"user","content":text})
        self._ai_send_btn.config(state='disabled',
                                  text="⏳  Javob kutilmoqda...")
        self._ai_append("🤖  AI javob yozmoqda...\n", 'sys')

        api_key = self.cfg.get('ai_api_key','')
        model   = self.cfg.get('ai_model','claude-haiku-4-5-20251001')
        hist    = self._ai_history.copy()

        def run():
            resp = ai_call(api_key, hist, system=system, model=model)
            def update():
                # Remove "writing" message
                self._ai_chat.config(state='normal')
                # Remove last line
                idx = self._ai_chat.index('end-2l')
                self._ai_chat.delete(idx, 'end')
                self._ai_chat.config(state='disabled')
                self._ai_append(f"\n🤖  AI:\n{resp}\n", 'ai')
                self._ai_history.append({"role":"assistant","content":resp})
                self._ai_send_btn.config(state='normal',
                                          text="  ↑ Yuborish  ")
            self.root.after(0, update)

        threading.Thread(target=run, daemon=True).start()

    # ─── Vault: Planning ──────────────────────────────

    def _build_vault_plan(self, parent):
        plan_sys = (
            "Sen UFQ tizimining rejalashtirish yordamchisisiz. "
            "O'zbek tilida professionalga loyiq "
            "Markdown formatda rejalar, diagrammalar (ASCII art), "
            "maqsad taqsimlash (Goal → Sub-goals → Tasks → Timeline), "
            "haftalik/oylik jadvallar yarat. "
            "Har doim tuzilgan, batafsil va amaliy natijalar ber."
        )

        top = tk.Frame(parent, bg=C['bg'])
        top.pack(fill='x', padx=12, pady=(10,4))
        mk_label(top,"📐  AI Rejalashtirish va Diagrammalar",
                 12, C['acc3'], bold=True).pack(side='left')

        # Templates
        tpl_fr = tk.Frame(parent, bg=C['card'], padx=10, pady=8)
        tpl_fr.pack(fill='x', padx=12, pady=(0,6))
        mk_label(tpl_fr,"📋  Shablonlar:",9,C['sub'],
                 bg=C['card']).pack(anchor='w',pady=(0,4))

        templates = {
            "📅 Haftalik reja":
                "Haftalik ishlar rejasini tuz. "
                "Kun bo'yicha jadval va muhim vazifalar.",
            "🎯 Maqsad breakdown":
                "Maqsadimni kichik vazifalarga bo'lib ber. "
                "Smart maqsad va timeline yarat.",
            "🗺 Mind Map":
                "Quyidagi mavzu bo'yicha ASCII mind map chiz.",
            "📊 Loyiha rejasi":
                "Loyiha uchun to'liq reja: bosqichlar, vaqt, "
                "resurslar va risklar.",
            "🏃 30-kunlik reja":
                "30 kunlik o'sish rejasi tuz. "
                "Har hafta uchun maqsad va nazorat.",
            "⚡ Kunlik jadval":
                "Samarali kunlik jadval tuz. "
                "Deep work bloklari bilan.",
        }

        tpl_row = tk.Frame(tpl_fr, bg=C['card'])
        tpl_row.pack(fill='x')

        self._plan_inp = None  # set below

        def use_template(prompt):
            if self._plan_inp:
                self._plan_inp.delete("1.0","end")
                self._plan_inp.insert("end", prompt)
                self._plan_inp.focus_set()

        for name, prompt in templates.items():
            mk_btn(tpl_row, name, lambda p=prompt: use_template(p),
                   C['inp'], fg=C['acc3'],
                   fs=8, px=8, py=5).pack(side='left', padx=2, pady=1)

        # Input
        inp_fr = tk.Frame(parent, bg=C['bg'])
        inp_fr.pack(fill='x', padx=12, pady=4)
        mk_label(inp_fr,"Nima rejalashtirasiz? (batafsil yozing):",
                 10, C['sub']).pack(anchor='w')
        brd = tk.Frame(inp_fr, bg=C['brd'], padx=1, pady=1)
        brd.pack(fill='x')
        self._plan_inp = scrolledtext.ScrolledText(
            brd, font=('Segoe UI',10),
            bg=C['inp'], fg=C['txt'],
            insertbackground=C['acc3'],
            wrap='word', relief='flat', height=4)
        self._plan_inp.pack(fill='x', padx=2, pady=2)
        self._plan_inp.focus_set()

        gen_row = tk.Frame(parent, bg=C['bg'])
        gen_row.pack(fill='x', padx=12, pady=4)

        self._plan_gen_btn = mk_btn(
            gen_row, "  🚀  REJA YARATISH  ",
            lambda: self._generate_plan(plan_sys),
            C['acc'], fs=12, px=24, py=11)
        self._plan_gen_btn.pack(side='left')

        self._plan_save_btn = mk_btn(
            gen_row, "💾 Saqlash",
            self._save_plan,
            C['grn'], fs=10, px=14, py=11)
        self._plan_save_btn.pack(side='left', padx=(8,0))
        self._plan_save_btn.config(state='disabled')

        mk_btn(gen_row, "📂 Saqlangan",
               self._show_saved_plans,
               C['inp'], fg=C['acc3'],
               fs=9, px=12, py=11).pack(side='right')

        # Output
        mk_label(parent,"— AI Natijasi —",8,C['mut']).pack(pady=(2,0))
        out_brd = tk.Frame(parent, bg=C['brd'], padx=1, pady=1)
        out_brd.pack(fill='both', expand=True, padx=12, pady=4)
        self._plan_out = scrolledtext.ScrolledText(
            out_brd, font=('Consolas',9),
            bg=C['inp'], fg=C['txt'],
            insertbackground=C['acc3'],
            wrap='word', relief='flat')
        self._plan_out.pack(fill='both', expand=True, padx=2, pady=2)
        self._plan_out.insert('end',
            "AI yordamida reja, diagramma yoki jadval yarating.\n"
            "Yuqoridan shablon tanlang yoki o'zingiz yozing.")
        self._plan_out.config(state='disabled')

    def _generate_plan(self, system):
        prompt = self._plan_inp.get("1.0","end-1c").strip()
        if not prompt:
            messagebox.showwarning("Bo'sh","Nima rejalashtirishingizni yozing!",
                                   parent=None)
            return
        self._plan_gen_btn.config(state='disabled', text="⏳  AI yozmoqda...")
        self._plan_out.config(state='normal')
        self._plan_out.delete("1.0","end")
        self._plan_out.insert('end',"⏳  AI javob tayyorlamoqda...\n")
        self._plan_out.config(state='disabled')

        api_key = self.cfg.get('ai_api_key','')
        model   = self.cfg.get('ai_model','claude-haiku-4-5-20251001')

        def run():
            resp = ai_call(api_key,
                           [{"role":"user","content":prompt}],
                           system=system, model=model,
                           max_tokens=2000)
            def update():
                self._plan_out.config(state='normal')
                self._plan_out.delete("1.0","end")
                self._plan_out.insert('end', resp)
                self._plan_out.config(state='disabled')
                self._plan_gen_btn.config(
                    state='normal', text="  🚀  REJA YARATISH  ")
                self._plan_save_btn.config(state='normal')
                self._last_plan = (prompt[:40], resp)
            self.root.after(0, update)

        self._last_plan = (prompt[:40], "")
        threading.Thread(target=run, daemon=True).start()

    def _save_plan(self):
        if hasattr(self, '_last_plan') and self._last_plan[1]:
            self.vm.save_plan(self._last_plan[0], self._last_plan[1])
            messagebox.showinfo("Saqlandi","Reja vault ga saqlandi!")
            self._plan_save_btn.config(state='disabled')

    def _show_saved_plans(self):
        plans = self.vm.get_plans()
        dlg = tk.Toplevel()
        dlg.title("Saqlangan Rejalar")
        dlg.configure(bg=C['bg'])
        dlg.attributes('-topmost', True)
        dlg.geometry("700x500")

        mk_label(dlg,f"📂  Saqlangan Rejalar ({len(plans)} ta)",
                 12, C['acc3'], bold=True).pack(pady=(12,8))

        if not plans:
            mk_label(dlg,"Hali reja saqlanmagan",11,C['sub']).pack(pady=20)
        else:
            paned = tk.PanedWindow(dlg, orient='horizontal', bg=C['bg'],
                                   sashwidth=4)
            paned.pack(fill='both', expand=True, padx=10, pady=8)

            lf = tk.Frame(paned, bg=C['card'], width=180)
            paned.add(lf, minsize=160)
            rf = tk.Frame(paned, bg=C['card'])
            paned.add(rf, minsize=400)

            detail = scrolledtext.ScrolledText(
                rf, font=('Consolas',9),
                bg=C['inp'], fg=C['txt'],
                wrap='word', relief='flat', state='disabled')
            detail.pack(fill='both', expand=True, padx=4, pady=4)

            def show_plan(plan):
                detail.config(state='normal')
                detail.delete("1.0","end")
                detail.insert('end', plan['content'])
                detail.config(state='disabled')

            for p in reversed(plans):
                row = tk.Frame(lf, bg=C['card'], padx=8, pady=6,
                               cursor='hand2')
                row.pack(fill='x')
                mk_label(row, p['title'][:25], 9, C['txt'],
                         bg=C['card']).pack(anchor='w')
                mk_label(row, p['saved'][:10], 7, C['mut'],
                         bg=C['card']).pack(anchor='w')
                tk.Frame(row, bg=C['mut'], height=1).pack(fill='x')
                plan_ref = p
                for w in [row] + row.winfo_children():
                    w.bind('<Button-1>',
                           lambda e, pp=plan_ref: show_plan(pp))

        mk_btn(dlg,"Yopish",dlg.destroy,C['inp'],
               fg=C['sub'],fs=9,px=12,py=6).pack(pady=8)
        dlg.grab_set()
        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

    # ════════════════════════════════════════════════════
    #  DONE SCREEN
    # ════════════════════════════════════════════════════

    def _screen_done(self):
        self.running = False
        log(f"Session done: {self.s_hours}h")
        self.tm.end()

        self._clear()
        self._fullscreen()
        self.root.configure(bg=C['bg'])
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.bind('<Alt-F4>', lambda e: "break")

        c = tk.Frame(self.root, bg=C['bg'])
        c.place(relx=.5, rely=.5, anchor='center')

        tk.Label(c, text="🏆",
                 font=('Segoe UI Emoji',80), bg=C['bg'], fg=C['yel']).pack()
        mk_label(c,"SESSIYA TUGADI!",36,bold=True).pack()
        mk_label(c,"Ajoyib! Bugun siz g'alaba qozondingiz! 💎",
                 13, C['acc3']).pack(pady=4)

        # Stats
        sf = tk.Frame(c, bg=C['inp'], padx=28, pady=16)
        sf.pack(pady=14)
        sessions = load_json(TASKS_FILE, [])
        lt_tasks = sessions[-1].get("tasks",[]) if sessions else []
        done_n   = sum(1 for t in lt_tasks if t.get('done'))
        total_n  = len(lt_tasks)

        for lbl, val, col in [
            ("⏱  Ishlangan:", f"{self.s_hours} soat", C['acc3']),
            ("🎯  Maqsad:", self.s_goal or "—", C['grn']),
            ("📋  Vazifalar:", f"{done_n}/{total_n} bajarildi",
             C['grn'] if done_n==total_n else C['yel']),
            ("🚫  Bloklangan:", f"{len(BLOCKED)} ta sayt", C['grn']),
        ]:
            r = tk.Frame(sf, bg=C['inp'])
            r.pack(pady=3)
            mk_label(r,lbl,12,C['sub'],bg=C['inp']).pack(side='left',padx=8)
            mk_label(r,val,12,col,bold=True,bg=C['inp']).pack(
                side='left',padx=8)

        tk.Frame(c, bg=C['acc'], height=2, width=540).pack(pady=16)

        # Journal
        jf = tk.Frame(c, bg=C['bg'])
        jf.pack(pady=8)
        self._done_jour_saved = False

        def open_journal_done():
            dlg = tk.Toplevel(self.root)
            dlg.title("Journal")
            dlg.configure(bg=C['bg'])
            dlg.attributes('-topmost',True)
            dlg.resizable(True,True)
            dlg.geometry("560x440")

            mk_label(dlg,
                f"📔  Bugungi Journal  —  {datetime.now().strftime('%d %B %Y')}",
                12, C['acc3'], bold=True).pack(pady=(14,8))

            pf2 = tk.Frame(dlg, bg=C['bg'])
            pf2.pack(fill='x', padx=14, pady=(0,4))
            ta_ref = [None]

            for q in ["Bugun nima yaxshi bo'ldi?",
                      "Nima chalg'itdi?","Ertaga reja?"]:
                mk_btn(pf2,f"+ {q.split('?')[0]}",
                       lambda qq=q: (
                           ta_ref[0] and ta_ref[0].insert(
                               'end', f"\n• {qq}\n"),
                           ta_ref[0] and ta_ref[0].focus_set()),
                       C['inp'],fg=C['acc3'],fs=8,px=8,py=4).pack(
                           side='left',padx=2)

            brd = tk.Frame(dlg, bg=C['brd'], padx=1, pady=1)
            brd.pack(fill='both', expand=True, padx=14, pady=4)
            ta2 = scrolledtext.ScrolledText(
                brd, font=('Segoe UI',10),
                bg=C['inp'], fg=C['txt'],
                insertbackground=C['acc3'],
                wrap='word', relief='flat')
            ta2.pack(fill='both', expand=True, padx=2, pady=2)
            ta_ref[0] = ta2
            ta2.focus_set()

            def save_j():
                content = ta2.get("1.0","end-1c").strip()
                if not content:
                    messagebox.showwarning("Bo'sh","Journal yozing!",parent=dlg)
                    return
                self.jm.add(content, self.s_goal, self.s_hours)
                self._done_jour_saved = True
                j_btn.config(text="✅  Journal yozildi",
                             bg=C['grn2'], state='disabled')
                dlg.destroy()

            mk_btn(dlg,"💾  SAQLASH",save_j,C['grn'],
                   fs=11,px=24,py=10).pack(pady=8)
            dlg.grab_set()
            dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

        j_btn = mk_btn(jf,"📔  Journal yozish",open_journal_done,
                        C['acc2'],fs=12,px=22,py=11)
        j_btn.pack()
        mk_label(jf,"(Tavsiya — kuchli odatlar shu yerda quriladi)",
                 9, C['mut']).pack(pady=2)

        tk.Frame(c, bg=C['brd'], height=1, width=540).pack(pady=14)
        mk_label(c,"Kompyuterni o'chirish yoki davom etish?",
                 15, bold=True).pack()

        btns = tk.Frame(c, bg=C['bg'])
        btns.pack(pady=16)
        mk_btn(btns,"🔴  HA — Kompyuterni o'chir",
               self._do_end, C['red'],fs=13,px=28,py=14).pack(
                   side='left',padx=10)

        ext_fr = tk.Frame(c, bg=C['bg'])
        ext_fr.pack()
        mk_label(ext_fr,"Yoki davom:",11,C['sub']).pack(side='left',padx=6)
        self._ext_v = tk.StringVar(value="30")
        brd3 = tk.Frame(ext_fr, bg=C['brd'], padx=1, pady=1)
        brd3.pack(side='left')
        tk.Entry(brd3, textvariable=self._ext_v,
                 font=('Consolas',14), bg=C['inp'], fg=C['acc3'],
                 relief='flat', width=5, justify='center').pack(ipady=6)
        mk_label(ext_fr,"daqiqa",11,C['sub']).pack(side='left',padx=6)
        mk_btn(ext_fr,"Davom et →",self._extend,
               C['acc'],fs=12,px=18,py=8).pack(side='left',padx=8)

    def _do_end(self):
        self.running = False
        for w in self._notifs:
            try: w.destroy()
            except: pass
        unblock_sites()
        self._clear()
        self._fullscreen()
        self.root.configure(bg=C['bg'])

        c = tk.Frame(self.root, bg=C['bg'])
        c.place(relx=.5, rely=.5, anchor='center')
        tk.Label(c, text="👋",
                 font=('Segoe UI Emoji',72), bg=C['bg'], fg=C['txt']).pack()
        mk_label(c,"Ajoyib ish qildingiz!",28,bold=True).pack(pady=6)
        mk_label(c,"Kompyuter 5 soniyada o'chirilmoqda...",
                 14, C['sub']).pack()
        self.root.update()
        time.sleep(2)
        do_shutdown()
        self.root.after(8000, self.root.destroy)

    def _extend(self):
        try:
            extra = int(self._ext_v.get())
            if extra <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Xato","To'g'ri daqiqa kiriting!",
                                 parent=self.root)
            return
        log(f"Extended {extra}min")
        self.s_hours = extra / 60
        self.total_s = extra * 60
        self.end_ts  = time.time() + extra*60
        self.running = True
        self.tm.new(goal=self.s_goal, hours=self.s_hours)
        self._screen_dashboard()
        threading.Thread(target=self._timer_loop, daemon=True).start()

# ════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════

if __name__ == "__main__":
    req_admin()
    FocusLock()
