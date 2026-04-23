

# 📄 EUF's Terminal - Complete Commands List

**EUF's Terminal** is a beginner-friendly command-line tool that replaces complex Linux commands with simple, easy-to-remember ones. It includes over 50 useful commands for file management, network testing, security checks, and fun games—all designed to make your terminal experience faster and easier.

**Dev : Rlue**

**Website : https://eufterminal.netlify.app/**


<img width="932" height="907" alt="7kFYdg3" src="https://github.com/user-attachments/assets/e8361460-77b2-4d21-99ee-770121322b31" />

---

## ⚡ PowerShell Installation Commands

### Download EUFTerminal (Source Code):
```powershell
Invoke-WebRequest -Uri "https://github.com/itzrlue/eufterminal/raw/main/main.py" -OutFile "main.py"; python main.py
```

### Download EUFTerminal (.exe):
```powershell
Invoke-WebRequest -Uri "https://github.com/itzrlue/eufterminal/raw/main/EUFTerminal.exe" -OutFile "EUFTerminal.exe"; Unblock-File -Path ".\EUFTerminal.exe"; Start-Process ".\EUFTerminal.exe"
```

---

## 📋 ALL COMMANDS

### 🔧 General Commands
| Command | What it does |
|---------|---------------|
| `help` | Show this help message |
| `info` | Show system information |
| `clear` | Clear screen |
| `exit` | Exit terminal |
| `dev` | Show developer info |

### 📁 File Management
| Command | What it does |
|---------|---------------|
| `create <n>` | Create a new file |
| `dircreate <n>` | Create a new directory |
| `delete <n>` | Delete a file |
| `dirdel <n>` | Delete a directory |
| `search <n>` | Search for files and directories |
| `move <src> <dst>` | Move file or directory |
| `rename <old> <new>` | Rename file or directory |
| `size <n>` | Show size of file or directory |
| `read <n>` | Read file content |
| `write <n>` | Write or append to file interactively |
| `compress <n>` | Compress to zip |
| `uncompress <n>` | Extract a zip archive |
| `copy <src> <dst>` | Copy file or directory |
| `touch <n>` | Create or update file timestamp |
| `hash <n>` | MD5/SHA1/SHA256 checksums |
| `scan <n>` | Scan with Windows Defender |
| `ls` | List current directory |
| `open <n>` | Open with default application |
| `count [dir]` | Count files and folders recursively |
| `large [dir] [MB]` | Find files larger than N MB (default 50) |
| `recent` | 20 most recently modified files |

### 🔒 File Protection
| Command | What it does |
|---------|---------------|
| `protect <n>` | Make file read-only (lock) |
| `unprotect <n>` | Remove read-only protection (unlock) |
| `hide <n>` | Hide a file or folder |
| `unhide <n>` | Unhide a file or folder |
| `encrypt <n>` | Encrypt a file (simple XOR) |
| `decrypt <n>` | Decrypt an encrypted file |

### 🧭 Navigation
| Command | What it does |
|---------|---------------|
| `cd <path>` | Change directory |
| `desktop` | Go to Desktop |
| `downloads` | Go to Downloads |
| `documents` | Go to Documents |
| `music` | Go to Music |
| `pictures` | Go to Pictures |
| `videos` | Go to Videos |
| `appdata` | Go to AppData/Roaming |

### 💻 Terminal & Shell
| Command | What it does |
|---------|---------------|
| `cmd` | Open CMD |
| `powershell` | Open PowerShell |
| `root` | Request admin privileges |
| `python [file.py]` | Run .py file \| no args = interactive |
| `html [file.html]` | Open .html in browser \| no args = interactive |
| `js [file.js]` | Run .js file \| no args = interactive |
| `calc <expr>` | Math expression evaluator |
| `encode <method> <txt>` | base64 / hex / url encode or decode |
| `clipboard <act>` | get / set <text> / clear |
| `note <act>` | add <text> / list / clear (persists) |
| `alias <n> <cmd>` | Session shortcut \| alias list |
| `run [file]` | Auto-run any file by type |
| `history [n]` | Show command history |
| `clear-history` | Clear session history |
| `diskusage` | Disk usage for all drives |
| `uptime` | System uptime and boot time |
| `ping-sweep [subnet]` | Ping all hosts in a /24 subnet |
| `terminal-here` | Open new CMD in current directory |
| `diff <f1> <f2>` | Show differences between two files |
| `zip-list <file.zip>` | List contents of a zip archive |
| `notepad [file]` | Open Windows Notepad |

### 🌐 HTTP Requests
| Command | What it does |
|---------|---------------|
| `request get <url>` | Send GET request |
| `request post <url> <data>` | Send POST request |
| `request delete <url>` | Send DELETE request |
| `request headers <url>` | Get only response headers |

### 🌐 Network
| Command | What it does |
|---------|---------------|
| `ipinfo <ip>` | IP geolocation |
| `domaininfo <domain>` | WHOIS and IP lookup |
| `ping <host>` | Ping |
| `traceroute <host>` | Trace network route |
| `portscan <ip>` | Scan common open ports |
| `speedtest` | Internet speed test |
| `wifi-list` | Saved Wi-Fi passwords |
| `download <url>` | Download file from URL |
| `net-scan` | Scan local network |
| `dns-over-https` | Set DNS to Cloudflare DoH |
| `flush-dns` | Flush DNS resolver cache |
| `ip-config` | Full ipconfig /all |
| `myip` | Public and local IP addresses |
| `netstat` | Active TCP/UDP connections |

### 🌐 Web & Apps
| Command | What it does |
|---------|---------------|
| `youtube` | Open YouTube |
| `deepseek` | Open DeepSeek |
| `relax` | Random relaxing video |
| `browser` | Open default browser |

### 🎮 Fun & Games
| Command | What it does |
|---------|---------------|
| `rain` | Rain animation (Q to stop) |
| `game` | Number guessing game |
| `rip` | R.I.P All Dead Souls |

### 🛡️ Security & System
| Command | What it does |
|---------|---------------|
| `kill-connections` | Kill all active connections |
| `sys-integrity` | SFC system file check |
| `anti-run <dir>` | Monitor dir for new executables |
| `antivirus-scan` | Scan processes for threats |
| `winsec <on/off>` | Toggle Windows Defender |
| `repair` | SFC + DISM repair |
| `tempdel` | Clean temp files |
| `tweak` | Windows performance tweaks |
| `closeall` | Close all user applications |
| `who-called-me` | Camera/mic access history |
| `hosts` | View hosts file |
| `regedit <key>` | Read a registry key |
| `services` | List Windows services |
| `service <act> <n>` | start / stop / restart a service |
| `taskmgr` | Open Task Manager |

### 🔋 Power
| Command | What it does |
|---------|---------------|
| `shutdown` | Shutdown computer |
| `sleep` | Sleep |
| `logout` | Log out |

### 👁️ Monitoring
| Command | What it does |
|---------|---------------|
| `cam-check` | Apps using camera now |
| `mic-check` | Apps using microphone now |
| `startup-check` | Startup programs |
| `activeapps` | Running applications |
| `process-tree` | Process hierarchy tree |
| `listening-ports` | Ports open for connections |
| `kill <name/pid>` | Kill a process |
| `autorun <on/off>` | Terminal auto-startup |
| `sysinfo` | Full hardware snapshot |
| `sysmon` | Live CPU / RAM monitor |

### 🛠️ Utilities
| Command | What it does |
|---------|---------------|
| `timer <h/m/s> <val>` | Set a timer |
| `weather` | Weather for your location |
| `env [filter]` | Environment variables |
| `screenshot` | Take a screenshot |
| `battery` | Battery status |

### 🎨 Color & Customization
| Command | What it does |
|---------|---------------|
| `color <n>` | Set input text color |
| `colortest` | Display all available colors |

### 🔑 Generators
| Command | What it does |
|---------|---------------|
| `passwd [length]` | Generate a strong random password |
| `uuid` | Generate a random UUID v4 |
| `base <val> <from> <to>` | Convert between number bases |


