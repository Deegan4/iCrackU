<div align="center">

```
 ██╗ ██████╗██████╗  █████╗  ██████╗██╗  ██╗██╗   ██╗
 ██║██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██║   ██║
 ██║██║     ██████╔╝███████║██║     █████╔╝ ██║   ██║
 ██║██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██║   ██║
 ██║╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╔╝
 ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝
```

**Terminal OSINT Framework · Kali Linux**

[![Python](https://img.shields.io/badge/Python-3.12%2B-00ff41?style=flat-square&logo=python&logoColor=white&labelColor=0d0d0d)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-00ff41?style=flat-square&logo=linux&logoColor=white&labelColor=0d0d0d)](https://kali.org)
[![License](https://img.shields.io/badge/License-MIT-00ff41?style=flat-square&labelColor=0d0d0d)](#license)
[![OSINT](https://img.shields.io/badge/Type-OSINT-00ff41?style=flat-square&labelColor=0d0d0d)](#)

</div>

---

## Overview

iCrackU is a terminal-based OSINT aggregator that chains together 10+ industry-standard reconnaissance tools into a single Mr. Robot–styled interface. Run a lookup, get everything — auto-saved as JSON and HTML reports.

```
  [ OSINT FRAMEWORK ]  ·  KALI LINUX  ·  ROOT@LOCALHOST
────────────────────────────────────────────────────────

  1  Email lookup
  2  Username lookup
  3  Phone lookup
  4  Name lookup
  5  Address lookup
  6  IP lookup
  7  Domain lookup
  8  Breach check
  9  Hash lookup
  P  Target profile
  R  Generate report
  0  Exit

  ────────────────────────────────────────────────────
  >
```

---

## Features

| Module | Tools | Notes |
|---|---|---|
| **Email** | Holehe, theHarvester, GHunt | Social account presence + Google profile |
| **Username** | Sherlock, Maigret | 300+ platforms |
| **Phone** | PhoneInfoga | Carrier, region, OSINT scan |
| **Name** | Sherlock, Maigret | Username-style token search |
| **Address** | Nominatim | Geocoding + coordinates |
| **IP** | ipinfo.io, Reverse DNS, Whois, Shodan* | Full host intelligence |
| **Domain** | python-whois, dnspython, subfinder* | WHOIS + DNS + subdomains |
| **Breach** | HaveIBeenPwned* | Checks 12B+ compromised accounts |
| **Hash** | hashid, VirusTotal* | Type detection + malware lookup |
| **Target Profile** | All of the above | Auto-classifies input, runs everything |

`*` = optional API key — prompted once, cached locally

---

## Install

```bash
git clone https://github.com/Deegan4/iCrackU.git
cd iCrackU
pip install -r requirements.txt
```

**Make it a global command:**

```bash
echo '#!/bin/bash' > ~/.local/bin/iCrackU
echo 'exec /path/to/iCrackU/venv/bin/python /path/to/iCrackU/icrack.py "$@"' >> ~/.local/bin/iCrackU
chmod +x ~/.local/bin/iCrackU
```

---

## Usage

```bash
iCrackU                                    # interactive menu
iCrackU --email target@example.com
iCrackU --username johndoe
iCrackU --phone +15551234567
iCrackU --name "John Doe"
iCrackU --address "1600 Pennsylvania Ave"
iCrackU --ip 8.8.8.8
iCrackU --domain example.com
iCrackU --breach target@example.com
iCrackU --hash d41d8cd98f00b204e9800998ecf8427e
iCrackU --target johndoe@gmail.com         # auto-detect + run all
iCrackU --check                            # tool availability
iCrackU --list                             # browse saved results
```

**Generate reports from any saved lookup:**

```bash
iCrackU --report results/2026-04-21_email_foo.json --format html
iCrackU --email target@example.com --save-report --format both
```

---

## Tool Dependencies

```bash
# Auto-installed via pip
pip install -r requirements.txt

# CLI tools (Kali usually has these)
pip install holehe theHarvester ghunt sherlock-project maigret
apt install whois

# PhoneInfoga (binary)
curl -sL https://github.com/sundowndev/phoneinfoga/releases/latest/download/phoneinfoga_Linux_x86_64.tar.gz | tar xz
mv phoneinfoga ~/.local/bin/

# Optional — subfinder for subdomain enumeration
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

Run `iCrackU --check` to see what's installed and what's missing.

---

## API Keys (Optional)

Some modules support optional API keys for deeper enrichment. Keys are prompted once on first use and cached at `~/.icrackU/keys.json` (chmod 600).

| Key | Service | Free Tier |
|---|---|---|
| `shodan` | [shodan.io](https://shodan.io) | Yes |
| `hibp` | [haveibeenpwned.com](https://haveibeenpwned.com/API/Key) | Yes ($3.50/mo) |
| `virustotal` | [virustotal.com](https://virustotal.com) | Yes |

---

## Output

Every lookup is auto-saved to `results/`:

```
results/
  2026-04-21_063340_email_foo@bar.com.json
  2026-04-21_063340_email_foo@bar.com.txt
  2026-04-21_063340_email_foo@bar.com.html   ← with --save-report
  profile_2026-04-21_johndoe.json            ← target profile
```

---

## Project Structure

```
iCrackU/
├── icrack.py              # CLI entry point + interactive menu
├── core/
│   ├── config.py          # API key management
│   ├── output.py          # Terminal UI (Rich)
│   ├── profiler.py        # Target classification + multi-dispatch
│   ├── reporter.py        # HTML + Markdown report generation
│   ├── runner.py          # Subprocess tool execution + timeout
│   └── saver.py           # Results persistence (JSON + TXT)
├── modules/
│   ├── email.py           # Holehe + theHarvester + GHunt
│   ├── username.py        # Sherlock + Maigret
│   ├── phone.py           # PhoneInfoga
│   ├── name.py            # Sherlock + Maigret (name token)
│   ├── address.py         # Nominatim geocoding
│   ├── ip.py              # ipinfo + reverse DNS + Shodan
│   ├── domain.py          # WHOIS + DNS + subfinder
│   ├── breach.py          # HaveIBeenPwned v3
│   └── hash.py            # hashid + VirusTotal
├── tests/                 # 35+ unit tests
└── results/               # Auto-saved lookup output (gitignored)
```

---

## Disclaimer

For authorized security research, ethical OSINT, and educational purposes only. Do not use against targets without explicit permission. The author assumes no liability for misuse.

---

<div align="center">
<sub>Built for Kali Linux · Powered by the OSINT community's best tools</sub>
</div>
