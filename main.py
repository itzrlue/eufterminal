#!/usr/bin/env python3
"""
EUF Terminal 
Developer: Jalal | Made By Love 3>
Version: 2.0.0
Windows Only
Website: https://eufterminal.netlify.app/
"""

import os
import sys
import subprocess
import shutil
import time
import json
import socket
import threading
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import platform
import re
from typing import Optional, List, Tuple
import random
import base64
from urllib.parse import quote, unquote

# ── Platform guard ────────────────────────────────────────────────────────
_OS = platform.system()
if _OS != "Windows":
    _OS_NAMES = {
        "Linux":  "Linux",
        "Darwin": "macOS",
    }
    _OS_LABEL = _OS_NAMES.get(_OS, _OS)
    print()
    print("  EUF Terminal is built exclusively for Windows.")
    print(f"  Detected OS : {_OS_LABEL}")
    print()
    print("  This tool relies on Windows-specific APIs:")
    print("  winreg, ctypes/WinAPI, netsh, PowerShell, Windows Defender, etc.")
    print("  Running it on another OS will not work.")
    print()
    print("  Sorry — Windows only.")
    print()
    sys.exit(1)

import winreg
import ctypes
from ctypes import wintypes

# Third-party libraries auto-install
REQUIRED_LIBS = ["psutil", "requests", "colorama", "python-whois", "tqdm"]
for lib in REQUIRED_LIBS:
    try:
        __import__(lib.replace("-", "_").replace("python_whois", "whois"))
    except ImportError:
        print(f"Installing {lib}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

import psutil
import requests
from colorama import init, Fore, Back, Style
import whois
from tqdm import tqdm

try:
    import msvcrt
except ImportError:
    msvcrt = None

init(autoreset=True)


class EUFTerminal:
    def __init__(self):
        self.username = os.getlogin()
        self.home_path = Path(f"C:\\Users\\{self.username}")
        if self.home_path.exists():
            os.chdir(self.home_path)
            self.current_path = self.home_path
        else:
            self.current_path = Path.cwd()

        self.hostname = socket.gethostname()
        os.system(f"title EUF Terminal - {self.username}@{self.hostname}")

        self.C = {
            'success': Fore.GREEN,
            'error': Fore.RED,
            'warning': Fore.YELLOW,
            'info': Fore.CYAN,
            'header': Fore.BLUE + Style.BRIGHT,
            'path': Fore.YELLOW,
            'prompt_arrow': Fore.RED,
            'input': Fore.CYAN,
        }

        self.relax_videos = [
            "https://www.youtube.com/watch?v=6wr4dsS2_D4",
            "https://www.youtube.com/watch?v=sTlzjFABmoA",
            "https://www.youtube.com/watch?v=g64BkZjSNBM",
            "https://www.youtube.com/watch?v=CSjQgycOTyE",
            "https://www.youtube.com/watch?v=7A2YmgCOImc",
            "https://www.youtube.com/watch?v=C3RsFw43Uhk",
        ]

        self.miner_processes = [
            'xmrig.exe', 'minergate.exe', 'nicehash.exe', 'cpuminer.exe',
            'ethminer.exe', 'miner.exe', 'coinminer.exe', 'minerd.exe',
            'cgminer.exe', 'bfgminer.exe', 'claymore.exe', 'phoenixminer.exe',
            't-rex.exe', 'gminer.exe', 'lolminer.exe', 'nbminer.exe',
            'teamredminer.exe', 'cryptominer.exe', 'minergate-cli.exe',
        ]

        self.threat_keywords = [
            'miner', 'mining', 'crypto', 'ransom', 'keylog', 'steal',
            'inject', 'payload', 'exploit', 'backdoor', 'trojan', 'virus',
            'malware', 'spyware', 'adware', 'hijack',
        ]
        # runtime state
        self.is_root      = self._check_admin_at_start()
        self._aliases:  dict = {}
        self._history:  list = []
        self.input_color     = Fore.GREEN

        # color map for 'color' command
        self.COLOR_MAP = {
            'green':   Fore.GREEN,
            'blue':    Fore.BLUE,
            'cyan':    Fore.CYAN,
            'white':   Fore.WHITE,
            'yellow':  Fore.YELLOW,
            'red':     Fore.RED,
            'magenta': Fore.MAGENTA,
            'bright':  Fore.WHITE + Style.BRIGHT,
        }

        # Command aliases mapping
        self.cmd_aliases = {
            'ls': ['ls', 'list', 'dir'],
            'clear': ['clear', 'cls'],
            'exit': ['exit', 'quit'],
            'help': ['help', 'commands', '?'],
            'info': ['info', 'sysinfo', 'system'],
            'create': ['create', 'new', 'touch'],
            'delete': ['delete', 'del', 'remove'],
            'copy': ['copy', 'cp'],
            'move': ['move', 'mv', 'rename'],
            'search': ['search', 'find'],
            'read': ['read', 'cat', 'type'],
            'compress': ['compress', 'zip'],
            'uncompress': ['uncompress', 'unzip', 'extract'],
            'ping': ['ping', 'p'],
            'kill': ['kill', 'stop', 'terminate'],
            'screenshot': ['screenshot', 'ss', 'shot'],
            'weather': ['weather', 'temp'],
            'shutdown': ['shutdown', 'poweroff'],
            'sleep': ['sleep', 'suspend'],
            'logout': ['logout', 'signout'],
            'notepad': ['notepad', 'npad'],
            'request': ['request', 'req', 'http'],
            'protect': ['protect', 'lock'],
            'unprotect': ['unprotect', 'unlock'],
            'hide': ['hide', 'hidefile'],
            'unhide': ['unhide', 'showfile'],
            'encrypt': ['encrypt', 'encode'],
            'decrypt': ['decrypt', 'decode'],
        }

    def _check_admin_at_start(self) -> bool:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    # ─────────────────────────────── helpers ──────────────────────────────────

    def _ok(self, msg):
        print(f"{self.C['success']}[SUCCESS] {Fore.WHITE}{msg}")

    def _err(self, msg):
        print(f"{self.C['error']}[ERROR] {Fore.WHITE}{msg}")

    def _info(self, msg):
        print(f"{self.C['info']}[INFO] {Fore.WHITE}{msg}")

    def _warn(self, msg):
        print(f"{self.C['warning']}[WARNING] {Fore.WHITE}{msg}")

    def _sep(self, title="", char="=", width=60):
        if title:
            pad = (width - len(title) - 2) // 2
            print(f"{self.C['header']}{char*pad} {title} {char*pad}{Style.RESET_ALL}")
        else:
            print(f"{self.C['header']}{char*width}{Style.RESET_ALL}")

    def _resolve(self, name: str) -> Path:
        p = Path(name)
        return p if p.is_absolute() else self.current_path / name

    def _getch(self):
        if msvcrt:
            return msvcrt.getch()
        input()
        return b''

    def _kbhit(self):
        if msvcrt:
            return msvcrt.kbhit()
        return False

    def progress_bar(self, current, total, prefix="", suffix="", length=35):
        if total == 0:
            return
        pct = float(current) * 100 / total
        filled = int(length * current // total)
        bar = (
            f"{Fore.CYAN}["
            f"{Fore.GREEN}{'#'*filled}"
            f"{Fore.RED}{'-'*(length-filled)}"
            f"{Fore.CYAN}]"
        )
        end = "\n" if current >= total else ""
        sys.stdout.write(f"\r{prefix} {bar} {pct:.1f}% {suffix}{end}")
        sys.stdout.flush()

    # ──────────────────────────── startup ─────────────────────────────────────

    def show_startup_welcome(self):
        os.system('cls')
        print(f"""
{Fore.CYAN}{'='*70}
{Fore.GREEN}Welcome, {Fore.YELLOW}{self.username}{Fore.GREEN}. I hope you're having a good day. Welcome to {Fore.RED}EUF Terminal{Fore.GREEN}.
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
""")
        for i in range(101):
            self.progress_bar(i, 100, prefix=f"{Fore.MAGENTA}Loading:", suffix=f"{Fore.CYAN}Complete", length=40)
            time.sleep(0.02)
        print()
        time.sleep(0.4)
        os.system('cls')

    # ─────────────────────────────── info ─────────────────────────────────────

    def _get_windows_version(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            build = winreg.QueryValueEx(key, "CurrentBuild")[0]
            name  = winreg.QueryValueEx(key, "ProductName")[0]
            winreg.CloseKey(key)
            return f"Windows 11 (Build {build})" if int(build) >= 22000 else f"{name} (Build {build})"
        except Exception:
            return f"Windows {platform.release()}"

    def _get_gpu(self):
        try:
            r = subprocess.run(
                ['powershell', '-Command',
                 'Get-WmiObject Win32_VideoController | Select-Object -ExpandProperty Name'],
                capture_output=True, text=True, timeout=6)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip().split('\n')[0].strip()
        except Exception:
            pass
        return "N/A"

    def cmd_info(self):
        os.system('cls')
        cpu_pct   = psutil.cpu_percent(interval=0.2)
        cpu_cores = psutil.cpu_count()
        freq      = psutil.cpu_freq()
        freq_mhz  = f"{freq.current:.0f}" if freq else "N/A"
        ram       = psutil.virtual_memory()
        ram_u     = ram.used  / (1024**3)
        ram_t     = ram.total / (1024**3)
        gpu       = self._get_gpu()[:30]
        win_ver   = self._get_windows_version()[:32]
        uptime    = str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]

        art = [
            f"{Fore.CYAN}             _.-;;-._",
            f"{Fore.CYAN}      '-..-'|   ||   |",
            f"{Fore.CYAN}      '-..-'|_.-;;-._|",
            f"{Fore.CYAN}      '-..-'|   ||   |",
            f"{Fore.CYAN}      '-..-'|_.-''-._|",
        ]

        info_lines = [
            f"{Fore.BLUE + Style.BRIGHT}  SYSTEM INFORMATION{Style.RESET_ALL}",
            f"  {Fore.CYAN}OS      {Fore.WHITE}{win_ver}",
            f"  {Fore.CYAN}CPU     {Fore.WHITE}{cpu_cores} Cores @ {freq_mhz} MHz",
            f"  {Fore.CYAN}Usage   {Fore.WHITE}{cpu_pct:.1f}%",
            f"  {Fore.CYAN}RAM     {Fore.WHITE}{ram_u:.1f} / {ram_t:.1f} GB  ({ram.percent}%)",
            f"  {Fore.CYAN}GPU     {Fore.WHITE}{gpu}",
            f"  {Fore.CYAN}User    {Fore.WHITE}{self.username}",
            f"  {Fore.CYAN}Host    {Fore.WHITE}{self.hostname}",
            f"  {Fore.CYAN}Uptime  {Fore.WHITE}{uptime}",
        ]

        print()
        max_rows = max(len(art), len(info_lines))
        for i in range(max_rows):
            left  = art[i]       if i < len(art)        else " " * 25
            right = info_lines[i] if i < len(info_lines) else ""
            print(f"{left:<45}{right}{Style.RESET_ALL}")
        print()

    # ──────────────────────────── help ────────────────────────────────────────

    def cmd_help(self):
        W = Fore.WHITE
        G = Fore.GREEN
        Y = Fore.YELLOW
        H = self.C['header']
        R = Style.RESET_ALL
        print(f"""
{H}{'='*80}
                         EUF TERMINAL COMMANDS
{'='*80}{R}

   {G}help{W}                  - Show this help message
   {G}info{W}                  - Show system information
   {G}clear{W}                 - Clear screen
   {G}exit{W}                  - Exit terminal
   {G}dev{W}                   - Show developer info

{Y}File Management:{W}
   {G}create{W} <n>            - Create a new file
   {G}dircreate{W} <n>         - Create a new directory
   {G}delete{W} <n>            - Delete a file
   {G}dirdel{W} <n>            - Delete a directory
   {G}search{W} <n>            - Search for files and directories
   {G}move{W} <src> <dst>      - Move file or directory
   {G}rename{W} <old> <new>    - Rename file or directory
   {G}size{W} <n>              - Show size of file or directory
   {G}read{W} <n>              - Read file content
   {G}write{W} <n>             - Write or append to file interactively
   {G}compress{W} <n>          - Compress to zip
   {G}uncompress{W} <n>        - Extract a zip archive
   {G}copy{W} <src> <dst>      - Copy file or directory
   {G}touch{W} <n>             - Create or update file timestamp
   {G}hash{W} <n>              - MD5 / SHA1 / SHA256 checksums
   {G}scan{W} <n>              - Scan with Windows Defender
   {G}ls{W}                    - List current directory
   {G}open{W} <n>              - Open with default application
   {G}count{W} [dir]           - Count files and folders recursively
   {G}large{W} [dir] [MB]      - Find files larger than N MB (default 50)
   {G}recent{W}                - 20 most recently modified files

{Y}File Protection:{W}
   {G}protect{W} <n>           - Make file read-only (lock)
   {G}unprotect{W} <n>         - Remove read-only protection (unlock)
   {G}hide{W} <n>              - Hide a file or folder
   {G}unhide{W} <n>            - Unhide a file or folder
   {G}encrypt{W} <n>           - Encrypt a file (simple XOR)
   {G}decrypt{W} <n>           - Decrypt an encrypted file

{Y}Navigation:{W}
   {G}cd{W} <path>             - Change directory
   {G}desktop{W}               - Go to Desktop
   {G}downloads{W}             - Go to Downloads
   {G}documents{W}             - Go to Documents
   {G}music{W}                 - Go to Music
   {G}pictures{W}              - Go to Pictures
   {G}videos{W}                - Go to Videos
   {G}appdata{W}               - Go to AppData/Roaming

{Y}Terminal & Shell:{W}
   {G}cmd{W}                   - Open CMD
   {G}powershell{W}            - Open PowerShell
   {G}root{W}                  - Request admin privileges
   {G}python{W} [file.py]      - Run .py file  |  no args = interactive
   {G}html{W} [file.html]      - Open .html in browser  |  no args = interactive
   {G}js{W} [file.js]          - Run .js file  |  no args = interactive
   {G}calc{W} <expr>           - Math expression evaluator
   {G}encode{W} <method> <txt> - base64 / hex / url  encode or decode
   {G}clipboard{W} <act>       - get / set <text> / clear
   {G}note{W} <act>            - add <text> / list / clear  (persists)
   {G}alias{W} <n> <cmd>       - Session shortcut  |  alias list
   {G}run{W} [file]            - Auto-run any file by type
   {G}history{W} [n]           - Show command history
   {G}clear-history{W}         - Clear session history
   {G}diskusage{W}             - Disk usage for all drives
   {G}uptime{W}                - System uptime and boot time
   {G}ping-sweep{W} [subnet]   - Ping all hosts in a /24 subnet
   {G}terminal-here{W}         - Open new CMD in current directory
   {G}diff{W} <f1> <f2>        - Show differences between two files
   {G}zip-list{W} <file.zip>   - List contents of a zip archive
   {G}notepad{W} [file]        - Open Windows Notepad

{Y}HTTP Requests:{W}
   {G}request{W} get <url>     - Send GET request
   {G}request{W} post <url> <data> - Send POST request
   {G}request{W} delete <url>  - Send DELETE request
   {G}request{W} headers <url> - Get only response headers

{Y}Network:{W}
   {G}ipinfo{W} <ip>           - IP geolocation
   {G}domaininfo{W} <domain>   - WHOIS and IP lookup
   {G}ping{W} <host>           - Ping
   {G}traceroute{W} <host>     - Trace network route
   {G}portscan{W} <ip>         - Scan common open ports
   {G}speedtest{W}             - Internet speed test
   {G}wifi-list{W}             - Saved Wi-Fi passwords
   {G}download{W} <url>        - Download file from URL
   {G}net-scan{W}              - Scan local network
   {G}dns-over-https{W}        - Set DNS to Cloudflare DoH
   {G}flush-dns{W}             - Flush DNS resolver cache
   {G}ip-config{W}             - Full ipconfig /all
   {G}myip{W}                  - Public and local IP addresses
   {G}netstat{W}               - Active TCP/UDP connections

{Y}Web & Apps:{W}
   {G}youtube{W}               - Open YouTube
   {G}deepseek{W}              - Open DeepSeek
   {G}relax{W}                 - Random relaxing video
   {G}browser{W}               - Open default browser

{Y}Fun & Games:{W}
   {G}rain{W}                  - Rain animation  (Q to stop)
   {G}game{W}                  - Number guessing game
   {G}rip{W}                   - R.I.P All Dead Souls

{Y}Security & System:{W}
   {G}kill-connections{W}      - Kill all active connections
   {G}sys-integrity{W}         - SFC system file check
   {G}anti-run{W} <dir>        - Monitor dir for new executables
   {G}antivirus-scan{W}        - Scan processes for threats
   {G}winsec{W} <on|off>       - Toggle Windows Defender
   {G}repair{W}                - SFC + DISM repair
   {G}tempdel{W}               - Clean temp files
   {G}tweak{W}                 - Windows performance tweaks
   {G}closeall{W}              - Close all user applications
   {G}who-called-me{W}         - Camera/mic access history
   {G}hosts{W}                 - View hosts file
   {G}regedit{W} <key>         - Read a registry key
   {G}services{W}              - List Windows services
   {G}service{W} <act> <n>     - start / stop / restart a service
   {G}taskmgr{W}               - Open Task Manager

{Y}Power:{W}
   {G}shutdown{W}              - Shutdown computer
   {G}sleep{W}                 - Sleep
   {G}logout{W}                - Log out

{Y}Monitoring:{W}
   {G}cam-check{W}             - Apps using camera now
   {G}mic-check{W}             - Apps using microphone now
   {G}startup-check{W}         - Startup programs
   {G}activeapps{W}            - Running applications
   {G}process-tree{W}          - Process hierarchy tree
   {G}listening-ports{W}       - Ports open for connections
   {G}kill{W} <name|pid>       - Kill a process
   {G}autorun{W} <on|off>      - Terminal auto-startup
   {G}sysinfo{W}               - Full hardware snapshot
   {G}sysmon{W}                - Live CPU / RAM monitor

{Y}Utilities:{W}
   {G}timer{W} <h/m/s> <val>   - Set a timer
   {G}weather{W}               - Weather for your location
   {G}env{W} [filter]          - Environment variables
   {G}screenshot{W}            - Take a screenshot
   {G}battery{W}               - Battery status

{Y}Color & Customization:{W}
   {G}color{W} <n>             - Set input text color
   {G}colortest{W}             - Display all available colors

{Y}Generators:{W}
   {G}passwd{W} [length]       - Generate a strong random password
   {G}uuid{W}                  - Generate a random UUID v4
   {G}base{W} <val> <from> <to>- Convert between number bases

{'='*80}{R}""")

    # ──────────────────────────── file management ──────────────────────────────

    def cmd_create(self, name: str):
        try:
            target = self._resolve(name)
            target.touch(exist_ok=True)
            self._ok(f"File created: {Fore.YELLOW}{target}")
        except Exception as e:
            self._err(str(e))

    def cmd_dircreate(self, name: str):
        try:
            target = self._resolve(name)
            target.mkdir(parents=True, exist_ok=True)
            self._ok(f"Directory created: {Fore.YELLOW}{target}")
        except Exception as e:
            self._err(str(e))

    def cmd_delete(self, name: str):
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"Not found: {name}")
                return
            if target.is_file():
                target.unlink()
                self._ok(f"File deleted: {Fore.RED}{name}")
            else:
                self._err(f"{name} is a directory. Use 'dirdel' instead.")
        except Exception as e:
            self._err(str(e))

    def cmd_dirdel(self, name: str):
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"Directory not found: {name}")
                return
            if not target.is_dir():
                self._err(f"{name} is not a directory.")
                return
            confirm = input(f"{Fore.YELLOW}Delete '{target}'? [y/N]: {Fore.WHITE}").strip().lower()
            if confirm != 'y':
                self._info("Cancelled.")
                return
            shutil.rmtree(target)
            self._ok(f"Directory deleted: {Fore.RED}{name}")
        except Exception as e:
            self._err(str(e))

    def cmd_search(self, name: str):
        self._info(f"Searching for '{Fore.YELLOW}{name}{Fore.WHITE}'...")
        found = []
        skip_dirs = {'windows', 'program files', 'program files (x86)', '$recycle.bin',
                     'system volume information', 'programdata'}
        try:
            for root, dirs, files in os.walk("C:\\"):
                root_lower = root.lower()
                if any(s in root_lower for s in skip_dirs):
                    dirs.clear()
                    continue
                for d in dirs:
                    if name.lower() in d.lower():
                        found.append(str(Path(root) / d))
                for f in files:
                    if name.lower() in f.lower():
                        found.append(str(Path(root) / f))
                if len(found) >= 200:
                    break
        except PermissionError:
            pass
        except Exception as e:
            self._err(str(e))
            return

        if not found:
            self._warn(f"Nothing found matching '{name}'")
            return

        display = found[:50]
        for p in display:
            print(f"  {Fore.CYAN}{p}")
        if len(found) > 50:
            print(f"  {Fore.YELLOW}... and {len(found)-50} more results.")
        self._ok(f"Found {len(found)} result(s).")

    def cmd_move(self, src: str, dst: str):
        try:
            s = self._resolve(src)
            d = self._resolve(dst)
            if not s.exists():
                self._err(f"Source not found: {src}")
                return
            shutil.move(str(s), str(d))
            self._ok(f"Moved: {Fore.YELLOW}{src} {Fore.WHITE}-> {Fore.CYAN}{dst}")
        except Exception as e:
            self._err(str(e))

    def cmd_rename(self, old: str, new: str):
        try:
            s = self._resolve(old)
            d = s.parent / new
            if not s.exists():
                self._err(f"Not found: {old}")
                return
            s.rename(d)
            self._ok(f"Renamed: {Fore.YELLOW}{old} {Fore.WHITE}-> {Fore.CYAN}{new}")
        except Exception as e:
            self._err(str(e))

    def cmd_size(self, name: str):
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"Not found: {name}")
                return
            if target.is_file():
                size = target.stat().st_size
            else:
                size = sum(f.stat().st_size for f in target.rglob('*') if f.is_file())
            units = [(1024**3, "GB"), (1024**2, "MB"), (1024, "KB"), (1, "B")]
            for factor, unit in units:
                if size >= factor:
                    print(f"{Fore.CYAN}Size:{Fore.WHITE} {size/factor:.2f} {unit} ({size:,} bytes)")
                    break
        except Exception as e:
            self._err(str(e))

    def cmd_read(self, name: str):
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"File not found: {name}")
                return
            if not target.is_file():
                self._err(f"{name} is not a file.")
                return
            self._sep(f"CONTENT: {name}")
            with open(target, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            print(f"{Fore.WHITE}{content}")
            self._sep()
            print(f"{Fore.YELLOW}Lines: {content.count(chr(10))+1} | Chars: {len(content)}")
        except Exception as e:
            self._err(str(e))

    def cmd_compress(self, name: str):
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"Not found: {name}")
                return
            zip_path = self.current_path / f"{target.stem}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                if target.is_file():
                    zf.write(target, target.name)
                else:
                    for f in target.rglob('*'):
                        zf.write(f, f.relative_to(target.parent))
            self._ok(f"Compressed to: {Fore.YELLOW}{zip_path.name}")
        except Exception as e:
            self._err(str(e))

    def cmd_uncompress(self, name: str):
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"Archive not found: {name}")
                return
            if target.suffix.lower() != '.zip':
                self._err("Only .zip archives are supported.")
                return
            out = self.current_path / target.stem
            out.mkdir(exist_ok=True)
            with zipfile.ZipFile(target, 'r') as zf:
                zf.extractall(out)
            self._ok(f"Extracted to: {Fore.YELLOW}{out}")
        except zipfile.BadZipFile:
            self._err("Invalid or corrupted zip file.")
        except Exception as e:
            self._err(str(e))

    def cmd_scan(self, name: str):
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"File not found: {name}")
                return
            defender = Path("C:\\Program Files\\Windows Defender\\MpCmdRun.exe")
            if not defender.exists():
                self._err("Windows Defender not found.")
                return
            self._info(f"Scanning '{name}' with Windows Defender...")
            result = subprocess.run(
                [str(defender), '-Scan', '-ScanType', '3', '-File', str(target)],
                capture_output=True, text=True, timeout=120)
            if 'found no threats' in result.stdout.lower() or result.returncode == 0:
                self._ok("No threats found.")
            else:
                self._warn("Potential threat detected! Check Windows Defender for details.")
            if result.stdout.strip():
                print(f"{Fore.WHITE}{result.stdout.strip()}")
        except subprocess.TimeoutExpired:
            self._err("Scan timed out.")
        except Exception as e:
            self._err(str(e))

    def cmd_cd(self, path: str = None):
        try:
            if not path or path == "~":
                new = self.home_path
            elif path == "..":
                new = self.current_path.parent
            elif path == ".":
                return
            else:
                new = Path(path) if Path(path).is_absolute() else self.current_path / path
            new = new.resolve()
            if new.exists() and new.is_dir():
                os.chdir(new)
                self.current_path = new
                self._ok(f"Directory: {Fore.YELLOW}{new}")
            else:
                self._err(f"Directory not found: {path}")
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── file protection commands ─────────────────────────

    def cmd_protect(self, name: str):
        """Make a file read-only (protected)."""
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"File not found: {name}")
                return
            os.chmod(target, 0o444)  # read-only for everyone
            self._ok(f"File protected (read-only): {Fore.YELLOW}{target.name}")
        except Exception as e:
            self._err(str(e))

    def cmd_unprotect(self, name: str):
        """Remove read-only protection."""
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"File not found: {name}")
                return
            os.chmod(target, 0o666)  # read-write
            self._ok(f"Protection removed: {Fore.YELLOW}{target.name}")
        except Exception as e:
            self._err(str(e))

    def cmd_hide(self, name: str):
        """Hide a file or folder."""
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"Not found: {name}")
                return
            subprocess.run(['attrib', '+h', str(target)], capture_output=True)
            self._ok(f"Hidden: {Fore.YELLOW}{target.name}")
        except Exception as e:
            self._err(str(e))

    def cmd_unhide(self, name: str):
        """Unhide a file or folder."""
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"Not found: {name}")
                return
            subprocess.run(['attrib', '-h', str(target)], capture_output=True)
            self._ok(f"Unhidden: {Fore.YELLOW}{target.name}")
        except Exception as e:
            self._err(str(e))

    def cmd_encrypt(self, name: str):
        """Simple XOR encryption for a file."""
        try:
            target = self._resolve(name)
            if not target.exists() or not target.is_file():
                self._err(f"File not found: {name}")
                return
            key = 0xAA  # simple XOR key
            data = target.read_bytes()
            encrypted = bytes([b ^ key for b in data])
            target.write_bytes(encrypted)
            self._ok(f"File encrypted: {Fore.YELLOW}{target.name}")
        except Exception as e:
            self._err(str(e))

    def cmd_decrypt(self, name: str):
        """Decrypt a file encrypted with simple XOR."""
        try:
            target = self._resolve(name)
            if not target.exists() or not target.is_file():
                self._err(f"File not found: {name}")
                return
            key = 0xAA
            data = target.read_bytes()
            decrypted = bytes([b ^ key for b in data])
            target.write_bytes(decrypted)
            self._ok(f"File decrypted: {Fore.YELLOW}{target.name}")
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── HTTP request commands ────────────────────────────

    def cmd_request(self, method: str = None, url: str = None, data: str = None):
        """Send HTTP requests (GET, POST, DELETE, etc.)."""
        if not method or not url:
            self._err("Usage: request <get|post|delete|headers> <url> [data]")
            return

        method = method.lower()
        try:
            if method == 'get':
                self._info(f"Sending GET to: {Fore.YELLOW}{url}")
                r = requests.get(url, timeout=15)
                self._sep(f"RESPONSE ({r.status_code})")
                print(f"{Fore.GREEN}{r.text[:2000]}{Style.RESET_ALL}")
                if len(r.text) > 2000:
                    print(f"{Fore.YELLOW}... (truncated, {len(r.text)} total chars)")
                self._sep()
                self._ok(f"Status: {r.status_code} - {r.reason}")

            elif method == 'post':
                self._info(f"Sending POST to: {Fore.YELLOW}{url}")
                payload = data or "{}"
                try:
                    json_data = json.loads(payload)
                    r = requests.post(url, json=json_data, timeout=15)
                except json.JSONDecodeError:
                    r = requests.post(url, data=payload, timeout=15)
                self._sep(f"RESPONSE ({r.status_code})")
                print(f"{Fore.GREEN}{r.text[:2000]}{Style.RESET_ALL}")
                self._sep()
                self._ok(f"Status: {r.status_code} - {r.reason}")

            elif method == 'delete':
                self._info(f"Sending DELETE to: {Fore.YELLOW}{url}")
                r = requests.delete(url, timeout=15)
                self._sep(f"RESPONSE ({r.status_code})")
                print(f"{Fore.GREEN}{r.text[:2000]}{Style.RESET_ALL}")
                self._sep()
                self._ok(f"Status: {r.status_code} - {r.reason}")

            elif method == 'headers':
                self._info(f"Getting headers from: {Fore.YELLOW}{url}")
                r = requests.head(url, timeout=10)
                self._sep("RESPONSE HEADERS")
                for k, v in r.headers.items():
                    print(f"  {Fore.CYAN}{k}: {Fore.WHITE}{v}")
                self._sep()
                self._ok(f"Status: {r.status_code} - {r.reason}")

            else:
                self._err(f"Unknown method: {method}. Use: get, post, delete, headers")

        except requests.ConnectionError:
            self._err("Connection failed. Check your internet.")
        except requests.Timeout:
            self._err("Request timed out.")
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── notepad command ──────────────────────────────────

    def cmd_notepad(self, filename: str = None):
        """Open Windows Notepad, optionally with a file."""
        try:
            if filename:
                target = self._resolve(filename)
                if target.exists():
                    subprocess.Popen(['notepad.exe', str(target)])
                    self._ok(f"Opened {Fore.YELLOW}{target.name} in Notepad")
                else:
                    # Create file if it doesn't exist
                    target.touch()
                    subprocess.Popen(['notepad.exe', str(target)])
                    self._ok(f"Created and opened: {Fore.YELLOW}{target.name}")
            else:
                subprocess.Popen(['notepad.exe'])
                self._ok("Notepad opened")
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── terminal & shell ─────────────────────────────────

    def cmd_cmd(self):
        self._info("Opening CMD... Type 'exit' to return.")
        try:
            subprocess.call('cmd', cwd=str(self.current_path))
        except Exception as e:
            self._err(str(e))
        self._ok("Returned to EUF Terminal.")

    def cmd_powershell(self):
        self._info("Opening PowerShell... Type 'exit' to return.")
        try:
            subprocess.call('powershell', cwd=str(self.current_path))
        except Exception as e:
            self._err(str(e))
        self._ok("Returned to EUF Terminal.")

    def _is_admin(self) -> bool:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def cmd_root(self):
        try:
            if self._is_admin():
                self.is_root = True
                self._ok("Already running as Administrator. Prompt updated.")
            else:
                self._warn("Requesting Administrator privileges via UAC...")
                script = str(Path(sys.argv[0]).resolve())
                ret = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, f'"{script}"',
                    str(self.current_path), 1)
                if ret <= 32:
                    self._err(f"UAC cancelled or failed (code {ret}).")
                else:
                    self._info("Elevated window launched. This session continues normally.")
        except Exception as e:
            self._err(str(e))

    def cmd_python_exec(self, filename: str = None):
        if filename:
            target = self._resolve(filename)
            if not target.exists():
                self._err(f"File not found: {filename}")
                return
            if target.suffix.lower() != '.py':
                self._warn(f"'{filename}' does not have a .py extension — trying anyway.")
            self._info(f"Running: {Fore.YELLOW}{target.name}")
            print(f"{Fore.BLUE}{'─'*50}{Style.RESET_ALL}")
            try:
                result = subprocess.run(
                    [sys.executable, str(target)],
                    cwd=str(target.parent),
                    timeout=300)
                print(f"{Fore.BLUE}{'─'*50}{Style.RESET_ALL}")
                if result.returncode == 0:
                    self._ok(f"'{target.name}' finished (exit code 0).")
                else:
                    self._warn(f"'{target.name}' exited with code {result.returncode}.")
            except subprocess.TimeoutExpired:
                self._err("Execution timed out (5 min).")
            except Exception as e:
                self._err(str(e))
        else:
            self._info("Interactive Python — type code, then 'END' to execute, 'QUIT' to cancel.")
            lines = []
            while True:
                try:
                    line = input(f"{Fore.CYAN}>>> {Fore.WHITE}")
                except EOFError:
                    break
                if line.strip().upper() == 'END':
                    break
                if line.strip().upper() == 'QUIT':
                    self._info("Cancelled.")
                    return
                lines.append(line)
            code = '\n'.join(lines)
            if not code.strip():
                return
            print(f"{Fore.BLUE}{'─'*50}{Style.RESET_ALL}")
            try:
                exec(compile(code, '<euf_python>', 'exec'), {'__builtins__': __builtins__})
                print(f"{Fore.BLUE}{'─'*50}{Style.RESET_ALL}")
                self._ok("Executed successfully.")
            except SyntaxError as e:
                self._err(f"Syntax error at line {e.lineno}: {e.msg}")
            except Exception as e:
                self._err(f"Runtime error: {type(e).__name__}: {e}")

    def cmd_html(self, filename: str = None):
        if filename:
            target = self._resolve(filename)
            if not target.exists():
                self._err(f"File not found: {filename}")
                return
            if target.suffix.lower() not in ('.html', '.htm'):
                self._warn(f"'{filename}' does not have an .html extension — trying anyway.")
            try:
                os.startfile(str(target))
                self._ok(f"Opened in browser: {Fore.YELLOW}{target.name}")
            except Exception as e:
                self._err(str(e))
        else:
            self._info("Interactive HTML — type code, then 'END' to open, 'QUIT' to cancel.")
            lines = []
            while True:
                try:
                    line = input(f"{Fore.CYAN}HTML> {Fore.WHITE}")
                except EOFError:
                    break
                if line.strip().upper() == 'END':
                    break
                if line.strip().upper() == 'QUIT':
                    self._info("Cancelled.")
                    return
                lines.append(line)
            code = '\n'.join(lines)
            if not code.strip():
                return
            try:
                html_file = self.current_path / f"euf_temp_{int(time.time())}.html"
                html_file.write_text(code, encoding='utf-8')
                os.startfile(str(html_file))
                self._ok(f"Opened in browser: {Fore.YELLOW}{html_file.name}")
            except Exception as e:
                self._err(str(e))

    def cmd_js(self, filename: str = None):
        if filename:
            target = self._resolve(filename)
            if not target.exists():
                self._err(f"File not found: {filename}")
                return
            if target.suffix.lower() != '.js':
                self._warn(f"'{filename}' does not have a .js extension — trying anyway.")
            self._info(f"Running: {Fore.YELLOW}{target.name}")
            print(f"{Fore.BLUE}{'─'*50}{Style.RESET_ALL}")
            try:
                r = subprocess.run(
                    ['cscript', '//Nologo', str(target)],
                    cwd=str(target.parent),
                    capture_output=True, text=True, timeout=60)
                if r.stdout:
                    print(f"{Fore.WHITE}{r.stdout}", end="")
                if r.stderr:
                    print(f"{Fore.RED}{r.stderr}", end="")
                print(f"{Fore.BLUE}{'─'*50}{Style.RESET_ALL}")
                if r.returncode == 0:
                    self._ok(f"'{target.name}' finished (exit code 0).")
                else:
                    self._warn(f"'{target.name}' exited with code {r.returncode}.")
            except subprocess.TimeoutExpired:
                self._err("Execution timed out (60s).")
            except FileNotFoundError:
                self._err("cscript not found. Make sure Windows Script Host is enabled.")
            except Exception as e:
                self._err(str(e))
        else:
            self._info("Interactive JS — type code, then 'END' to execute, 'QUIT' to cancel.")
            lines = []
            while True:
                try:
                    line = input(f"{Fore.CYAN}JS> {Fore.WHITE}")
                except EOFError:
                    break
                if line.strip().upper() == 'END':
                    break
                if line.strip().upper() == 'QUIT':
                    self._info("Cancelled.")
                    return
                lines.append(line)
            code = '\n'.join(lines)
            if not code.strip():
                return
            js_file = None
            try:
                js_file = self.current_path / f"euf_temp_{int(time.time())}.js"
                js_file.write_text(code, encoding='utf-8')
                print(f"{Fore.BLUE}{'─'*50}{Style.RESET_ALL}")
                r = subprocess.run(
                    ['cscript', '//Nologo', str(js_file)],
                    capture_output=True, text=True, timeout=30)
                if r.stdout:
                    print(f"{Fore.WHITE}{r.stdout}", end="")
                if r.stderr:
                    print(f"{Fore.RED}{r.stderr}", end="")
                print(f"{Fore.BLUE}{'─'*50}{Style.RESET_ALL}")
                self._ok("Executed successfully.")
            except subprocess.TimeoutExpired:
                self._err("Execution timed out (30s).")
            except FileNotFoundError:
                self._err("cscript not found. Make sure Windows Script Host is enabled.")
            except Exception as e:
                self._err(str(e))
            finally:
                if js_file and js_file.exists():
                    try:
                        js_file.unlink()
                    except Exception:
                        pass

    # ─────────────────────── network tools ────────────────────────────────────

    def cmd_ipinfo(self, ip: str):
        try:
            self._info(f"Looking up: {Fore.YELLOW}{ip}")
            r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=8)
            if r.status_code != 200:
                self._err(f"Request failed ({r.status_code})")
                return
            d = r.json()
            if 'error' in d:
                self._err(d.get('reason', 'Unknown error'))
                return
            self._sep(f"IP INFO: {ip}")
            fields = [
                ("IP",      d.get('ip',       'N/A')),
                ("City",    d.get('city',     'N/A')),
                ("Region",  d.get('region',   'N/A')),
                ("Country", d.get('country_name', 'N/A')),
                ("ISP",     d.get('org',      'N/A')),
                ("Timezone",d.get('timezone', 'N/A')),
                ("Latitude",str(d.get('latitude','N/A'))),
                ("Longitude",str(d.get('longitude','N/A'))),
            ]
            for k, v in fields:
                print(f"  {Fore.CYAN}{k:<12}{Fore.WHITE}{v}")
            self._sep()
        except requests.ConnectionError:
            self._err("No internet connection.")
        except Exception as e:
            self._err(str(e))

    def cmd_domaininfo(self, domain: str):
        try:
            self._info(f"Looking up domain: {Fore.YELLOW}{domain}")
            try:
                ip = socket.gethostbyname(domain)
                print(f"  {Fore.CYAN}IP Address: {Fore.WHITE}{ip}")
            except socket.gaierror:
                print(f"  {Fore.RED}Could not resolve IP.")
                ip = None

            try:
                w = whois.whois(domain)
                self._sep(f"WHOIS: {domain}")
                for field in ['registrar', 'creation_date', 'expiration_date', 'name_servers']:
                    val = getattr(w, field, None)
                    if val:
                        if isinstance(val, list):
                            val = val[0]
                        print(f"  {Fore.CYAN}{field:<18}{Fore.WHITE}{val}")
            except Exception:
                self._warn("WHOIS lookup failed.")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_ping(self, host: str):
        try:
            self._info(f"Pinging {Fore.YELLOW}{host}{Fore.WHITE}...")
            subprocess.call(['ping', '-n', '4', host])
        except Exception as e:
            self._err(str(e))

    def cmd_portscan(self, ip: str):
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
                        443, 445, 3306, 3389, 5900, 8080, 8443]
        self._info(f"Scanning common ports on {Fore.YELLOW}{ip}{Fore.WHITE}...")
        open_ports = []
        lock = threading.Lock()

        def check(port):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.0)
                if s.connect_ex((ip, port)) == 0:
                    with lock:
                        open_ports.append(port)
                s.close()
            except Exception:
                pass

        threads = [threading.Thread(target=check, args=(p,), daemon=True) for p in common_ports]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        self._sep(f"PORT SCAN: {ip}")
        if open_ports:
            for p in sorted(open_ports):
                services = {21:'FTP',22:'SSH',23:'Telnet',25:'SMTP',53:'DNS',80:'HTTP',
                            110:'POP3',135:'MSRPC',139:'NetBIOS',143:'IMAP',443:'HTTPS',
                            445:'SMB',3306:'MySQL',3389:'RDP',5900:'VNC',8080:'HTTP-Alt',8443:'HTTPS-Alt'}
                svc = services.get(p, "Unknown")
                print(f"  {Fore.GREEN}[OPEN] {Fore.WHITE}Port {Fore.CYAN}{p:<6}{Fore.WHITE} {svc}")
        else:
            self._warn("No open ports found.")
        self._sep()

    def cmd_speedtest(self):
        self._info("Testing internet speed (this may take a moment)...")

        try:
            try:
                import speedtest as _st
            except ImportError:
                _st = None

            if _st and hasattr(_st, 'Speedtest'):
                st = _st.Speedtest(secure=True)
                st.get_best_server()
                print(f"{Fore.YELLOW}Testing download...", end=' ', flush=True)
                dl = st.download() / 1_000_000
                print(f"{Fore.GREEN}{dl:.2f} Mbps")
                print(f"{Fore.YELLOW}Testing upload... ", end=' ', flush=True)
                ul = st.upload()   / 1_000_000
                print(f"{Fore.GREEN}{ul:.2f} Mbps")
                ping = getattr(getattr(st, 'results', None), 'ping', None)
                if ping is not None:
                    print(f"  {Fore.CYAN}Ping    : {Fore.WHITE}{ping:.2f} ms")
                return

            if _st is None:
                self._info("Installing speedtest-cli...")
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', 'speedtest-cli', '--quiet'],
                    timeout=60)
                import speedtest as _st
                if hasattr(_st, 'Speedtest'):
                    st = _st.Speedtest(secure=True)
                    st.get_best_server()
                    print(f"{Fore.YELLOW}Testing download...", end=' ', flush=True)
                    dl = st.download() / 1_000_000
                    print(f"{Fore.GREEN}{dl:.2f} Mbps")
                    print(f"{Fore.YELLOW}Testing upload... ", end=' ', flush=True)
                    ul = st.upload()   / 1_000_000
                    print(f"{Fore.GREEN}{ul:.2f} Mbps")
                    return

        except Exception as lib_err:
            self._warn(f"speedtest-cli unavailable ({lib_err}). Using HTTP fallback...")

        try:
            import time as _time

            DL_URL = "https://speed.cloudflare.com/__down?bytes=10000000"
            print(f"{Fore.YELLOW}Testing download (HTTP)...", end=' ', flush=True)
            t0 = _time.perf_counter()
            r  = requests.get(DL_URL, stream=True, timeout=30)
            received = sum(len(chunk) for chunk in r.iter_content(chunk_size=65536))
            dt = _time.perf_counter() - t0
            dl_mbps = (received * 8) / (dt * 1_000_000) if dt > 0 else 0
            print(f"{Fore.GREEN}{dl_mbps:.2f} Mbps")

            UL_URL  = "https://speed.cloudflare.com/__up"
            payload = b'0' * 5_000_000
            print(f"{Fore.YELLOW}Testing upload (HTTP)...  ", end=' ', flush=True)
            t0 = _time.perf_counter()
            requests.post(UL_URL, data=payload, timeout=30)
            dt = _time.perf_counter() - t0
            ul_mbps = (len(payload) * 8) / (dt * 1_000_000) if dt > 0 else 0
            print(f"{Fore.GREEN}{ul_mbps:.2f} Mbps")

            PING_URL = "https://speed.cloudflare.com/__down?bytes=1"
            samples  = []
            for _ in range(6):
                t0 = _time.perf_counter()
                requests.head(PING_URL, timeout=5)
                samples.append((_time.perf_counter() - t0) * 1000)
            avg_ping = sum(sorted(samples)[1:-1]) / max(len(samples) - 2, 1)
            print(f"  {Fore.CYAN}Ping    : {Fore.WHITE}{avg_ping:.1f} ms (avg)")

        except requests.ConnectionError:
            self._err("No internet connection.")
        except Exception as e:
            self._err(f"Speed test failed: {e}")

    def cmd_wifi_list(self):
        try:
            self._info("Retrieving saved Wi-Fi profiles...")
            r = subprocess.run(['netsh', 'wlan', 'show', 'profiles'],
                               capture_output=True, text=True)
            profiles = re.findall(r"All User Profile\s*:\s*(.+)", r.stdout)
            if not profiles:
                self._warn("No saved Wi-Fi profiles found.")
                return
            self._sep("SAVED WI-FI NETWORKS")
            for profile in profiles:
                name = profile.strip()
                try:
                    p = subprocess.run(
                        ['netsh', 'wlan', 'show', 'profile', name, 'key=clear'],
                        capture_output=True, text=True)
                    pwd_match = re.search(r"Key Content\s*:\s*(.+)", p.stdout)
                    pwd = pwd_match.group(1).strip() if pwd_match else "(no password / hidden)"
                    print(f"  {Fore.CYAN}{name:<35} {Fore.YELLOW}{pwd}")
                except Exception:
                    print(f"  {Fore.CYAN}{name:<35} {Fore.RED}(error retrieving password)")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_download(self, url: str):
        try:
            self._info(f"Downloading: {Fore.YELLOW}{url}")
            fname = url.split('/')[-1].split('?')[0] or f"download_{int(time.time())}"
            dest = self.current_path / fname
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            self.progress_bar(downloaded, total,
                                              prefix=f"{Fore.MAGENTA}Download:",
                                              suffix=f"{downloaded//1024}KB")
            print()
            self._ok(f"Saved to: {Fore.YELLOW}{dest}")
        except requests.HTTPError as e:
            self._err(f"HTTP error: {e}")
        except requests.ConnectionError:
            self._err("Connection failed.")
        except Exception as e:
            self._err(str(e))

    def cmd_net_scan(self):
        try:
            import ipaddress
            self._info("Scanning local network...")
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            network = '.'.join(local_ip.split('.')[:3])
            found = []
            lock = threading.Lock()

            def ping_host(ip):
                r = subprocess.run(['ping', '-n', '1', '-w', '500', ip],
                                   capture_output=True)
                if r.returncode == 0:
                    with lock:
                        found.append(ip)

            threads = []
            self._info(f"Scanning {network}.1 - {network}.254 ...")
            for i in range(1, 255):
                t = threading.Thread(target=ping_host, args=(f"{network}.{i}",), daemon=True)
                threads.append(t)
                t.start()
                if len(threads) % 50 == 0:
                    for th in threads[-50:]:
                        th.join(timeout=2)
            for t in threads:
                t.join(timeout=2)

            self._sep("LOCAL NETWORK DEVICES")
            for ip in sorted(found, key=lambda x: int(x.split('.')[-1])):
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except Exception:
                    hostname = "N/A"
                marker = f"{Fore.GREEN}(YOU)" if ip == local_ip else ""
                print(f"  {Fore.CYAN}{ip:<16} {Fore.WHITE}{hostname} {marker}")
            print(f"\n  {Fore.YELLOW}Total: {len(found)} device(s) found.")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_dns_over_https(self):
        try:
            self._info("Enabling DNS over HTTPS (Cloudflare)...")
            ifaces = ['Ethernet', 'Wi-Fi', 'Local Area Connection']
            for iface in ifaces:
                subprocess.run(
                    ['netsh', 'interface', 'ip', 'set', 'dns',
                     f'name="{iface}"', 'static', '1.1.1.1'],
                    capture_output=True)
                subprocess.run(
                    ['netsh', 'interface', 'ip', 'add', 'dns',
                     f'name="{iface}"', '1.0.0.1', 'index=2'],
                    capture_output=True)
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            self._ok("DNS set to Cloudflare 1.1.1.1 & 1.0.0.1. DNS cache flushed.")
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── web & apps ───────────────────────────────────────

    def _open_url(self, url: str, label: str = ""):
        import webbrowser
        webbrowser.open(url)
        self._ok(f"{label or url} opened in browser.")

    def cmd_browser(self):
        self._open_url("https://www.google.com", "Browser")

    def cmd_youtube(self):
        self._open_url("https://youtube.com", "YouTube")

    def cmd_deepseek(self):
        self._open_url("https://chat.deepseek.com", "DeepSeek")

    # ─────────────────────── fun & games ──────────────────────────────────────

    def cmd_rain(self):
        os.system('cls')
        print('\033[?25l', end='', flush=True)

        static_art = [
            "      |       |        |       | |",
            " ' |   |   |     '  |      '      ",
            "              |           |     | ",
            " '     |  _,..--I--..,_ |         ",
            "   / _.-`` _,-`   `-,_ ``-._ \\    ",
            "     `-,_,_,.,_   _,.,_._,-`      ",
            "|  | '   '     `Y` __ '     '     ",
            "  '|        ,-. I /  \\       |  | ",
            " |    |    /   )I \\  /     '   |  ",
            "'  '      /   / I_.\"\"._           ",
            "|  |    ,l  .'..`      `.   ' |  |",
            " |     / | /   \\        l         ",
            "      /, '\"  .  \\      ||   |   | ",
            " |  ' ||      |\"|      ||   |     ",
            "'     ||      | |      ||       | ",
            "|     \\|      | '.____,'/  |  |   ",
            "   |   |      |  |    |F   '    | ",
            " | '   |      |  | |\\ |     ' |   ",
            "       |      |  | || |      |    ",
            "|  |   |      |  | || |    |    | ",
            "       |      |  | || |      |    ",
            " ' |   '.____,'  \\_||_/   |    |  ",
            "         |/\\|    [_][_]      |    ",
            "\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"",
        ]

        try:
            cols, rows = shutil.get_terminal_size(fallback=(80, 30))
            cols = max(cols - 1, 40)
            rows = max(rows - 2, 20)
        except Exception:
            cols, rows = 80, 30

        art_height = len(static_art)
        safe_art = [line[:cols] for line in static_art]
        art_width  = max(len(l) for l in safe_art) if safe_art else 0
        start_y    = max(0, (rows - art_height) // 2)
        start_x    = max(0, (cols - art_width)  // 2)

        def art_char_at(ax, ay):
            if 0 <= ay < len(safe_art):
                line = safe_art[ay]
                if 0 <= ax < len(line):
                    return line[ax]
            return ' '

        def is_art(cx, cy):
            ax = cx - start_x
            ay = cy - start_y
            return art_char_at(ax, ay) != ' '

        drops = []
        attempts = 0
        while len(drops) < 60 and attempts < 5000:
            attempts += 1
            x = random.randint(0, cols - 1)
            y = random.randint(-(rows), -1)
            if not is_art(x, max(0, y)):
                drops.append({'x': x, 'y': y, 'speed': random.randint(1, 2)})

        try:
            while True:
                if msvcrt and msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key in (b'\x1b', b'q', b'Q'):
                        break

                sys.stdout.write('\033[2J\033[H')

                for drop in drops:
                    drop['y'] += drop['speed']
                    if drop['y'] >= rows:
                        drop['y'] = random.randint(-(rows // 2), -1)
                        drop['x'] = random.randint(0, cols - 1)

                    cy = drop['y']
                    cx = drop['x']
                    if 0 <= cy < rows and 0 <= cx < cols:
                        if not is_art(cx, cy):
                            sys.stdout.write(f"\033[{cy+1};{cx+1}H{Fore.CYAN}|")

                for i, line in enumerate(safe_art):
                    row = start_y + i
                    if 0 <= row < rows:
                        sys.stdout.write(f"\033[{row+1};{start_x+1}H{Fore.GREEN}{line}")

                hint = "Press Q or ESC to stop"
                sys.stdout.write(f"\033[{rows};1H{Fore.YELLOW}{hint}")

                sys.stdout.flush()
                time.sleep(0.08)

        except KeyboardInterrupt:
            pass
        finally:
            print('\033[?25h', end='')
            os.system('cls')
            self._ok("Rain stopped.")

    def cmd_rip(self):
        os.system('cls')
        print(f"""
{Fore.CYAN}               ______
              '-._   ```\"\"\"--.._
           ,-----.:___           `\\  ,;;;,
            '-.._     ```\"\"\"--.._  |,%%%%%%              _
            ,    '.              `\\;;;;  -\\      _    _.'/\\
          .' `-.__ \\            ,;;;;\" .__{{=====/_)==:_  ||
     ,===/        ```\";,,,,,,,;;;;;'`-./.____,'/ /     '.\\/
    '---/              ';;;;;;;;'      `--.._.' /
   ,===/                          '-.        `\\/
  '---/                            ,'`.        |
     ;                        __.-'    \\     ,'
  \\______,,.....------'''``          `---`

{Fore.RED}                    R.I.P All Dead Souls.{Style.RESET_ALL}
""")
        print(f"{Fore.WHITE}Press any key to continue...")
        self._getch()
        os.system('cls')

    def cmd_relax(self):
        os.system('cls')
        print(f"""
{Fore.CYAN}                                               _
                 ___                          (_)
               _/XXX\\_
{Fore.GREEN}_             /XXXXXX\\_                                    __
{Fore.CYAN}X\\__    __   /X XXXX XX\\                          _       /XX\\__      ___
    \\__/  \\_/__       \\ \\                       _/X\\__   /XX XXX\\____/XXX\\
  \\  ___   \\/  \\_      \\ \\               __   _/      \\_/  _/  -   __  -  \\__/
 ___/   \\__/   \\ \\__     \\\\__           /  \\_//  _ _ \\  \\     __  /  \\____//
/  __    \\  /     \\ \\_   _//_\\___     _/    //           \\___/  \\/     __/
__/_______\\________\\__\\_/________\\_ _/_____/_____________/______\\____/_______
{Fore.YELLOW}                                  /|\\
                                 / | \\
                                /  |  \\
                               /   |   \\
                              /    |    \\
{Fore.MAGENTA}
         Opening a relaxing video in your browser...

         {Fore.WHITE}Press any key to return to terminal.
""")
        import webbrowser
        webbrowser.open(random.choice(self.relax_videos))
        self._getch()
        os.system('cls')
        self._ok("Relaxation session ended. Welcome back.")

    def cmd_game(self):
        os.system('cls')
        self._sep("GUESS THE NUMBER")
        secret = random.randint(1, 100)
        attempts = 0
        print(f"{Fore.WHITE}I picked a number between 1 and 100. Try to guess it!")
        print(f"{Fore.YELLOW}Type 'quit' to exit.\n")
        while True:
            try:
                raw = input(f"{Fore.CYAN}Your guess: {Fore.WHITE}").strip()
                if raw.lower() == 'quit':
                    print(f"{Fore.YELLOW}The number was {secret}. Bye!")
                    break
                guess = int(raw)
                attempts += 1
                if guess < secret:
                    print(f"  {Fore.BLUE}Too low!")
                elif guess > secret:
                    print(f"  {Fore.RED}Too high!")
                else:
                    self._ok(f"Correct! You got it in {attempts} attempt(s).")
                    break
            except ValueError:
                self._err("Enter a valid number.")
            except KeyboardInterrupt:
                print()
                break

    # ─────────────────────── security & system ────────────────────────────────

    def cmd_kill_connections(self):
        try:
            self._warn("Killing all active TCP connections...")
            conns = psutil.net_connections(kind='tcp')
            killed = 0
            for c in conns:
                if c.status == 'ESTABLISHED' and c.pid:
                    try:
                        proc = psutil.Process(c.pid)
                        name = proc.name()
                        proc.kill()
                        print(f"  {Fore.RED}Killed: {Fore.WHITE}{name} (PID {c.pid})")
                        killed += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            self._ok(f"Killed {killed} connection(s).")
        except Exception as e:
            self._err(str(e))

    def cmd_sys_integrity(self):
        try:
            self._info("Running System File Checker (SFC). This may take a few minutes...")
            result = subprocess.run(['sfc', '/scannow'], capture_output=True, text=True,
                                    timeout=600)
            output = result.stdout or result.stderr
            if 'did not find any integrity violations' in output.lower():
                self._ok("No integrity violations found.")
            elif 'repaired' in output.lower():
                self._warn("Some issues were found and repaired.")
            else:
                self._warn("Check complete. Review output above.")
            print(f"{Fore.WHITE}{output[:2000]}")
        except subprocess.TimeoutExpired:
            self._err("SFC timed out.")
        except Exception as e:
            self._err(str(e))

    def cmd_anti_run(self, directory: str):
        target = self._resolve(directory)
        if not target.exists() or not target.is_dir():
            self._err(f"Directory not found: {directory}")
            return
        self._info(f"Monitoring '{target}' for executables. Press Ctrl+C to stop.")
        known = set(f for f in target.iterdir() if f.suffix.lower() in ('.exe', '.bat', '.cmd', '.ps1'))
        try:
            while True:
                time.sleep(2)
                current = set(f for f in target.iterdir() if f.suffix.lower() in ('.exe', '.bat', '.cmd', '.ps1'))
                new_files = current - known
                for nf in new_files:
                    self._warn(f"New executable detected: {nf.name}")
                    choice = input(f"  Delete it? [y/N]: ").strip().lower()
                    if choice == 'y':
                        try:
                            nf.unlink()
                            self._ok(f"Deleted: {nf.name}")
                        except Exception as e:
                            self._err(str(e))
                known = current
        except KeyboardInterrupt:
            self._ok("Monitoring stopped.")

    def cmd_antivirus_scan(self):
        self._info("Scanning running processes for threats...")
        threats = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    name = (proc.info['name'] or '').lower()
                    exe  = (proc.info['exe']  or '').lower()
                    flagged = (
                        name in self.miner_processes or
                        any(k in name for k in self.threat_keywords) or
                        any(k in exe  for k in self.threat_keywords)
                    )
                    if flagged:
                        threats.append((proc.info['pid'], proc.info['name'], proc.info['exe'] or 'N/A'))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            self._err(str(e))
            return

        self._sep("ANTIVIRUS SCAN RESULTS")
        if threats:
            for pid, name, exe in threats:
                print(f"  {Fore.RED}[THREAT] {Fore.WHITE}PID {pid} | {name} | {exe}")
            self._warn(f"{len(threats)} threat(s) found!")
            choice = input(f"\n{Fore.YELLOW}Kill all threats? [y/N]: {Fore.WHITE}").strip().lower()
            if choice == 'y':
                for pid, name, _ in threats:
                    try:
                        psutil.Process(pid).kill()
                        self._ok(f"Killed: {name} (PID {pid})")
                    except Exception as e:
                        self._err(f"Could not kill {name}: {e}")
        else:
            self._ok("No threats detected.")
        self._sep()

    def cmd_winsec(self, state: str):
        state = state.lower()
        if state not in ('on', 'off'):
            self._err("Usage: winsec <on/off>")
            return
        try:
            if state == 'off':
                self._warn("Disabling Windows Defender Real-Time Protection...")
                subprocess.run(
                    ['powershell', '-Command',
                     'Set-MpPreference -DisableRealtimeMonitoring $true'],
                    capture_output=True, check=True)
                self._ok("Real-Time Protection disabled.")
            else:
                self._info("Enabling Windows Defender Real-Time Protection...")
                subprocess.run(
                    ['powershell', '-Command',
                     'Set-MpPreference -DisableRealtimeMonitoring $false'],
                    capture_output=True, check=True)
                self._ok("Real-Time Protection enabled.")
        except subprocess.CalledProcessError:
            self._err("Access denied. Run as Administrator (use 'root' first).")
        except Exception as e:
            self._err(str(e))

    def cmd_repair(self):
        self._info("Running SFC and DISM repair. This will take several minutes...")
        try:
            print(f"{Fore.YELLOW}Step 1: DISM /RestoreHealth")
            subprocess.run(['DISM', '/Online', '/Cleanup-Image', '/RestoreHealth'],
                           timeout=600)
            print(f"{Fore.YELLOW}Step 2: SFC /scannow")
            subprocess.run(['sfc', '/scannow'], timeout=600)
            self._ok("System repair complete.")
        except subprocess.TimeoutExpired:
            self._err("Repair timed out.")
        except Exception as e:
            self._err(str(e))

    def cmd_tempdel(self):
        temp_dirs = [
            Path(os.environ.get('TEMP', '')),
            Path(os.environ.get('TMP', '')),
            Path(f"C:\\Windows\\Temp"),
            Path(f"C:\\Users\\{self.username}\\AppData\\Local\\Temp"),
        ]
        total = 0
        self._info("Cleaning temporary files...")
        for td in temp_dirs:
            if not td.exists():
                continue
            for item in td.iterdir():
                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink()
                        total += size
                    elif item.is_dir():
                        size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                        shutil.rmtree(item, ignore_errors=True)
                        total += size
                except Exception:
                    pass
        mb = total / (1024**2)
        self._ok(f"Freed {mb:.2f} MB of temporary files.")

    def cmd_tweak(self):
        self._info("Applying performance tweaks...")
        tweaks = [
            (['powershell', '-Command', 'powercfg /setactive SCHEME_MIN'], "Power plan: High Performance"),
            (['sc', 'config', 'SysMain', 'start=disabled'], "Disabled SysMain (Superfetch)"),
            (['sc', 'stop', 'SysMain'], "Stopped SysMain"),
            (['powershell', '-Command',
              'Set-ItemProperty -Path "HKCU:\\Control Panel\\Desktop" -Name "MenuShowDelay" -Value 0'],
             "Menu delay: 0ms"),
            (['powershell', '-Command',
              'Set-ItemProperty -Path "HKCU:\\Control Panel\\Desktop" -Name "WaitToKillAppTimeout" -Value 2000'],
             "App kill timeout: 2s"),
        ]
        for cmd_args, label in tweaks:
            try:
                subprocess.run(cmd_args, capture_output=True, timeout=15)
                print(f"  {Fore.GREEN}[OK] {Fore.WHITE}{label}")
            except Exception as e:
                print(f"  {Fore.RED}[FAIL] {Fore.WHITE}{label}: {e}")
        self._ok("Tweaks applied. Some may require restart.")

    def cmd_closeall(self):
        self._warn("Closing all user applications...")
        skipped = {'explorer.exe', 'taskmgr.exe', 'python.exe', 'python3.exe',
                   'cmd.exe', 'powershell.exe', 'conhost.exe', 'svchost.exe'}
        closed = 0
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['pid'] == current_pid:
                    continue
                if proc.info['name'].lower() in skipped:
                    continue
                proc.terminate()
                closed += 1
                print(f"  {Fore.YELLOW}Closed: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        self._ok(f"Closed {closed} application(s).")

    def cmd_who_called_me(self):
        try:
            self._info("Checking camera/microphone access history...")
            reg_paths = [
                (r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam", "CAMERA"),
                (r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone", "MICROPHONE"),
            ]
            events = []
            for reg_path, dtype in reg_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            sub_name = winreg.EnumKey(key, i)
                            sub = winreg.OpenKey(key, sub_name)
                            start_val = winreg.QueryValueEx(sub, "LastUsedTimeStart")[0]
                            if start_val > 0:
                                dt = datetime.fromtimestamp(start_val / 10_000_000 - 11_644_473_600)
                                events.append({'app': sub_name.replace('.exe', ''), 'device': dtype, 'time': dt})
                            winreg.CloseKey(sub)
                        except Exception:
                            pass
                    winreg.CloseKey(key)
                except Exception:
                    pass

            events.sort(key=lambda x: x['time'], reverse=True)
            self._sep("DEVICE ACCESS HISTORY")
            if events:
                for ev in events[:20]:
                    color = Fore.RED if ev['device'] == "CAMERA" else Fore.CYAN
                    print(f"  {color}[{ev['device']:<11}] {Fore.WHITE}{ev['app']:<30} {ev['time'].strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                self._warn("No access history found.")
            self._sep()
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── power options ────────────────────────────────────

    def cmd_shutdown(self):
        self._warn("Shutting down in 5 seconds... Press Ctrl+C to cancel.")
        try:
            for i in range(5, 0, -1):
                sys.stdout.write(f"\r{Fore.YELLOW}Shutdown in {i}s... ")
                sys.stdout.flush()
                time.sleep(1)
            os.system("shutdown /s /t 0")
        except KeyboardInterrupt:
            print(f"\n{Fore.GREEN}Shutdown cancelled.")

    def cmd_sleep(self):
        self._info("Putting computer to sleep...")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    def cmd_logout(self):
        self._warn("Logging out in 3 seconds...")
        time.sleep(3)
        os.system("shutdown /l")

    # ─────────────────────── monitoring ───────────────────────────────────────

    def _check_device_usage(self, device_type: str):
        reg_map = {
            'camera': r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",
            'microphone': r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone",
        }
        reg_path = reg_map.get(device_type.lower())
        if not reg_path:
            self._err("Unknown device type.")
            return
        self._info(f"Checking {device_type} usage...")
        now = datetime.now()
        active = []
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    sub_name = winreg.EnumKey(key, i)
                    sub = winreg.OpenKey(key, sub_name)
                    try:
                        start_raw = winreg.QueryValueEx(sub, "LastUsedTimeStart")[0]
                        stop_raw  = winreg.QueryValueEx(sub, "LastUsedTimeStop")[0]
                        start_dt  = datetime.fromtimestamp(start_raw / 10_000_000 - 11_644_473_600)
                        stop_dt   = datetime.fromtimestamp(stop_raw  / 10_000_000 - 11_644_473_600)
                        if stop_raw <= start_raw and (now - start_dt).seconds < 3600:
                            active.append(sub_name)
                    except Exception:
                        pass
                    winreg.CloseKey(sub)
                except Exception:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            self._err(str(e))
            return

        self._sep(f"{device_type.upper()} USAGE")
        if active:
            for app in active:
                print(f"  {Fore.RED}[ACTIVE] {Fore.WHITE}{app}")
        else:
            self._ok(f"No apps currently detected using {device_type}.")
        self._sep()

    def cmd_cam_check(self):
        self._check_device_usage('camera')

    def cmd_mic_check(self):
        self._check_device_usage('microphone')

    def cmd_startup_check(self):
        self._info("Reading startup programs...")
        startup_keys = [
            (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
        ]
        self._sep("STARTUP PROGRAMS")
        for hive, path in startup_keys:
            hive_name = "HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM"
            try:
                key = winreg.OpenKey(hive, path)
                count = winreg.QueryInfoKey(key)[1]
                for i in range(count):
                    try:
                        name, val, _ = winreg.EnumValue(key, i)
                        print(f"  {Fore.CYAN}[{hive_name}] {Fore.WHITE}{name:<30} {Fore.YELLOW}{val[:60]}")
                    except Exception:
                        pass
                winreg.CloseKey(key)
            except Exception:
                pass
        startup_folder = Path(f"C:\\Users\\{self.username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        if startup_folder.exists():
            for item in startup_folder.iterdir():
                print(f"  {Fore.CYAN}[Folder] {Fore.WHITE}{item.name}")
        self._sep()

    def cmd_activeapps(self):
        self._info("Running applications:")
        self._sep("ACTIVE APPLICATIONS")
        seen = set()
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info']):
            try:
                name = proc.info['name']
                if name in seen:
                    continue
                seen.add(name)
                cpu = proc.cpu_percent(interval=0)
                mem = proc.info['memory_info'].rss / (1024**2) if proc.info['memory_info'] else 0
                print(f"  {Fore.CYAN}{name:<35} {Fore.GREEN}CPU:{cpu:5.1f}% {Fore.YELLOW}MEM:{mem:6.1f}MB")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        self._sep()

    def cmd_autorun(self, state: str):
        state = state.lower()
        if state not in ('on', 'off'):
            self._err("Usage: autorun <on/off>")
            return
        try:
            script_path = str(Path(sys.argv[0]).resolve())
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            if state == 'on':
                winreg.SetValueEx(key, "EUFTerminal", 0, winreg.REG_SZ,
                                  f'"{sys.executable}" "{script_path}"')
                self._ok("EUF Terminal added to startup.")
            else:
                try:
                    winreg.DeleteValue(key, "EUFTerminal")
                    self._ok("EUF Terminal removed from startup.")
                except FileNotFoundError:
                    self._warn("Not found in startup.")
            winreg.CloseKey(key)
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── process tree & ports ─────────────────────────────

    def cmd_process_tree(self):
        self._info("Building process tree...")
        try:
            procs = {}
            children = {}
            for proc in psutil.process_iter(['pid', 'ppid', 'name', 'status', 'cpu_percent', 'memory_info']):
                try:
                    info = proc.info
                    procs[info['pid']] = info
                    children.setdefault(info['ppid'], []).append(info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            def render(pid, prefix="", is_last=True):
                proc = procs.get(pid)
                if not proc:
                    return
                connector = "└─ " if is_last else "├─ "
                mem_mb = (proc['memory_info'].rss / (1024**2)) if proc.get('memory_info') else 0
                name   = proc.get('name') or '?'
                status = proc.get('status') or ''
                status_color = Fore.GREEN if status == 'running' else Fore.YELLOW
                print(f"{Fore.CYAN}{prefix}{connector}{Fore.WHITE}{name:<28}"
                      f" {Fore.BLUE}PID:{Fore.WHITE}{pid:<7}"
                      f" {status_color}{status:<10}"
                      f" {Fore.YELLOW}{mem_mb:5.1f}MB{Style.RESET_ALL}")
                kids = children.get(pid, [])
                ext  = "   " if is_last else "│  "
                for i, child_pid in enumerate(kids):
                    render(child_pid, prefix + ext, i == len(kids) - 1)

            self._sep("PROCESS TREE  (name | PID | status | memory)")
            roots = [pid for pid in procs if procs[pid].get('ppid', 0) not in procs
                     or procs[pid].get('ppid', 0) == 0]
            roots = sorted(set(roots))
            for i, root_pid in enumerate(roots):
                render(root_pid, "", i == len(roots) - 1)
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_listening_ports(self):
        self._info("Scanning listening ports...")
        try:
            conns = psutil.net_connections(kind='inet')
            listening = [c for c in conns if c.status == psutil.CONN_LISTEN]
            if not listening:
                self._warn("No listening ports found.")
                return

            self._sep("LISTENING PORTS")
            print(f"  {Fore.CYAN}{'Port':<8} {'Proto':<7} {'Address':<22} {'PID':<8} {'Process'}{Style.RESET_ALL}")
            print(f"  {Fore.BLUE}{'-'*65}{Style.RESET_ALL}")

            seen = set()
            for c in sorted(listening, key=lambda x: x.laddr.port if x.laddr else 0):
                port  = c.laddr.port if c.laddr else '?'
                addr  = c.laddr.ip   if c.laddr else '?'
                proto = 'TCP' if c.type == socket.SOCK_STREAM else 'UDP'
                pid   = c.pid or 0
                key   = (port, proto)
                if key in seen:
                    continue
                seen.add(key)
                try:
                    pname = psutil.Process(pid).name() if pid else 'System'
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pname = 'N/A'
                port_color = Fore.GREEN if port < 1024 else Fore.YELLOW
                print(f"  {port_color}{port:<8}{Fore.WHITE}{proto:<7}{addr:<22}"
                      f"{Fore.BLUE}{pid:<8}{Fore.CYAN}{pname}{Style.RESET_ALL}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── utilities ────────────────────────────────────────

    def cmd_timer(self, unit: str, value: str):
        try:
            val = int(value)
            if val <= 0:
                raise ValueError("Must be positive")
            unit_map = {'h': 3600, 'm': 60, 's': 1}
            if unit.lower() not in unit_map:
                self._err("Unit must be h, m, or s.")
                return
            secs = val * unit_map[unit.lower()]
            self._info(f"Timer set for {val}{unit.lower()} ({secs}s). Press Ctrl+C to cancel.")
            try:
                for elapsed in range(secs + 1):
                    remaining = secs - elapsed
                    m, s = divmod(remaining, 60)
                    h, m = divmod(m, 60)
                    label = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
                    self.progress_bar(elapsed, secs, prefix=f"{Fore.MAGENTA}Timer:", suffix=label)
                    if elapsed < secs:
                        time.sleep(1)
                print()
                self._ok("Timer finished!")
                for _ in range(3):
                    print('\a', end='', flush=True)
                    time.sleep(0.3)
            except KeyboardInterrupt:
                print()
                self._warn("Timer cancelled.")
        except ValueError as e:
            self._err(f"Invalid value: {e}")
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── extra commands ───────────────────────────────────

    def cmd_sysinfo_full(self):
        try:
            self._sep("FULL SYSTEM SNAPSHOT")
            print(f"\n{Fore.YELLOW}[ OS ]{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}Name      {Fore.WHITE}{self._get_windows_version()}")
            print(f"  {Fore.CYAN}Platform  {Fore.WHITE}{platform.architecture()[0]}  |  {platform.machine()}")
            print(f"  {Fore.CYAN}Node      {Fore.WHITE}{socket.gethostname()}")

            print(f"\n{Fore.YELLOW}[ CPU ]{Style.RESET_ALL}")
            freq = psutil.cpu_freq()
            print(f"  {Fore.CYAN}Cores (physical) {Fore.WHITE}{psutil.cpu_count(logical=False)}")
            print(f"  {Fore.CYAN}Cores (logical)  {Fore.WHITE}{psutil.cpu_count(logical=True)}")
            if freq:
                print(f"  {Fore.CYAN}Freq current     {Fore.WHITE}{freq.current:.0f} MHz")
                print(f"  {Fore.CYAN}Freq max         {Fore.WHITE}{freq.max:.0f} MHz")
            temps = {}
            try:
                temps = psutil.sensors_temperatures()
            except Exception:
                pass
            if temps:
                for sensor, readings in temps.items():
                    for r in readings:
                        print(f"  {Fore.CYAN}Temp ({sensor})  {Fore.WHITE}{r.current}°C")

            print(f"\n{Fore.YELLOW}[ RAM ]{Style.RESET_ALL}")
            vm = psutil.virtual_memory()
            sw = psutil.swap_memory()
            print(f"  {Fore.CYAN}Total     {Fore.WHITE}{vm.total/(1024**3):.2f} GB")
            print(f"  {Fore.CYAN}Used      {Fore.WHITE}{vm.used/(1024**3):.2f} GB  ({vm.percent}%)")
            print(f"  {Fore.CYAN}Available {Fore.WHITE}{vm.available/(1024**3):.2f} GB")
            print(f"  {Fore.CYAN}Swap      {Fore.WHITE}{sw.used/(1024**3):.2f} / {sw.total/(1024**3):.2f} GB")

            print(f"\n{Fore.YELLOW}[ DISKS ]{Style.RESET_ALL}")
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    bar_len = 20
                    filled = int(bar_len * usage.percent / 100)
                    bar = f"{Fore.GREEN}{'#'*filled}{Fore.RED}{'-'*(bar_len-filled)}{Fore.WHITE}"
                    print(f"  {Fore.CYAN}{part.device:<6}{Fore.WHITE} [{bar}] "
                          f"{usage.percent:5.1f}%  "
                          f"{usage.used/(1024**3):.1f}/{usage.total/(1024**3):.1f} GB  "
                          f"{Fore.YELLOW}{part.fstype}")
                except PermissionError:
                    pass

            print(f"\n{Fore.YELLOW}[ NETWORK INTERFACES ]{Style.RESET_ALL}")
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            for iface, addr_list in addrs.items():
                st = stats.get(iface)
                up = f"{Fore.GREEN}UP" if st and st.isup else f"{Fore.RED}DOWN"
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        print(f"  {Fore.CYAN}{iface:<20}{Fore.WHITE}{addr.address:<18}{up}{Style.RESET_ALL}")

            print(f"\n{Fore.YELLOW}[ GPU ]{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}Name  {Fore.WHITE}{self._get_gpu()}")

            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_netstat(self):
        self._info("Reading network connections...")
        try:
            conns = psutil.net_connections(kind='inet')
            self._sep("NETWORK CONNECTIONS")
            print(f"  {Fore.CYAN}{'Proto':<6}{'Local':<26}{'Remote':<26}{'Status':<14}{'PID':<7}Process{Style.RESET_ALL}")
            print(f"  {Fore.BLUE}{'-'*90}{Style.RESET_ALL}")
            for c in sorted(conns, key=lambda x: x.laddr.port if x.laddr else 0):
                proto  = 'TCP' if c.type == socket.SOCK_STREAM else 'UDP'
                local  = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else '-'
                remote = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else '-'
                status = c.status or '-'
                pid    = c.pid or 0
                try:
                    pname = psutil.Process(pid).name() if pid else '-'
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pname = '-'
                s_color = Fore.GREEN if status == 'ESTABLISHED' else (
                          Fore.YELLOW if status == 'LISTEN' else Fore.WHITE)
                print(f"  {Fore.CYAN}{proto:<6}{Fore.WHITE}{local:<26}{remote:<26}"
                      f"{s_color}{status:<14}{Fore.BLUE}{pid:<7}{Fore.CYAN}{pname}{Style.RESET_ALL}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_kill(self, target: str):
        try:
            killed = 0
            try:
                pid = int(target)
                proc = psutil.Process(pid)
                name = proc.name()
                proc.kill()
                self._ok(f"Killed PID {pid} ({name})")
                return
            except ValueError:
                pass
            except psutil.NoSuchProcess:
                self._err(f"No process with PID {target}")
                return
            except psutil.AccessDenied:
                self._err(f"Access denied killing PID {target}. Try 'root' first.")
                return

            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == target.lower():
                        proc.kill()
                        print(f"  {Fore.GREEN}Killed: {Fore.WHITE}{proc.info['name']} "
                              f"(PID {proc.info['pid']})")
                        killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if killed == 0:
                self._err(f"No process found named '{target}'")
            else:
                self._ok(f"Killed {killed} process(es).")
        except Exception as e:
            self._err(str(e))

    def cmd_env(self, var: str = None):
        self._sep("ENVIRONMENT VARIABLES")
        env = os.environ
        items = sorted(env.items())
        if var:
            items = [(k, v) for k, v in items if var.lower() in k.lower()]
            if not items:
                self._warn(f"No variable matching '{var}'")
                return
        for k, v in items:
            print(f"  {Fore.CYAN}{k:<35}{Fore.WHITE}{v[:80]}")
        self._sep()

    def cmd_hash_file(self, name: str):
        import hashlib
        try:
            target = self._resolve(name)
            if not target.exists() or not target.is_file():
                self._err(f"File not found: {name}")
                return
            self._info(f"Hashing: {Fore.YELLOW}{target.name}")
            data = target.read_bytes()
            self._sep(f"HASHES: {target.name}")
            print(f"  {Fore.CYAN}MD5    {Fore.WHITE}{hashlib.md5(data).hexdigest()}")
            print(f"  {Fore.CYAN}SHA1   {Fore.WHITE}{hashlib.sha1(data).hexdigest()}")
            print(f"  {Fore.CYAN}SHA256 {Fore.WHITE}{hashlib.sha256(data).hexdigest()}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_clipboard(self, action: str = None, text: str = None):
        try:
            import subprocess as sp
            if not action or action.lower() == 'get':
                r = sp.run(['powershell', '-Command', 'Get-Clipboard'],
                           capture_output=True, text=True)
                content = r.stdout.strip()
                self._sep("CLIPBOARD CONTENTS")
                print(f"{Fore.WHITE}{content if content else '(empty)'}")
                self._sep()
            elif action.lower() == 'set':
                if not text:
                    self._err("Usage: clipboard set <text>")
                    return
                sp.run(['powershell', '-Command', f'Set-Clipboard -Value "{text}"'],
                       capture_output=True)
                self._ok("Clipboard updated.")
            elif action.lower() == 'clear':
                sp.run(['powershell', '-Command', 'Set-Clipboard -Value ""'],
                       capture_output=True)
                self._ok("Clipboard cleared.")
            else:
                self._err("Usage: clipboard [get|set <text>|clear]")
        except Exception as e:
            self._err(str(e))

    def cmd_sysmon(self):
        self._info("Live system monitor — Ctrl+C to stop.")
        try:
            while True:
                cpu   = psutil.cpu_percent(interval=0.5)
                vm    = psutil.virtual_memory()
                disk  = psutil.disk_io_counters()
                net   = psutil.net_io_counters()

                cpu_bar_len = 30
                cpu_filled  = int(cpu_bar_len * cpu / 100)
                ram_filled  = int(cpu_bar_len * vm.percent / 100)
                cpu_color   = Fore.GREEN if cpu < 50 else (Fore.YELLOW if cpu < 80 else Fore.RED)
                ram_color   = Fore.GREEN if vm.percent < 60 else (Fore.YELLOW if vm.percent < 85 else Fore.RED)

                cpu_bar = (f"{Fore.CYAN}[{cpu_color}{'#'*cpu_filled}"
                           f"{Fore.RED}{'-'*(cpu_bar_len-cpu_filled)}{Fore.CYAN}]")
                ram_bar = (f"{Fore.CYAN}[{ram_color}{'#'*ram_filled}"
                           f"{Fore.RED}{'-'*(cpu_bar_len-ram_filled)}{Fore.CYAN}]")

                disk_r = disk.read_bytes  / (1024**2) if disk else 0
                disk_w = disk.write_bytes / (1024**2) if disk else 0
                net_s  = net.bytes_sent   / (1024**2) if net else 0
                net_r  = net.bytes_recv   / (1024**2) if net else 0

                os.system('cls')
                print(f"{Fore.BLUE + Style.BRIGHT}  LIVE SYSTEM MONITOR  {Fore.YELLOW}(Ctrl+C to stop){Style.RESET_ALL}\n")
                print(f"  {Fore.CYAN}CPU  {cpu_bar} {cpu_color}{cpu:5.1f}%{Style.RESET_ALL}")
                print(f"  {Fore.CYAN}RAM  {ram_bar} {ram_color}{vm.percent:5.1f}%"
                      f"  {Fore.WHITE}{vm.used/(1024**3):.1f}/{vm.total/(1024**3):.1f} GB{Style.RESET_ALL}")
                print(f"\n  {Fore.YELLOW}Disk   read: {Fore.WHITE}{disk_r:8.1f} MB   "
                      f"{Fore.YELLOW}write: {Fore.WHITE}{disk_w:.1f} MB")
                print(f"  {Fore.YELLOW}Net    sent: {Fore.WHITE}{net_s:8.1f} MB   "
                      f"{Fore.YELLOW}recv:  {Fore.WHITE}{net_r:.1f} MB")
                time.sleep(0.5)
        except KeyboardInterrupt:
            os.system('cls')
            self._ok("Monitor stopped.")

    def cmd_encode(self, method: str = None, text: str = None):
        import base64
        try:
            from urllib.parse import quote, unquote
        except ImportError:
            quote = unquote = None

        if not method or not text:
            self._err("Usage: encode <base64|hex|url|decode> <text>")
            return

        method = method.lower()
        try:
            if method == 'base64':
                result = base64.b64encode(text.encode()).decode()
                print(f"  {Fore.CYAN}Base64: {Fore.GREEN}{result}")
            elif method == 'hex':
                result = text.encode().hex()
                print(f"  {Fore.CYAN}Hex:    {Fore.GREEN}{result}")
            elif method == 'url':
                result = quote(text) if quote else text
                print(f"  {Fore.CYAN}URL:    {Fore.GREEN}{result}")
            elif method == 'decode':
                parts = text.split(' ', 1)
                if len(parts) < 2:
                    self._err("Usage: encode decode <base64|hex|url> <data>")
                    return
                dtype, data = parts[0].lower(), parts[1]
                if dtype == 'base64':
                    result = base64.b64decode(data.encode()).decode(errors='replace')
                elif dtype == 'hex':
                    result = bytes.fromhex(data).decode(errors='replace')
                elif dtype == 'url':
                    result = unquote(data) if unquote else data
                else:
                    self._err(f"Unknown decode type: {dtype}")
                    return
                print(f"  {Fore.CYAN}Decoded: {Fore.GREEN}{result}")
            else:
                self._err(f"Unknown method '{method}'. Use: base64, hex, url, decode")
        except Exception as e:
            self._err(f"Encode/decode error: {e}")

    def cmd_ls(self):
        try:
            items = sorted(self.current_path.iterdir(),
                           key=lambda p: (not p.is_dir(), p.name.lower()))
            self._sep(f"CONTENTS: {self.current_path}")
            dirs  = [i for i in items if i.is_dir()]
            files = [i for i in items if i.is_file()]
            for d in dirs:
                print(f"  {Fore.BLUE}[DIR]  {Fore.CYAN}{d.name}{Style.RESET_ALL}")
            for f in files:
                try:
                    sz = f.stat().st_size
                    if sz >= 1024**2:
                        sz_str = f"{sz/(1024**2):.1f} MB"
                    elif sz >= 1024:
                        sz_str = f"{sz/1024:.1f} KB"
                    else:
                        sz_str = f"{sz} B"
                except Exception:
                    sz_str = "?"
                print(f"  {Fore.WHITE}[FILE] {Fore.YELLOW}{f.name:<40}{Fore.GREEN}{sz_str:>10}{Style.RESET_ALL}")
            print(f"\n  {Fore.CYAN}{len(dirs)} folder(s), {len(files)} file(s){Style.RESET_ALL}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_open(self, name: str):
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"Not found: {name}")
                return
            os.startfile(str(target))
            self._ok(f"Opened: {Fore.YELLOW}{target.name}")
        except Exception as e:
            self._err(str(e))

    def cmd_copy_file(self, src: str, dst: str):
        try:
            s = self._resolve(src)
            d = self._resolve(dst)
            if not s.exists():
                self._err(f"Source not found: {src}")
                return
            if s.is_file():
                shutil.copy2(str(s), str(d))
            else:
                shutil.copytree(str(s), str(d))
            self._ok(f"Copied: {Fore.YELLOW}{src} {Fore.WHITE}-> {Fore.CYAN}{dst}")
        except Exception as e:
            self._err(str(e))

    def cmd_touch(self, name: str):
        try:
            target = self._resolve(name)
            target.touch(exist_ok=True)
            self._ok(f"Touched: {Fore.YELLOW}{target.name}")
        except Exception as e:
            self._err(str(e))

    def cmd_write(self, name: str):
        try:
            target = self._resolve(name)
            mode = 'a' if target.exists() else 'w'
            action = "Appending to" if mode == 'a' else "Writing to"
            self._info(f"{action} '{name}'. Type 'END' on a new line when done, 'QUIT' to cancel.")
            lines = []
            while True:
                try:
                    line = input(f"{Fore.CYAN}> {Fore.WHITE}")
                except EOFError:
                    break
                if line.strip().upper() == 'END':
                    break
                if line.strip().upper() == 'QUIT':
                    self._info("Cancelled.")
                    return
                lines.append(line)
            content = '\n'.join(lines) + '\n'
            with open(target, mode, encoding='utf-8') as f:
                f.write(content)
            self._ok(f"Written {len(lines)} line(s) to '{name}'.")
        except Exception as e:
            self._err(str(e))

    def cmd_myip(self):
        try:
            self._sep("IP ADDRESSES")
            pub = requests.get('https://api.ipify.org', timeout=6).text.strip()
            print(f"  {Fore.CYAN}Public IP   {Fore.GREEN}{pub}")
            addrs = psutil.net_if_addrs()
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                        print(f"  {Fore.CYAN}Local  ({iface:<16}) {Fore.YELLOW}{addr.address}")
            self._sep()
        except requests.ConnectionError:
            self._err("No internet connection.")
        except Exception as e:
            self._err(str(e))

    def cmd_screenshot(self):
        try:
            try:
                from PIL import ImageGrab
            except ImportError:
                self._info("Installing Pillow...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                                       'Pillow', '--quiet'], timeout=60)
                from PIL import ImageGrab
            ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
            dest = self.current_path / f"screenshot_{ts}.png"
            img  = ImageGrab.grab()
            img.save(str(dest))
            self._ok(f"Screenshot saved: {Fore.YELLOW}{dest.name}")
        except Exception as e:
            self._err(str(e))

    def cmd_battery(self):
        try:
            batt = psutil.sensors_battery()
            if batt is None:
                self._warn("No battery detected (desktop PC or driver missing).")
                return
            pct    = batt.percent
            plugged = batt.power_plugged
            secs   = batt.secsleft
            pct_color = Fore.GREEN if pct > 50 else (Fore.YELLOW if pct > 20 else Fore.RED)
            bar_len   = 25
            filled    = int(bar_len * pct / 100)
            bar = (f"{Fore.CYAN}[{pct_color}{'#'*filled}"
                   f"{Fore.RED}{'-'*(bar_len-filled)}{Fore.CYAN}]")
            self._sep("BATTERY")
            print(f"  {Fore.CYAN}Charge    {bar} {pct_color}{pct:.1f}%{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}Plugged   {Fore.WHITE}{'Yes (charging)' if plugged else 'No'}")
            if not plugged and secs != psutil.POWER_TIME_UNKNOWN:
                h, rem = divmod(secs, 3600)
                m = rem // 60
                print(f"  {Fore.CYAN}Remaining {Fore.WHITE}{h}h {m}m")
            self._sep()
        except Exception as e:
            self._err(str(e))

    # ─────────────────────── quick navigation ─────────────────────────────────

    def _goto(self, folder: str):
        candidates = [
            Path(f"C:\\Users\\{self.username}\\{folder}"),
            Path(os.environ.get('USERPROFILE', '')) / folder,
        ]
        for p in candidates:
            if p.exists():
                os.chdir(p)
                self.current_path = p
                self._ok(f"Moved to: {Fore.YELLOW}{p}")
                return
        self._err(f"Folder '{folder}' not found.")

    def cmd_desktop(self):
        self._goto("Desktop")

    def cmd_downloads(self):
        self._goto("Downloads")

    def cmd_documents(self):
        self._goto("Documents")

    def cmd_music(self):
        self._goto("Music")

    def cmd_pictures(self):
        self._goto("Pictures")

    def cmd_videos(self):
        self._goto("Videos")

    def cmd_appdata(self):
        p = Path(os.environ.get('APPDATA', f"C:\\Users\\{self.username}\\AppData\\Roaming"))
        if p.exists():
            os.chdir(p)
            self.current_path = p
            self._ok(f"Moved to: {Fore.YELLOW}{p}")
        else:
            self._err("AppData not found.")

    # ─────────────────────── system tools ─────────────────────────────────────

    def cmd_taskmgr(self):
        try:
            subprocess.Popen(['taskmgr'])
            self._ok("Task Manager opened.")
        except Exception as e:
            self._err(str(e))

    def cmd_services(self):
        self._info("Reading services...")
        try:
            r = subprocess.run(
                ['powershell', '-Command',
                 'Get-Service | Select-Object Name,Status,DisplayName | Sort-Object Status'],
                capture_output=True, text=True, timeout=20)
            if r.returncode != 0:
                self._err("Could not query services.")
                return
            self._sep("WINDOWS SERVICES")
            for line in r.stdout.strip().splitlines()[3:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(None, 2)
                if len(parts) < 2:
                    continue
                name, status = parts[0], parts[1]
                disp = parts[2] if len(parts) > 2 else ''
                color = Fore.GREEN if status == 'Running' else Fore.RED
                print(f"  {color}{status:<12}{Fore.WHITE}{name:<35}{Fore.YELLOW}{disp}")
            self._sep()
        except subprocess.TimeoutExpired:
            self._err("Query timed out.")
        except Exception as e:
            self._err(str(e))

    def cmd_service_ctrl(self, action: str, name: str):
        action = action.lower()
        if action not in ('start', 'stop', 'restart'):
            self._err("Usage: service <start|stop|restart> <name>")
            return
        try:
            self._info(f"{action.capitalize()}ing service '{name}'...")
            r = subprocess.run(
                ['powershell', '-Command', f'{action.capitalize()}-Service -Name "{name}"'],
                capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                self._ok(f"Service '{name}' {action}ed.")
            else:
                self._err(r.stderr.strip() or f"Failed to {action} service '{name}'.")
        except subprocess.TimeoutExpired:
            self._err("Timed out.")
        except Exception as e:
            self._err(str(e))

    def cmd_regedit_read(self, path: str):
        hive_map = {
            'HKCU': winreg.HKEY_CURRENT_USER,
            'HKLM': winreg.HKEY_LOCAL_MACHINE,
            'HKCR': winreg.HKEY_CLASSES_ROOT,
            'HKU':  winreg.HKEY_USERS,
        }
        try:
            parts = path.replace('/', '\\').split('\\', 1)
            if len(parts) < 2 or parts[0].upper() not in hive_map:
                self._err("Format: regedit <HKCU|HKLM|HKCR>\\path\\to\\key")
                return
            hive   = hive_map[parts[0].upper()]
            subkey = parts[1]
            key    = winreg.OpenKey(hive, subkey)
            self._sep(f"REGISTRY: {path}")
            i = 0
            while True:
                try:
                    name, data, dtype = winreg.EnumValue(key, i)
                    print(f"  {Fore.CYAN}{name or '(Default)':<35}{Fore.WHITE}{str(data)[:60]}")
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
            self._sep()
        except FileNotFoundError:
            self._err(f"Key not found: {path}")
        except PermissionError:
            self._err("Access denied. Try 'root' first.")
        except Exception as e:
            self._err(str(e))

    def cmd_hosts(self):
        hosts_path = Path(r"C:\Windows\System32\drivers\etc\hosts")
        try:
            if not hosts_path.exists():
                self._err("Hosts file not found.")
                return
            self._sep("HOSTS FILE")
            lines = hosts_path.read_text(encoding='utf-8', errors='replace').splitlines()
            for line in lines:
                if line.startswith('#'):
                    print(f"  {Fore.BLUE}{line}{Style.RESET_ALL}")
                elif line.strip():
                    print(f"  {Fore.GREEN}{line}{Style.RESET_ALL}")
            self._sep()
        except PermissionError:
            self._err("Access denied reading hosts file.")
        except Exception as e:
            self._err(str(e))

    def cmd_traceroute(self, host: str):
        self._info(f"Tracing route to {Fore.YELLOW}{host}{Fore.WHITE}...")
        try:
            subprocess.call(['tracert', '-d', '-h', '20', host])
        except Exception as e:
            self._err(str(e))

    def cmd_flush_dns(self):
        try:
            r = subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
            if r.returncode == 0:
                self._ok("DNS cache flushed.")
            else:
                self._err(r.stderr.strip())
        except Exception as e:
            self._err(str(e))

    def cmd_ip_config(self):
        try:
            r = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            self._sep("IPCONFIG /ALL")
            print(f"{Fore.WHITE}{r.stdout}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_count_files(self, directory: str = None):
        target = self._resolve(directory) if directory else self.current_path
        if not target.is_dir():
            self._err(f"Not a directory: {target}")
            return
        self._info(f"Counting in '{target}'...")
        try:
            files = dirs = total_size = 0
            ext_counts: dict = {}
            for item in target.rglob('*'):
                try:
                    if item.is_file():
                        files += 1
                        sz = item.stat().st_size
                        total_size += sz
                        ext = item.suffix.lower() or '(no ext)'
                        ext_counts[ext] = ext_counts.get(ext, 0) + 1
                    elif item.is_dir():
                        dirs += 1
                except PermissionError:
                    pass
            self._sep("COUNT")
            print(f"  {Fore.CYAN}Files       {Fore.WHITE}{files:,}")
            print(f"  {Fore.CYAN}Folders     {Fore.WHITE}{dirs:,}")
            mb = total_size / (1024**2)
            print(f"  {Fore.CYAN}Total size  {Fore.WHITE}{mb:.2f} MB")
            if ext_counts:
                top = sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:8]
                print(f"\n  {Fore.YELLOW}Top extensions:")
                for ext, cnt in top:
                    print(f"    {Fore.CYAN}{ext:<15}{Fore.WHITE}{cnt:,}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_find_large(self, directory: str = None, min_mb: str = "50"):
        target = self._resolve(directory) if directory else self.current_path
        if not target.is_dir():
            self._err(f"Not a directory: {target}")
            return
        try:
            threshold = float(min_mb) * 1024 * 1024
        except ValueError:
            self._err("min_mb must be a number.")
            return
        self._info(f"Searching for files > {min_mb} MB in '{target}'...")
        found = []
        try:
            for f in target.rglob('*'):
                try:
                    if f.is_file() and f.stat().st_size >= threshold:
                        found.append((f.stat().st_size, f))
                except PermissionError:
                    pass
        except Exception as e:
            self._err(str(e))
            return
        found.sort(reverse=True)
        self._sep(f"LARGE FILES (> {min_mb} MB)")
        if not found:
            self._warn("No large files found.")
        else:
            for sz, p in found[:30]:
                mb = sz / (1024**2)
                print(f"  {Fore.YELLOW}{mb:8.1f} MB  {Fore.WHITE}{p}")
        self._sep()

    def cmd_recent(self):
        try:
            items = []
            for f in self.current_path.rglob('*'):
                try:
                    if f.is_file():
                        items.append((f.stat().st_mtime, f))
                except PermissionError:
                    pass
            items.sort(reverse=True)
            self._sep("RECENTLY MODIFIED FILES")
            for mtime, f in items[:20]:
                dt = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                print(f"  {Fore.CYAN}{dt}  {Fore.WHITE}{f}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_calc(self, expr: str):
        import math, operator
        allowed = {
            'abs': abs, 'round': round, 'min': min, 'max': max, 'pow': pow,
            'sqrt': math.sqrt, 'ceil': math.ceil, 'floor': math.floor,
            'log': math.log, 'log10': math.log10, 'sin': math.sin,
            'cos': math.cos, 'tan': math.tan, 'pi': math.pi, 'e': math.e,
        }
        try:
            result = eval(expr, {"__builtins__": {}}, allowed)
            print(f"  {Fore.CYAN}{expr} {Fore.WHITE}= {Fore.GREEN}{result}{Style.RESET_ALL}")
        except ZeroDivisionError:
            self._err("Division by zero.")
        except Exception:
            self._err(f"Invalid expression: {expr}")

    def cmd_note(self, action: str = None, *args):
        notes_file = self.home_path / '.euf_notes.txt'
        action = (action or 'list').lower()
        try:
            if action == 'add':
                text = ' '.join(args)
                if not text:
                    self._err("Usage: note add <text>")
                    return
                ts = datetime.now().strftime('%Y-%m-%d %H:%M')
                with open(notes_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{ts}] {text}\n")
                self._ok("Note saved.")
            elif action == 'list':
                if not notes_file.exists() or not notes_file.read_text(encoding='utf-8').strip():
                    self._warn("No notes yet. Use 'note add <text>'.")
                    return
                self._sep("NOTES")
                lines = notes_file.read_text(encoding='utf-8').splitlines()
                for line in lines:
                    print(f"  {Fore.CYAN}{line}{Style.RESET_ALL}")
                self._sep()
            elif action == 'clear':
                if notes_file.exists():
                    notes_file.unlink()
                self._ok("All notes cleared.")
            else:
                self._err("Usage: note <add|list|clear>")
        except Exception as e:
            self._err(str(e))

    def cmd_alias_run(self, name: str, *cmd_parts):
        if not hasattr(self, '_aliases'):
            self._aliases: dict = {}
        name_l = name.lower()
        if name_l == 'list':
            if not self._aliases:
                self._warn("No aliases defined.")
            else:
                self._sep("ALIASES")
                for k, v in self._aliases.items():
                    print(f"  {Fore.CYAN}{k:<20}{Fore.WHITE}{v}")
                self._sep()
        elif name_l == 'del':
            target_alias = cmd_parts[0] if cmd_parts else ''
            if target_alias in self._aliases:
                del self._aliases[target_alias]
                self._ok(f"Alias '{target_alias}' removed.")
            else:
                self._err(f"Alias '{target_alias}' not found.")
        elif cmd_parts:
            self._aliases[name_l] = ' '.join(cmd_parts)
            self._ok(f"Alias '{name_l}' -> '{self._aliases[name_l]}'")
        else:
            self._err("Usage: alias <name> <command>  |  alias list  |  alias del <name>")

    def cmd_diskusage(self):
        self._sep("DISK USAGE")
        try:
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    bar_len = 25
                    filled  = int(bar_len * usage.percent / 100)
                    color   = (Fore.GREEN if usage.percent < 70
                               else Fore.YELLOW if usage.percent < 90
                               else Fore.RED)
                    bar = (f"{Fore.CYAN}[{color}{'#'*filled}"
                           f"{Fore.RED}{'-'*(bar_len-filled)}{Fore.CYAN}]")
                    free_gb  = usage.free  / (1024**3)
                    total_gb = usage.total / (1024**3)
                    print(f"  {Fore.YELLOW}{part.device:<6}{Fore.WHITE} {bar} "
                          f"{color}{usage.percent:5.1f}%  "
                          f"{Fore.WHITE}{free_gb:.1f} GB free / {total_gb:.1f} GB"
                          f"  {Fore.BLUE}{part.fstype}{Style.RESET_ALL}")
                except (PermissionError, OSError):
                    pass
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_uptime(self):
        try:
            boot   = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot
            days   = uptime.days
            hours, rem = divmod(uptime.seconds, 3600)
            mins  = rem // 60
            self._sep("UPTIME")
            print(f"  {Fore.CYAN}Boot time  {Fore.WHITE}{boot.strftime('%Y-%m-%d  %H:%M:%S')}")
            print(f"  {Fore.CYAN}Uptime     {Fore.WHITE}{days}d  {hours}h  {mins}m")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_clear_history(self):
        self._history.clear()
        self._ok("History cleared.")

    def cmd_ping_sweep(self, subnet: str = None):
        try:
            if not subnet:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                subnet = '.'.join(local_ip.split('.')[:3])
            self._info(f"Sweeping {subnet}.1-254 ...")
            found = []
            lock  = threading.Lock()

            def _ping(ip):
                r = subprocess.run(
                    ['ping', '-n', '1', '-w', '400', ip],
                    capture_output=True)
                if r.returncode == 0:
                    with lock:
                        found.append(ip)

            threads = [threading.Thread(target=_ping,
                       args=(f"{subnet}.{i}",), daemon=True)
                       for i in range(1, 255)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=3)

            self._sep(f"PING SWEEP: {subnet}.0/24")
            if found:
                for ip in sorted(found, key=lambda x: int(x.split('.')[-1])):
                    try:
                        name = socket.gethostbyaddr(ip)[0]
                    except Exception:
                        name = ''
                    print(f"  {Fore.GREEN}[UP]  {Fore.CYAN}{ip:<18}{Fore.WHITE}{name}")
            else:
                self._warn("No hosts responded.")
            print(f"\n  {Fore.YELLOW}{len(found)} host(s) found.")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_open_terminal_here(self):
        try:
            subprocess.Popen(['cmd'], cwd=str(self.current_path))
            self._ok(f"New CMD opened at: {Fore.YELLOW}{self.current_path}")
        except Exception as e:
            self._err(str(e))

    def cmd_file_diff(self, file1: str, file2: str):
        import difflib
        try:
            t1 = self._resolve(file1)
            t2 = self._resolve(file2)
            for f, n in [(t1, file1), (t2, file2)]:
                if not f.exists():
                    self._err(f"File not found: {n}")
                    return
            lines1 = t1.read_text(encoding='utf-8', errors='replace').splitlines()
            lines2 = t2.read_text(encoding='utf-8', errors='replace').splitlines()
            diff   = list(difflib.unified_diff(
                lines1, lines2,
                fromfile=file1, tofile=file2, lineterm=''))
            self._sep(f"DIFF: {file1}  vs  {file2}")
            if not diff:
                self._ok("Files are identical.")
            else:
                for line in diff:
                    if line.startswith('+') and not line.startswith('+++'):
                        print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                    elif line.startswith('-') and not line.startswith('---'):
                        print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                    elif line.startswith('@@'):
                        print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.WHITE}{line}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_zip_list(self, name: str):
        try:
            target = self._resolve(name)
            if not target.exists():
                self._err(f"File not found: {name}")
                return
            with zipfile.ZipFile(target, 'r') as zf:
                infos = zf.infolist()
            self._sep(f"ZIP CONTENTS: {target.name}  ({len(infos)} items)")
            total = 0
            for info in sorted(infos, key=lambda x: x.filename):
                sz   = info.file_size
                total += sz
                sz_s = (f"{sz/(1024**2):.1f}MB" if sz >= 1024**2
                        else f"{sz//1024}KB" if sz >= 1024 else f"{sz}B")
                color = Fore.BLUE if info.filename.endswith('/') else Fore.WHITE
                print(f"  {color}{info.filename:<50}{Fore.GREEN}{sz_s:>8}{Style.RESET_ALL}")
            print(f"\n  {Fore.YELLOW}Total uncompressed: {total/(1024**2):.2f} MB")
            self._sep()
        except zipfile.BadZipFile:
            self._err("Not a valid zip file.")
        except Exception as e:
            self._err(str(e))

    def cmd_run(self, filename: str = None):
        if not filename:
            runnable_exts = {'.py', '.js', '.html', '.htm', '.bat',
                             '.cmd', '.ps1', '.exe', '.vbs', '.jar'}
            items = [f for f in self.current_path.iterdir()
                     if f.is_file() and f.suffix.lower() in runnable_exts]
            if not items:
                self._warn("No runnable files found in current directory.")
                return
            self._sep("RUNNABLE FILES")
            for i, f in enumerate(items, 1):
                print(f"  {Fore.CYAN}{i:>2}. {Fore.WHITE}{f.name}")
            self._sep()
            try:
                choice = input(f"{Fore.CYAN}Pick number (or name): {Fore.WHITE}").strip()
            except (EOFError, KeyboardInterrupt):
                return
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    filename = items[idx].name
                else:
                    self._err("Invalid number.")
                    return
            else:
                filename = choice

        target = self._resolve(filename)
        if not target.exists():
            self._err(f"File not found: {filename}")
            return
        if not target.is_file():
            self._err(f"Not a file: {filename}")
            return

        ext = target.suffix.lower()
        self._info(f"Running: {Fore.YELLOW}{target.name}")
        sep = f"{Fore.BLUE}{'─'*50}{Style.RESET_ALL}"

        try:
            if ext == '.py':
                print(sep)
                r = subprocess.run([sys.executable, str(target)],
                                   cwd=str(target.parent), timeout=300)
                print(sep)
                code = r.returncode
            elif ext == '.js':
                print(sep)
                r = subprocess.run(['cscript', '//Nologo', str(target)],
                                   cwd=str(target.parent), timeout=60)
                print(sep)
                code = r.returncode
            elif ext in ('.html', '.htm'):
                os.startfile(str(target))
                self._ok(f"Opened in browser: {target.name}")
                return
            elif ext in ('.bat', '.cmd'):
                print(sep)
                r = subprocess.run(['cmd', '/c', str(target)],
                                   cwd=str(target.parent), timeout=120)
                print(sep)
                code = r.returncode
            elif ext == '.ps1':
                print(sep)
                r = subprocess.run(
                    ['powershell', '-ExecutionPolicy', 'Bypass',
                     '-File', str(target)],
                    cwd=str(target.parent), timeout=120)
                print(sep)
                code = r.returncode
            elif ext == '.exe':
                print(sep)
                r = subprocess.run([str(target)],
                                   cwd=str(target.parent), timeout=300)
                print(sep)
                code = r.returncode
            elif ext == '.vbs':
                print(sep)
                r = subprocess.run(['cscript', '//Nologo', str(target)],
                                   cwd=str(target.parent), timeout=60)
                print(sep)
                code = r.returncode
            else:
                os.startfile(str(target))
                self._ok(f"Opened: {target.name}")
                return

            if code == 0:
                self._ok(f"'{target.name}' finished  (exit 0).")
            else:
                self._warn(f"'{target.name}' exited with code {code}.")

        except subprocess.TimeoutExpired:
            self._err("Execution timed out.")
        except FileNotFoundError as e:
            self._err(f"Runtime not found: {e}")
        except PermissionError:
            self._err("Permission denied. Try 'root' first.")
        except Exception as e:
            self._err(str(e))

    def cmd_history(self, n: str = None):
        history = getattr(self, '_history', [])
        if not history:
            self._warn("No history yet.")
            return
        limit = int(n) if n and n.isdigit() else len(history)
        self._sep("COMMAND HISTORY")
        start = max(0, len(history) - limit)
        for i, cmd in enumerate(history[start:], start + 1):
            print(f"  {Fore.CYAN}{i:>4}  {Fore.WHITE}{cmd}")
        self._sep()

    # ─────────────────────── new commands ────────────────────────────────────

    def cmd_whoami(self):
        try:
            self._sep("WHOAMI")
            print(f"  {Fore.CYAN}User      {Fore.WHITE}{self.username}")
            print(f"  {Fore.CYAN}Hostname  {Fore.WHITE}{self.hostname}")
            print(f"  {Fore.CYAN}Home      {Fore.WHITE}{self.home_path}")
            is_adm = self._is_admin()
            priv_color = Fore.RED if is_adm else Fore.GREEN
            print(f"  {Fore.CYAN}Admin     {priv_color}{'YES - Elevated' if is_adm else 'No'}{Style.RESET_ALL}")
            r = subprocess.run(['net', 'user', self.username],
                               capture_output=True, text=True, timeout=8)
            for line in r.stdout.splitlines():
                if 'Local Group' in line or 'Global Group' in line:
                    print(f"  {Fore.CYAN}Groups    {Fore.WHITE}{line.split('*')[-1].strip()}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_path(self):
        self._sep("PATH")
        for p in os.environ.get('PATH', '').split(';'):
            p = p.strip()
            if not p:
                continue
            exists = Path(p).exists()
            color  = Fore.GREEN if exists else Fore.RED
            mark   = '' if exists else '  (not found)'
            print(f"  {color}{p}{Fore.YELLOW}{mark}{Style.RESET_ALL}")
        self._sep()

    def cmd_find_text(self, pattern: str, directory: str = None):
        target = self._resolve(directory) if directory else self.current_path
        if not target.is_dir():
            self._err(f"Not a directory: {target}")
            return
        self._info(f"Searching for '{Fore.YELLOW}{pattern}{Fore.WHITE}' in '{target}'...")
        found = 0
        try:
            for f in target.rglob('*'):
                if not f.is_file():
                    continue
                if f.suffix.lower() in {'.exe','.dll','.bin','.png','.jpg',
                                         '.jpeg','.gif','.zip','.mp3','.mp4'}:
                    continue
                try:
                    text = f.read_text(encoding='utf-8', errors='ignore')
                    hits = [i+1 for i, ln in enumerate(text.splitlines())
                            if pattern.lower() in ln.lower()]
                    if hits:
                        print(f"  {Fore.CYAN}{f}  {Fore.YELLOW}lines: {hits[:5]}")
                        found += 1
                except Exception:
                    pass
        except Exception as e:
            self._err(str(e))
            return
        self._ok(f"Found in {found} file(s).")

    def cmd_wlan_info(self):
        try:
            r = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'],
                               capture_output=True, text=True, timeout=8)
            self._sep("WI-FI INFO")
            for line in r.stdout.splitlines():
                line = line.strip()
                if not line or ':' not in line:
                    continue
                key, _, val = line.partition(':')
                key = key.strip()
                val = val.strip()
                if key and val:
                    print(f"  {Fore.CYAN}{key:<28}{Fore.WHITE}{val}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_proxy(self, action: str = None):
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path,
                                 0, winreg.KEY_READ | winreg.KEY_WRITE)
            action = (action or 'show').lower()
            if action == 'show':
                self._sep("PROXY SETTINGS")
                for field in ['ProxyEnable', 'ProxyServer', 'ProxyOverride']:
                    try:
                        val = winreg.QueryValueEx(key, field)[0]
                        print(f"  {Fore.CYAN}{field:<20}{Fore.WHITE}{val}")
                    except FileNotFoundError:
                        print(f"  {Fore.CYAN}{field:<20}{Fore.RED}(not set)")
                self._sep()
            elif action == 'off':
                winreg.SetValueEx(key, 'ProxyEnable', 0, winreg.REG_DWORD, 0)
                self._ok("Proxy disabled.")
            elif action == 'on':
                self._err("Usage: proxy on <host:port>")
            else:
                winreg.SetValueEx(key, 'ProxyServer', 0, winreg.REG_SZ, action)
                winreg.SetValueEx(key, 'ProxyEnable', 0, winreg.REG_DWORD, 1)
                self._ok(f"Proxy set to {action}")
            winreg.CloseKey(key)
        except PermissionError:
            self._err("Access denied. Try 'root' first.")
        except Exception as e:
            self._err(str(e))

    def cmd_startup_add(self, name: str, path: str):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, path)
            winreg.CloseKey(key)
            self._ok(f"'{name}' added to startup.")
        except PermissionError:
            self._err("Access denied. Try 'root' first.")
        except Exception as e:
            self._err(str(e))

    def cmd_startup_remove(self, name: str):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, name)
                self._ok(f"'{name}' removed from startup.")
            except FileNotFoundError:
                self._err(f"'{name}' not found in startup.")
            winreg.CloseKey(key)
        except Exception as e:
            self._err(str(e))

    def cmd_cpu_cores(self):
        self._info("Per-core CPU usage — Ctrl+C to stop.")
        try:
            while True:
                os.system('cls')
                cores = psutil.cpu_percent(interval=0.5, percpu=True)
                self._sep("CPU CORES")
                for i, pct in enumerate(cores):
                    bar_len = 30
                    filled  = int(bar_len * pct / 100)
                    color   = (Fore.GREEN if pct < 50
                               else Fore.YELLOW if pct < 80 else Fore.RED)
                    bar = (f"{Fore.CYAN}[{color}{'#'*filled}"
                           f"{Fore.RED}{'-'*(bar_len-filled)}{Fore.CYAN}]")
                    print(f"  {Fore.CYAN}Core {i:<3}{bar} {color}{pct:5.1f}%{Style.RESET_ALL}")
                freq = psutil.cpu_freq()
                if freq:
                    print(f"\n  {Fore.CYAN}Freq  {Fore.WHITE}{freq.current:.0f} MHz  (max {freq.max:.0f} MHz)")
                print(f"\n  {Fore.YELLOW}Ctrl+C to stop{Style.RESET_ALL}")
                self._sep()
        except KeyboardInterrupt:
            os.system('cls')
            self._ok("Stopped.")

    def cmd_tcp_block(self, port: str):
        try:
            port_int = int(port)
            rule_name = f"EUFBlock_{port_int}"
            r = subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name={rule_name}',
                'dir=in', 'action=block',
                'protocol=TCP', f'localport={port_int}'
            ], capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                self._ok(f"TCP port {port_int} blocked  (rule: {rule_name}).")
            else:
                self._err(r.stderr.strip() or "Failed. Try 'root' first.")
        except ValueError:
            self._err("Port must be a number.")
        except Exception as e:
            self._err(str(e))

    def cmd_tcp_unblock(self, port: str):
        try:
            port_int  = int(port)
            rule_name = f"EUFBlock_{port_int}"
            r = subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                f'name={rule_name}'
            ], capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                self._ok(f"TCP port {port_int} unblocked.")
            else:
                self._err(f"Rule '{rule_name}' not found or access denied.")
        except ValueError:
            self._err("Port must be a number.")
        except Exception as e:
            self._err(str(e))

    def cmd_mac_address(self):
        self._sep("MAC ADDRESSES")
        try:
            addrs = psutil.net_if_addrs()
            import psutil as _ps
            AF_LINK = _ps.AF_LINK
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == AF_LINK and addr.address:
                        print(f"  {Fore.CYAN}{iface:<25}{Fore.WHITE}{addr.address.upper()}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_installed_apps(self):
        self._info("Reading installed apps...")
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        apps = []
        for hive, path in reg_paths:
            try:
                key = winreg.OpenKey(hive, path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub_name = winreg.EnumKey(key, i)
                        sub = winreg.OpenKey(key, sub_name)
                        try:
                            name = winreg.QueryValueEx(sub, 'DisplayName')[0]
                            try:
                                ver = winreg.QueryValueEx(sub, 'DisplayVersion')[0]
                            except Exception:
                                ver = ''
                            apps.append((name.strip(), ver.strip()))
                        except Exception:
                            pass
                        winreg.CloseKey(sub)
                    except Exception:
                        pass
                winreg.CloseKey(key)
            except Exception:
                pass
        apps = sorted(set(apps), key=lambda x: x[0].lower())
        self._sep(f"INSTALLED APPS  ({len(apps)} total)")
        for name, ver in apps:
            print(f"  {Fore.CYAN}{name:<45}{Fore.WHITE}{ver}")
        self._sep()

    def cmd_windows_update(self):
        try:
            self._info("Checking for Windows Updates (may take a moment)...")
            r = subprocess.run(
                ['powershell', '-Command',
                 'Get-WindowsUpdate -ErrorAction SilentlyContinue 2>&1 | '
                 'Select-Object Title,Size | Format-Table -AutoSize'],
                capture_output=True, text=True, timeout=120)
            self._sep("WINDOWS UPDATES")
            out = r.stdout.strip()
            if out:
                print(f"{Fore.WHITE}{out}")
            else:
                self._ok("No pending updates found (or PSWindowsUpdate not installed).")
                self._info("Install it with:  Install-Module PSWindowsUpdate -Force")
            self._sep()
        except subprocess.TimeoutExpired:
            self._err("Update check timed out.")
        except Exception as e:
            self._err(str(e))

    def cmd_color(self, color_name: str = None):
        if not color_name or color_name.lower() == 'list':
            self._sep("AVAILABLE COLORS")
            for name, code in self.COLOR_MAP.items():
                print(f"  {code}{name}{Style.RESET_ALL}")
            self._sep()
            print(f"  {Fore.CYAN}Current color: {self.input_color}example text{Style.RESET_ALL}")
            return
        c = color_name.lower()
        if c not in self.COLOR_MAP:
            self._err(f"Unknown color '{c}'. Use: {', '.join(self.COLOR_MAP)}")
            return
        self.input_color = self.COLOR_MAP[c]
        self._ok(f"Input color set to: {self.input_color}{c}{Style.RESET_ALL}")

    def cmd_passwd(self, length: str = "16"):
        import secrets, string
        try:
            n = max(8, int(length))
        except ValueError:
            n = 16
        chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
        pwd = ''.join(secrets.choice(chars) for _ in range(n))
        self._sep("GENERATED PASSWORD")
        print(f"  {Fore.GREEN}{pwd}{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}Length: {Fore.WHITE}{n}  |  "
              f"{Fore.CYAN}Strength: {Fore.GREEN}Strong")
        try:
            subprocess.run(['powershell', '-Command',
                            f'Set-Clipboard -Value "{pwd}"'],
                           capture_output=True, timeout=5)
            print(f"  {Fore.YELLOW}(copied to clipboard)")
        except Exception:
            pass
        self._sep()

    def cmd_uuid(self):
        import uuid
        u = str(uuid.uuid4())
        print(f"  {Fore.GREEN}{u}{Style.RESET_ALL}")
        try:
            subprocess.run(['powershell', '-Command',
                            f'Set-Clipboard -Value "{u}"'],
                           capture_output=True, timeout=5)
            print(f"  {Fore.YELLOW}(copied to clipboard)")
        except Exception:
            pass

    def cmd_base_convert(self, value: str = None, from_base: str = None, to_base: str = None):
        if not all([value, from_base, to_base]):
            self._err("Usage: base <value> <from> <to>   e.g. base FF 16 10")
            return
        try:
            fb = int(from_base)
            tb = int(to_base)
            dec = int(value, fb)
            if tb == 2:
                result = bin(dec)[2:]
            elif tb == 8:
                result = oct(dec)[2:]
            elif tb == 10:
                result = str(dec)
            elif tb == 16:
                result = hex(dec)[2:].upper()
            else:
                result = ""
                n = dec
                while n:
                    result = str(n % tb) + result
                    n //= tb
                result = result or "0"
            self._sep("BASE CONVERSION")
            print(f"  {Fore.CYAN}Input  (base {fb}): {Fore.WHITE}{value}")
            print(f"  {Fore.CYAN}Output (base {tb}): {Fore.GREEN}{result}{Style.RESET_ALL}")
            if tb not in (2, 8, 10, 16):
                print(f"  {Fore.YELLOW}Dec: {dec}  Hex: {hex(dec)[2:].upper()}"
                      f"  Bin: {bin(dec)[2:]}")
            self._sep()
        except ValueError as e:
            self._err(f"Conversion error: {e}")

    def cmd_ping_latency(self, host: str = "8.8.8.8", count: str = "10"):
        try:
            n = max(3, int(count))
        except ValueError:
            n = 10
        self._info(f"Pinging {Fore.YELLOW}{host}{Fore.WHITE} x{n}...")
        latencies = []
        for _ in range(n):
            r = subprocess.run(
                ['ping', '-n', '1', host],
                capture_output=True, text=True, timeout=5)
            match = re.search(r'time[=<](\d+)ms', r.stdout)
            if match:
                latencies.append(int(match.group(1)))
            time.sleep(0.2)
        self._sep(f"PING STATS: {host}")
        if latencies:
            print(f"  {Fore.CYAN}Sent      {Fore.WHITE}{n}")
            print(f"  {Fore.CYAN}Received  {Fore.WHITE}{len(latencies)}")
            print(f"  {Fore.CYAN}Lost      {Fore.RED}{n - len(latencies)}")
            print(f"  {Fore.CYAN}Min       {Fore.GREEN}{min(latencies)} ms")
            print(f"  {Fore.CYAN}Max       {Fore.YELLOW}{max(latencies)} ms")
            avg = sum(latencies) / len(latencies)
            print(f"  {Fore.CYAN}Avg       {Fore.WHITE}{avg:.1f} ms")
            jitter = max(latencies) - min(latencies)
            print(f"  {Fore.CYAN}Jitter    {Fore.WHITE}{jitter} ms")
        else:
            self._err("Host unreachable.")
        self._sep()

    def cmd_sys_theme(self, theme: str = None):
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        dark_val  = {"dark": 0, "light": 1}
        theme = (theme or 'show').lower()
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path,
                                 0, winreg.KEY_READ | winreg.KEY_WRITE)
            if theme == 'show':
                apps = winreg.QueryValueEx(key, 'AppsUseLightTheme')[0]
                sys_ = winreg.QueryValueEx(key, 'SystemUsesLightTheme')[0]
                self._sep("WINDOWS THEME")
                print(f"  {Fore.CYAN}Apps mode    {Fore.WHITE}{'Light' if apps else 'Dark'}")
                print(f"  {Fore.CYAN}System mode  {Fore.WHITE}{'Light' if sys_ else 'Dark'}")
                self._sep()
            elif theme in ('dark', 'light'):
                v = dark_val[theme]
                winreg.SetValueEx(key, 'AppsUseLightTheme',   0, winreg.REG_DWORD, v)
                winreg.SetValueEx(key, 'SystemUsesLightTheme', 0, winreg.REG_DWORD, v)
                self._ok(f"Switched to {theme} mode. Restart Explorer to apply.")
            else:
                self._err("Usage: theme <dark|light|show>")
            winreg.CloseKey(key)
        except Exception as e:
            self._err(str(e))

    def cmd_network_speed_live(self):
        self._info("Live network speed — Ctrl+C to stop.")
        try:
            prev   = psutil.net_io_counters()
            prev_t = time.time()
            while True:
                time.sleep(1)
                curr  = psutil.net_io_counters()
                now   = time.time()
                dt    = max(now - prev_t, 0.001)
                dl_kb = (curr.bytes_recv - prev.bytes_recv) / dt / 1024
                ul_kb = (curr.bytes_sent - prev.bytes_sent) / dt / 1024
                dl_str = f"{dl_kb/1024:.2f} MB/s" if dl_kb >= 1024 else f"{dl_kb:.1f} KB/s"
                ul_str = f"{ul_kb/1024:.2f} MB/s" if ul_kb >= 1024 else f"{ul_kb:.1f} KB/s"
                bar_max  = 1024
                dl_fill  = min(30, int(30 * dl_kb / bar_max))
                ul_fill  = min(30, int(30 * ul_kb / bar_max))
                dl_bar   = (f"{Fore.CYAN}[{Fore.GREEN}{'#'*dl_fill}"
                            f"{Fore.RED}{'-'*(30-dl_fill)}{Fore.CYAN}]")
                ul_bar   = (f"{Fore.CYAN}[{Fore.YELLOW}{'#'*ul_fill}"
                            f"{Fore.RED}{'-'*(30-ul_fill)}{Fore.CYAN}]")
                total_r  = curr.bytes_recv / (1024**3)
                total_s  = curr.bytes_sent / (1024**3)
                os.system('cls')
                print(f"{Fore.BLUE + Style.BRIGHT}  LIVE NETWORK SPEED{Style.RESET_ALL}")
                print()
                print(f"  {Fore.GREEN}Download  {dl_bar}  {Fore.GREEN}{dl_str}{Style.RESET_ALL}")
                print(f"  {Fore.YELLOW}Upload    {ul_bar}  {Fore.YELLOW}{ul_str}{Style.RESET_ALL}")
                print()
                print(f"  {Fore.CYAN}Total recv: {Fore.WHITE}{total_r:.2f} GB   "
                      f"sent: {total_s:.2f} GB")
                print()
                print(f"  {Fore.YELLOW}Ctrl+C to stop{Style.RESET_ALL}")
                prev   = curr
                prev_t = now
        except KeyboardInterrupt:
            os.system('cls')
            self._ok("Monitor stopped.")
        except Exception as e:
            self._err(str(e))

    def cmd_file_type(self, name: str):
        SIGS = {
            b'\x89PNG':             'PNG image',
            b'\xff\xd8\xff':      'JPEG image',
            b'GIF8':                 'GIF image',
            b'%PDF':                 'PDF document',
            b'PK\x03\x04':        'ZIP / Office document',
            b'MZ':                   'Windows EXE/DLL',
            b'\x7fELF':            'ELF binary (Linux)',
            b'\xca\xfe\xba\xbe':'Java class file',
            b'\x1f\x8b':          'GZIP archive',
            b'Rar!':                 'RAR archive',
            b'\xff\xfe':          'UTF-16 LE text',
            b'\xfe\xff':          'UTF-16 BE text',
            b'\xef\xbb\xbf':     'UTF-8 BOM text',
            b'RIFF':                 'RIFF (WAV/AVI)',
            b'ID3':                  'MP3 audio',
            b'BM':                   'BMP image',
            b'OTTO':                 'OpenType font',
        }
        try:
            target = self._resolve(name)
            if not target.exists() or not target.is_file():
                self._err(f"File not found: {name}")
                return
            header = target.read_bytes()[:16]
            detected = "Unknown / text"
            for sig, label in SIGS.items():
                if header.startswith(sig):
                    detected = label
                    break
            size = target.stat().st_size
            self._sep(f"FILE TYPE: {target.name}")
            print(f"  {Fore.CYAN}Extension  {Fore.WHITE}{target.suffix or '(none)'}")
            print(f"  {Fore.CYAN}Type       {Fore.GREEN}{detected}{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}Size       {Fore.WHITE}{size:,} bytes")
            print(f"  {Fore.CYAN}Magic hex  {Fore.YELLOW}{header[:8].hex().upper()}")
            self._sep()
        except Exception as e:
            self._err(str(e))

    def cmd_watch(self, filename: str = None, interval: str = "2"):
        if not filename:
            self._err("Usage: watch <file> [interval]")
            return
        target = self._resolve(filename)
        if not target.exists() or not target.is_file():
            self._err(f"File not found: {filename}")
            return
        try:
            secs = max(0.5, float(interval))
        except ValueError:
            secs = 2.0
        self._info(f"Watching '{target.name}' every {secs}s — Ctrl+C to stop.")
        try:
            with open(target, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        print(f"{Fore.GREEN}{line}", end="", flush=True)
                    else:
                        time.sleep(secs)
        except KeyboardInterrupt:
            print()
            self._ok("Watch stopped.")
        except Exception as e:
            self._err(str(e))

    def cmd_colortest(self):
        self._sep("COLOR TEST")
        colors = [
            (Fore.RED,     'RED'),
            (Fore.GREEN,   'GREEN'),
            (Fore.YELLOW,  'YELLOW'),
            (Fore.BLUE,    'BLUE'),
            (Fore.MAGENTA, 'MAGENTA'),
            (Fore.CYAN,    'CYAN'),
            (Fore.WHITE,   'WHITE'),
        ]
        styles = [('Normal', ''), ('Bright', Style.BRIGHT)]
        for sname, scode in styles:
            row = f"  {Fore.CYAN}{sname:<8}{Style.RESET_ALL}  "
            for code, name in colors:
                row += f"{scode}{code}{'#'*8}  {Style.RESET_ALL}"
            print(row)
            row2 = f"           "
            for code, name in colors:
                row2 += f"{scode}{code}{name:<10}{Style.RESET_ALL}"
            print(row2)
        print()
        print(f"  {Fore.CYAN}Use 'color <name>' to set your input color.{Style.RESET_ALL}")
        self._sep()

    # ─────────────────────── startup manager ─────────────────────────────────

    def cmd_startup_manager(self):
        import winreg as _wr
        reg_paths = [
            (_wr.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKCU"),
            (_wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKLM"),
        ]
        while True:
            entries = []
            for hive, path, hname in reg_paths:
                try:
                    key = _wr.OpenKey(hive, path, 0, _wr.KEY_READ)
                    count = _wr.QueryInfoKey(key)[1]
                    for i in range(count):
                        try:
                            name, val, _ = _wr.EnumValue(key, i)
                            entries.append({'hive': hive, 'path': path, 'hname': hname,
                                            'name': name, 'val': val})
                        except Exception:
                            pass
                    _wr.CloseKey(key)
                except Exception:
                    pass
            sf = Path(f"C:\\Users\\{self.username}\\AppData\\Roaming\\Microsoft"
                      f"\\Windows\\Start Menu\\Programs\\Startup")
            folder_items = list(sf.iterdir()) if sf.exists() else []

            os.system('cls')
            self._sep("STARTUP MANAGER")
            print(f"  {Fore.YELLOW}Registry entries:{Style.RESET_ALL}")
            for i, e in enumerate(entries, 1):
                print(f"  {Fore.CYAN}{i:>3}. [{e['hname']}] {Fore.WHITE}{e['name']:<28}"
                      f" {Fore.YELLOW}{e['val'][:55]}")
            if folder_items:
                print(f"\n  {Fore.YELLOW}Startup folder:{Style.RESET_ALL}")
                for i, f in enumerate(folder_items, len(entries)+1):
                    print(f"  {Fore.CYAN}{i:>3}. [Folder] {Fore.WHITE}{f.name}")
            self._sep()
            print(f"  {Fore.GREEN}a{Fore.WHITE} - Add entry   "
                  f"{Fore.RED}d <n>{Fore.WHITE} - Delete entry   "
                  f"{Fore.YELLOW}q{Fore.WHITE} - Quit")
            try:
                choice = input(f"\n  {Fore.CYAN}Action: {Fore.WHITE}").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break
            if choice == 'q':
                break
            elif choice == 'a':
                try:
                    name = input(f"  {Fore.CYAN}Entry name: {Fore.WHITE}").strip()
                    path = input(f"  {Fore.CYAN}Program path: {Fore.WHITE}").strip()
                    if not name or not path:
                        self._err("Name and path required.")
                        continue
                    key = _wr.OpenKey(_wr.HKEY_CURRENT_USER,
                                      r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                                      0, _wr.KEY_SET_VALUE)
                    _wr.SetValueEx(key, name, 0, _wr.REG_SZ, path)
                    _wr.CloseKey(key)
                    self._ok(f"Added '{name}' to startup.")
                except Exception as e:
                    self._err(str(e))
            elif choice.startswith('d '):
                try:
                    idx = int(choice[2:].strip()) - 1
                    if 0 <= idx < len(entries):
                        e = entries[idx]
                        key = _wr.OpenKey(e['hive'], e['path'], 0, _wr.KEY_SET_VALUE)
                        _wr.DeleteValue(key, e['name'])
                        _wr.CloseKey(key)
                        self._ok(f"Removed '{e['name']}' from startup.")
                    elif len(entries) <= idx < len(entries) + len(folder_items):
                        fi = folder_items[idx - len(entries)]
                        confirm = input(f"  {Fore.YELLOW}Delete '{fi.name}'? [y/N]: {Fore.WHITE}").strip().lower()
                        if confirm == 'y':
                            fi.unlink()
                            self._ok(f"Deleted '{fi.name}' from startup folder.")
                    else:
                        self._err("Invalid number.")
                except Exception as e:
                    self._err(str(e))
            input(f"\n  {Fore.CYAN}Press Enter to refresh...{Style.RESET_ALL}")

    # ─────────────────────── weather command ──────────────────────────────────

    def cmd_weather(self):
        try:
            self._info("Detecting location...")
            ip = requests.get('https://api.ipify.org', timeout=6).text.strip()
            geo = requests.get(f'http://ip-api.com/json/{ip}', timeout=6).json()
            if geo.get('status') != 'success':
                self._err("Could not detect location.")
                return
            city = geo['city']
            self._info(f"Getting weather for {Fore.YELLOW}{city}{Fore.WHITE}...")
            r = requests.get(f"https://wttr.in/{city}?format=%C|%t|%w|%h", timeout=8)
            if r.status_code != 200:
                self._err("Weather service unavailable.")
                return
            parts = r.text.strip().split('|')
            if len(parts) < 4:
                self._err("Unexpected weather data format.")
                return
            condition, temp, wind, humidity = parts
            self._sep(f"WEATHER: {city.upper()}")
            print(f"  {Fore.CYAN}Condition : {Fore.WHITE}{condition}")
            print(f"  {Fore.CYAN}Temperature: {Fore.WHITE}{temp}")
            print(f"  {Fore.CYAN}Wind       : {Fore.WHITE}{wind}")
            print(f"  {Fore.CYAN}Humidity   : {Fore.WHITE}{humidity}")
            self._sep()
        except requests.ConnectionError:
            self._err("No internet connection.")
        except Exception as e:
            self._err(str(e))

    def cmd_dev(self):
        print(f"""
{self.C['header']}{'='*50}
          DEVELOPER INFORMATION
{'='*50}{Style.RESET_ALL}
  {Fore.CYAN}Developer : {Fore.GREEN}Jalal
  {Fore.CYAN}Version   : {Fore.YELLOW}2.0.0
  {Fore.CYAN}Platform  : {Fore.CYAN}Windows
  {Fore.CYAN}Website   : {Fore.BLUE}https://eufterminal.netlify.app/
  {Fore.MAGENTA}Made By Love 3>

{self.C['header']}{'='*50}{Style.RESET_ALL}""")

    # ─────────────────────── main loop ────────────────────────────────────────

    def run(self):
        self.show_startup_welcome()

        COMMANDS = {
            'help':              lambda a: self.cmd_help(),
            'info':              lambda a: self.cmd_info(),
            'clear':             lambda a: os.system('cls'),
            'exit':              None,
            'dev':               lambda a: self.cmd_dev(),
            # file
            'create':            lambda a: self.cmd_create(a[0]) if a else self._err("Usage: create <name>"),
            'dircreate':         lambda a: self.cmd_dircreate(a[0]) if a else self._err("Usage: dircreate <name>"),
            'delete':            lambda a: self.cmd_delete(a[0]) if a else self._err("Usage: delete <name>"),
            'dirdel':            lambda a: self.cmd_dirdel(a[0]) if a else self._err("Usage: dirdel <name>"),
            'search':            lambda a: self.cmd_search(a[0]) if a else self._err("Usage: search <name>"),
            'move':              lambda a: self.cmd_move(a[0], a[1]) if len(a) >= 2 else self._err("Usage: move <src> <dst>"),
            'rename':            lambda a: self.cmd_rename(a[0], a[1]) if len(a) >= 2 else self._err("Usage: rename <old> <new>"),
            'size':              lambda a: self.cmd_size(a[0]) if a else self._err("Usage: size <name>"),
            'read':              lambda a: self.cmd_read(a[0]) if a else self._err("Usage: read <name>"),
            'compress':          lambda a: self.cmd_compress(a[0]) if a else self._err("Usage: compress <name>"),
            'uncompress':        lambda a: self.cmd_uncompress(a[0]) if a else self._err("Usage: uncompress <name>"),
            'scan':              lambda a: self.cmd_scan(a[0]) if a else self._err("Usage: scan <filename>"),
            'cd':                lambda a: self.cmd_cd(a[0] if a else None),
            # file protection
            'protect':           lambda a: self.cmd_protect(a[0]) if a else self._err("Usage: protect <file>"),
            'unprotect':         lambda a: self.cmd_unprotect(a[0]) if a else self._err("Usage: unprotect <file>"),
            'hide':              lambda a: self.cmd_hide(a[0]) if a else self._err("Usage: hide <file>"),
            'unhide':            lambda a: self.cmd_unhide(a[0]) if a else self._err("Usage: unhide <file>"),
            'encrypt':           lambda a: self.cmd_encrypt(a[0]) if a else self._err("Usage: encrypt <file>"),
            'decrypt':           lambda a: self.cmd_decrypt(a[0]) if a else self._err("Usage: decrypt <file>"),
            # http requests
            'request':           lambda a: self.cmd_request(a[0] if a else None, a[1] if len(a) > 1 else None, ' '.join(a[2:]) if len(a) > 2 else None),
            # notepad
            'notepad':           lambda a: self.cmd_notepad(a[0] if a else None),
            # shell
            'cmd':               lambda a: self.cmd_cmd(),
            'powershell':        lambda a: self.cmd_powershell(),
            'root':              lambda a: self.cmd_root(),
            'python':            lambda a: self.cmd_python_exec(' '.join(a) if a else None),
            'html':              lambda a: self.cmd_html(' '.join(a) if a else None),
            'js':                lambda a: self.cmd_js(' '.join(a) if a else None),
            # network
            'ipinfo':            lambda a: self.cmd_ipinfo(a[0]) if a else self._err("Usage: ipinfo <ip>"),
            'domaininfo':        lambda a: self.cmd_domaininfo(a[0]) if a else self._err("Usage: domaininfo <domain>"),
            'ping':              lambda a: self.cmd_ping(a[0]) if a else self._err("Usage: ping <host>"),
            'portscan':          lambda a: self.cmd_portscan(a[0]) if a else self._err("Usage: portscan <ip>"),
            'speedtest':         lambda a: self.cmd_speedtest(),
            'wifi-list':         lambda a: self.cmd_wifi_list(),
            'download':          lambda a: self.cmd_download(a[0]) if a else self._err("Usage: download <url>"),
            'net-scan':          lambda a: self.cmd_net_scan(),
            'dns-over-https':    lambda a: self.cmd_dns_over_https(),
            # web
            'browser':           lambda a: self.cmd_browser(),
            'youtube':           lambda a: self.cmd_youtube(),
            'deepseek':          lambda a: self.cmd_deepseek(),
            'relax':             lambda a: self.cmd_relax(),
            # fun
            'rain':              lambda a: self.cmd_rain(),
            'game':              lambda a: self.cmd_game(),
            'rip':               lambda a: self.cmd_rip(),
            # security
            'kill-connections':  lambda a: self.cmd_kill_connections(),
            'sys-integrity':     lambda a: self.cmd_sys_integrity(),
            'anti-run':          lambda a: self.cmd_anti_run(a[0]) if a else self._err("Usage: anti-run <dir>"),
            'antivirus-scan':    lambda a: self.cmd_antivirus_scan(),
            'winsec':            lambda a: self.cmd_winsec(a[0]) if a else self._err("Usage: winsec <on/off>"),
            'repair':            lambda a: self.cmd_repair(),
            'tempdel':           lambda a: self.cmd_tempdel(),
            'tweak':             lambda a: self.cmd_tweak(),
            'closeall':          lambda a: self.cmd_closeall(),
            'who-called-me':     lambda a: self.cmd_who_called_me(),
            # power
            'shutdown':          lambda a: self.cmd_shutdown(),
            'sleep':             lambda a: self.cmd_sleep(),
            'logout':            lambda a: self.cmd_logout(),
            # monitoring
            'cam-check':         lambda a: self.cmd_cam_check(),
            'mic-check':         lambda a: self.cmd_mic_check(),
            'startup-check':     lambda a: self.cmd_startup_check(),
            'activeapps':        lambda a: self.cmd_activeapps(),
            'process-tree':      lambda a: self.cmd_process_tree(),
            'listening-ports':   lambda a: self.cmd_listening_ports(),
            'autorun':           lambda a: self.cmd_autorun(a[0]) if a else self._err("Usage: autorun <on/off>"),
            # utilities
            'timer':             lambda a: self.cmd_timer(a[0], a[1]) if len(a) >= 2 else self._err("Usage: timer <h/m/s> <value>"),
            'weather':           lambda a: self.cmd_weather(),
            'sysinfo':           lambda a: self.cmd_sysinfo_full(),
            'sysmon':            lambda a: self.cmd_sysmon(),
            'netstat':           lambda a: self.cmd_netstat(),
            'myip':              lambda a: self.cmd_myip(),
            'kill':              lambda a: self.cmd_kill(a[0]) if a else self._err("Usage: kill <name|pid>"),
            'env':               lambda a: self.cmd_env(a[0] if a else None),
            'hash':              lambda a: self.cmd_hash_file(a[0]) if a else self._err("Usage: hash <file>"),
            'clipboard':         lambda a: self.cmd_clipboard(a[0] if a else None, ' '.join(a[1:]) if len(a) > 1 else None),
            'encode':            lambda a: self.cmd_encode(a[0] if a else None, ' '.join(a[1:]) if len(a) > 1 else None),
            'ls':                lambda a: self.cmd_ls(),
            'open':              lambda a: self.cmd_open(a[0]) if a else self._err("Usage: open <name>"),
            'copy':              lambda a: self.cmd_copy_file(a[0], a[1]) if len(a) >= 2 else self._err("Usage: copy <src> <dst>"),
            'touch':             lambda a: self.cmd_touch(a[0]) if a else self._err("Usage: touch <name>"),
            'write':             lambda a: self.cmd_write(a[0]) if a else self._err("Usage: write <file>"),
            'screenshot':        lambda a: self.cmd_screenshot(),
            'battery':           lambda a: self.cmd_battery(),
            # navigation
            'desktop':           lambda a: self.cmd_desktop(),
            'downloads':         lambda a: self.cmd_downloads(),
            'documents':         lambda a: self.cmd_documents(),
            'music':             lambda a: self.cmd_music(),
            'pictures':          lambda a: self.cmd_pictures(),
            'videos':            lambda a: self.cmd_videos(),
            'appdata':           lambda a: self.cmd_appdata(),
            # system tools
            'taskmgr':           lambda a: self.cmd_taskmgr(),
            'services':          lambda a: self.cmd_services(),
            'service':           lambda a: self.cmd_service_ctrl(a[0], a[1]) if len(a) >= 2 else self._err("Usage: service <start|stop|restart> <n>"),
            'regedit':           lambda a: self.cmd_regedit_read(a[0]) if a else self._err("Usage: regedit <HKCU|HKLM>\\path"),
            'hosts':             lambda a: self.cmd_hosts(),
            'traceroute':        lambda a: self.cmd_traceroute(a[0]) if a else self._err("Usage: traceroute <host>"),
            'flush-dns':         lambda a: self.cmd_flush_dns(),
            'ip-config':         lambda a: self.cmd_ip_config(),
            # file extras
            'count':             lambda a: self.cmd_count_files(a[0] if a else None),
            'large':             lambda a: self.cmd_find_large(a[0] if a else None, a[1] if len(a) > 1 else "50"),
            'recent':            lambda a: self.cmd_recent(),
            # shell extras
            'calc':              lambda a: self.cmd_calc(' '.join(a)) if a else self._err("Usage: calc <expr>"),
            'note':              lambda a: self.cmd_note(a[0] if a else 'list', *a[1:]),
            'alias':             lambda a: self.cmd_alias_run(a[0], *a[1:]) if a else self._err("Usage: alias <n> <cmd>  |  alias list"),
            'run':               lambda a: self.cmd_run(a[0] if a else None),
            'history':           lambda a: self.cmd_history(a[0] if a else None),
            'clear-history':     lambda a: self.cmd_clear_history(),
            'diskusage':         lambda a: self.cmd_diskusage(),
            'uptime':            lambda a: self.cmd_uptime(),
            'ping-sweep':        lambda a: self.cmd_ping_sweep(a[0] if a else None),
            'terminal-here':     lambda a: self.cmd_open_terminal_here(),
            'diff':              lambda a: self.cmd_file_diff(a[0], a[1]) if len(a) >= 2 else self._err("Usage: diff <f1> <f2>"),
            'zip-list':          lambda a: self.cmd_zip_list(a[0]) if a else self._err("Usage: zip-list <file.zip>"),
            # new commands
            'whoami':            lambda a: self.cmd_whoami(),
            'path':              lambda a: self.cmd_path(),
            'find-text':         lambda a: self.cmd_find_text(a[0], a[1] if len(a)>1 else None) if a else self._err("Usage: find-text <pattern> [dir]"),
            'wlan-info':         lambda a: self.cmd_wlan_info(),
            'proxy':             lambda a: self.cmd_proxy(a[0] if a else None),
            'startup-add':       lambda a: self.cmd_startup_add(a[0], ' '.join(a[1:])) if len(a)>=2 else self._err("Usage: startup-add <n> <path>"),
            'startup-remove':    lambda a: self.cmd_startup_remove(a[0]) if a else self._err("Usage: startup-remove <n>"),
            'cpu-cores':         lambda a: self.cmd_cpu_cores(),
            'tcp-block':         lambda a: self.cmd_tcp_block(a[0]) if a else self._err("Usage: tcp-block <port>"),
            'tcp-unblock':       lambda a: self.cmd_tcp_unblock(a[0]) if a else self._err("Usage: tcp-unblock <port>"),
            'mac-address':       lambda a: self.cmd_mac_address(),
            'installed-apps':    lambda a: self.cmd_installed_apps(),
            'win-update':        lambda a: self.cmd_windows_update(),
            # color + new
            'color':             lambda a: self.cmd_color(a[0] if a else None),
            'passwd':            lambda a: self.cmd_passwd(a[0] if a else "16"),
            'uuid':              lambda a: self.cmd_uuid(),
            'base':              lambda a: self.cmd_base_convert(a[0] if a else None, a[1] if len(a)>1 else None, a[2] if len(a)>2 else None),
            'ping-stats':        lambda a: self.cmd_ping_latency(a[0] if a else "8.8.8.8", a[1] if len(a)>1 else "10"),
            'theme':             lambda a: self.cmd_sys_theme(a[0] if a else None),
            'net-speed':         lambda a: self.cmd_network_speed_live(),
            'file-type':         lambda a: self.cmd_file_type(a[0]) if a else self._err("Usage: file-type <name>"),
            'watch':             lambda a: self.cmd_watch(a[0] if a else None, a[1] if len(a)>1 else "2"),
            'colortest':         lambda a: self.cmd_colortest(),
            # startup manager
            'startup-manager':   lambda a: self.cmd_startup_manager(),
        }

        while True:
            try:
                user_color = Fore.RED if self.is_root else Fore.GREEN
                user_label = "Root" if self.is_root else self.username

                line1 = (
                    f"\n{Fore.RED}\u2500\u2500("
                    f"{user_color}{user_label}"
                    f"{Fore.BLUE}㉿"
                    f"{user_color}{self.hostname}"
                    f"{Fore.RED})-["
                    f"{Fore.GREEN}{self.current_path}"
                    f"{Fore.RED}]"
                    f"{Style.RESET_ALL}"
                )
                line2 = (
                    f"{Fore.RED} \u2514\u2500"
                    f"{user_color}$ "
                    f"{self.input_color}"
                )

                title_prefix = "[Admin] " if self.is_root else ""
                os.system(
                    f"title {title_prefix}EUF Terminal"
                    f" - {user_label}@{self.hostname}")

                print(line1)
                raw = input(line2).strip()
                print(Style.RESET_ALL, end="", flush=True)
                if not raw:
                    continue

                self._history.append(raw)

                parts = raw.split()
                cmd   = parts[0].lower()
                args  = parts[1:]

                # Check aliases
                for main_cmd, aliases in self.cmd_aliases.items():
                    if cmd in aliases:
                        cmd = main_cmd
                        break

                if cmd == 'exit':
                    print(f"{self.C['success']}Goodbye!")
                    break

                if cmd in self._aliases:
                    expanded = self._aliases[cmd].split() + args
                    cmd  = expanded[0].lower()
                    args = expanded[1:]
                    for main_cmd, aliases in self.cmd_aliases.items():
                        if cmd in aliases:
                            cmd = main_cmd
                            break

                handler = COMMANDS.get(cmd)
                if handler is not None:
                    handler(args)
                else:
                    close = [k for k in COMMANDS if k.startswith(cmd[:3])]
                    hint  = f"  Did you mean: {', '.join(close[:4])}" if close else ""
                    self._err(f"Unknown command: '{cmd}'.{hint}  Type 'help' for all commands.")

            except KeyboardInterrupt:
                print(f"\n{self.C['warning']}Ctrl+C caught. Type 'exit' to quit.")
            except EOFError:
                break
            except Exception as e:
                import traceback
                self._err(f"Unexpected error: {type(e).__name__}: {e}")
                if os.environ.get('EUF_DEBUG'):
                    traceback.print_exc()


def main():
    terminal = EUFTerminal()
    terminal.run()


if __name__ == "__main__":
    main()
