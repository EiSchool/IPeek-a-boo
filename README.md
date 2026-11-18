# IPeek-a-Boo – *"I see your IP!"*

[![CI](https://github.com/EiSchool/IPeek-a-boo/actions/workflows/ci.yml/badge.svg)](https://github.com/EiSchool/IPeek-a-boo/actions/workflows/ci.yml)

A Python command-line app for network technicians. It **peeks** at a computer's current **public IPv4 and IPv6 addresses** and shows the **location, ISP, ASN and country code** behind them. The **Peek-a-Boo check** then tells you whether an IP is "hiding" behind a VPN, a proxy or a data center.

Built by **Team We Don't Byte** for DEVASC Project Activity 3 – Social Coding (Option 2: IPv4/IPv6 Address Application), and extended in Project Activity 4 – Automated Software Testing and Deployment.

| Member | Role | Owns |
|---|---|---|
| Eissa D. Tinio | Scrum Leader & Repository Owner | `app.py`, `README.md`, merges |
| Kristofer Luis Carpio | Developer (REST APIs) | `ipinfo/api.py` |
| Jethro Cabuhat | Recorder & UI Developer | `ipinfo/display.py`, `ipinfo/export.py`, docs |
| Cole Ezekiel Vidal | QA (Quality Assurance) | `ipinfo/analysis.py`, `tests/` |

**Repository:** https://github.com/EiSchool/IPeek-a-boo · **Version:** 1.1.0 (Sprint 2)

> **Why the name?** "IP" + "peek" + the game peek-a-boo. Even if you hide behind a VPN, the app still finds you.

---

## Features

| # | Feature | Menu option |
|---|---|---|
| 1 | Shows the computer's public **IPv4** and **IPv6**. If the network has no IPv6, it says so instead of crashing. | 1 |
| 2 | Shows **location and provider** details: city, region, country, country code, postal code, latitude/longitude, time zone, **ISP** and **ASN** | 1, 2 |
| 3 | **Peek-a-Boo check**: is the IP a **VPN/proxy/Tor exit**, a **data center/cloud host**, or on **mobile data**? It ends with a fun one-line verdict. | 1, 2 |
| 4 | **Looks up any IP address** you type in, after checking that it is valid | 2 |
| 5 | **Offline address analysis**: type (public/private/loopback/link-local/multicast/**carrier-grade NAT**), IPv4 class, binary, integer, reverse-DNS name, IPv6 compressed/expanded forms | 2, 3 |
| 6 | **Halloween theme**: pumpkin banner, pumpkin-orange / witch-purple / slime-green colors, spooky menu hints and messages (`rich` library) | all |
| 7 | **Automatic fallback**: if ipapi.co is down or rate limited, ip-api.com is used instead | 1, 2 |
| 8 | **Friendly errors** for timeouts, no internet, rate limits and invalid input | all |
| 9 | **Saves results** to JSON or CSV in `exports/` | 4 |
| 10 | **"Where am I?" map links**: Google Maps and OpenStreetMap links built from the coordinates *(Sprint 2)* | 1, 2 |
| 11 | **"Your IP changed!" alert**: remembers your last public IPv4/IPv6 and warns when it changes *(Sprint 2)* | 1 |
| 12 | **Subnet / CIDR calculator**: network, mask, wildcard, broadcast, first/last host, host count; accepts `/24` or `255.255.255.0` *(Sprint 2)* | 5 |

## REST APIs used

None of them needs an API key, so there are no secrets in this repository.

| API | Endpoint | Used for |
|---|---|---|
| [ipify](https://www.ipify.org) | `https://api.ipify.org?format=json` | Public IPv4 |
| ipify (IPv6) | `https://api6.ipify.org?format=json` | Public IPv6 (only answers over IPv6) |
| [ipapi.co](https://ipapi.co) (primary) | `https://ipapi.co/<ip>/json/` | Location, ISP, ASN. Free tier: about 1,000 requests/day |
| [ip-api.com](https://ip-api.com) (fallback) | `http://ip-api.com/json/<ip>` | Location, ISP, ASN. Free tier: 45 requests/min, HTTP only |
| ip-api.com (Peek-a-Boo) | `http://ip-api.com/json/<ip>?fields=status,message,mobile,proxy,hosting` | VPN/proxy, hosting and mobile flags |

---

## Setup

**Requirements:** Python 3.10 or newer, and an internet connection (menu options 3 and 5 work offline).

1. Install Python from <https://www.python.org/downloads/>. On Windows, tick **"Add python.exe to PATH"** in the installer.
2. Clone the repository and install the two libraries it needs:

```bash
git clone https://github.com/EiSchool/IPeek-a-boo.git
cd IPeek-a-boo
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

```
┌──────────────────────────────────────────────┐
│       ,(                                     │
│    .-'-'-.                                   │
│   / /\ /\ \                                  │
│  |    ^    |                                 │
│   \ \/\/\/ /                                 │
│    '-...-'                                   │
│                                              │
│ IPeek-a-Boo  I see your IP!                  │
│ Public IPv4 / IPv6 - Geolocation - ISP - ASN │
│ by team We Don't Byte  -  Halloween edition  │
└──────────────────────────────────────────────┘

  1  Show my public IP information  (unmask yourself)
  2  Look up any IP address  (hunt a stranger)
  3  Analyze an IP address (offline)  (read its bones)
  4  Save last result to a file  (bury it in exports/)
  5  Subnet / CIDR calculator  (carve up the graveyard)
  0  Exit  (flee into the night)
```

Example (option 2 → `8.8.8.8`, shortened):

```
        Peek-a-Boo check
┌───────────────────────┬───────┐
│ VPN / proxy / Tor     │ Yes   │
│ Hosting / data center │ Yes   │
│ Mobile network        │ No    │
└───────────────────────┴───────┘
BOO! Nice mask... but we still see you. ip-api.com lists this IP as a VPN, proxy or Tor exit.
This IP haunts a data center (cloud/hosting), not a home or office.
```

Good addresses to try:

| Address | What it shows |
|---|---|
| `8.8.8.8` | Google DNS: Mountain View, AS15169, data center |
| `2001:4860:4860::8888` | Google DNS over IPv6 |
| `192.168.1.1` | Private: facts only, no geolocation |
| `100.64.0.1` | Carrier-grade NAT range (common with ISPs) |
| `127.0.0.1`, `::1` | Loopback |
| `hello` | Invalid input: friendly error |

## Running the tests

The 45 tests don't use the internet: the API tests feed in saved sample responses, and the
"IP changed" tests write to a temporary folder.

```bash
python -m unittest -v
```

| File | Tests | What it checks |
|---|---|---|
| `tests/test_analysis.py` | 14 | IP validation, address type, IPv4 class, binary/integer, IPv6 forms, **subnet calculator** (`/24`, dotted masks, `/27`, `/31`, `/32`, `/8`, IPv6 `/64`, bad input) |
| `tests/test_api.py` | 9 | Converting each API's JSON to one format, fallback to the second API, no-IPv6, Peek-a-Boo flags |
| `tests/test_export.py` | 3 | JSON round trip, CSV rows, unknown format rejected |
| `tests/test_maps.py` | 4 | **Map links** from coordinates, rounding, missing/invalid/out-of-range coordinates |
| `tests/test_history.py` | 6 | **IP change alert**: first run, unchanged, IPv4 changed, IPv6 lost, damaged file, unwritable folder |
| `tests/test_app.py` | 9 | **Integration**: every menu action with the APIs faked, and an **end-to-end** run of `python app.py` typing menu choices into it |

To see how much of the code the tests cover (the pipeline fails below 75%):

```bash
pip install -r requirements-dev.txt
python -m coverage run -m unittest
python -m coverage report
python -m flake8 .
```

## CI/CD pipeline (GitHub Actions)

`.github/workflows/ci.yml` runs **automatically on every push to any branch and on every pull request to `main`**:

```
push / pull request
   │
   ├─► Lint            flake8 (syntax errors, undefined names, unused imports, style)
   │      │ only if lint passes
   ├─► Tests  ×4       Ubuntu + Windows  ×  Python 3.10 + 3.13
   │                   45 unit/integration/end-to-end tests, coverage must be ≥ 75%
   │                   (coverage report uploaded as a downloadable artifact)
   │
   └─► CI passed       green only if lint AND all four test jobs succeeded
```

**Merging is blocked unless the pipeline passes.** On GitHub: *Settings → Branches → Add branch
protection rule* (or *Rules → Rulesets*) for `main`, then tick:

- **Require a pull request before merging** → *Require approvals: 1*
- **Require status checks to pass before merging** → *Require branches to be up to date* → add the check **`CI passed`**
- **Do not allow bypassing the above settings**

The result shows on every pull request as a ✅ or ❌ next to each commit, and the badge at the top
of this README shows the state of `main`. A `Jenkinsfile` with the same stages is included for
comparison with Jenkins.

---

## Project structure

```
app.py               Menu loop; connects all the modules together
ipinfo/
  api.py             REST API calls + converting each API's JSON to one standard format
  analysis.py        Offline IP facts and the subnet calculator (built-in ipaddress module)
  display.py         All screen output (banner, menu, tables, verdicts) using rich
  export.py          Saving results to JSON / CSV
  maps.py            "Where am I?" map links from latitude/longitude
  history.py         Remembers the last public IP for the "Your IP changed!" alert
tests/               unittest tests (unit, integration and end-to-end)
requirements.txt     Third-party libraries (requests, rich)
requirements-dev.txt + the CI tools (flake8, coverage)
setup.cfg            flake8 and coverage settings shared by local runs and CI
.github/workflows/   ci.yml - the GitHub Actions pipeline
Jenkinsfile          The same pipeline for Jenkins (for comparison)
```

### How it works

```
user picks a menu option (app.py)
        │
        ├─► analysis.parse_ip()  ──► analysis.analyze()     (offline facts)
        │
        ├─► api.get_public_ipv4() / get_public_ipv6()       (ipify)
        │
        ├─► api.get_ip_details(ip)                          (ipapi.co → fallback ip-api.com)
        │        └─ each API's JSON is converted to ONE standard dict
        │
        ├─► api.get_privacy_check(ip)                       (Peek-a-Boo: ip-api.com flags)
        │
        ├─► display.show_table() / show_peekaboo_verdict()  (rich colored output)
        │
        └─ the result is kept as last_result ──► option 4 ──► export.save_results()
```

Design rules that keep the code easy to extend:

- **`api.py` never prints, and `display.py` never calls the network.** Each module does one job, which is also why four people could work on it at the same time.
- **Every geolocation API is converted to the same dict** (`ip, city, region, country, country_code, postal, latitude, longitude, timezone, isp, asn, source`), so the display and export code never needs to know which API answered.
- **API errors become `LookupFailed`.** `app.py` catches just this one exception and shows a friendly message.
- **Every menu action returns a result** in the form `{section: {field: value}}`, which is what `export.py` saves.

## How to continue this project

| To… | Do this |
|---|---|
| Add a new menu feature | Write a function in `app.py` that returns a result dict, add it to `ACTIONS`, and add a line to `display.MENU` |
| Add another geolocation API | In `api.py`, write a `_url()` function and a `_from_<name>()` function that converts its JSON to the standard dict, then add both to `GEO_PROVIDERS` |
| Show a new field | Add it to the standard dict in each `_from_*()` function and give it a label in `display.LABELS` |
| Change the theme, layout or the verdict jokes | Edit only `display.py`. The whole palette is the five color constants at the top (`PUMPKIN`, `WITCH`, `SLIME`, `BONE`, `BLOOD`) |
| Add an export format | Add it to `export.FORMATS` and write it in `save_results()` |

Add a test in `tests/` for any new logic, and run `python -m unittest` before opening a pull request. The CI pipeline runs the same tests again on GitHub.

## Team workflow (GitHub)

- `main` always works. Nobody pushes to it directly; everything goes through a **pull request**.
- Each task gets its own branch: `feature/<short-name>` or `fix/<short-name>`. Sprint 1 branches: `feature/api-carpio` (Kristofer), `feature/analysis-vidal` and `feature/tests-vidal` (Cole), `feature/display-cabuhat` and `feature/export-cabuhat` (Jethro), `feature/menu-tinio` (Eissa).
- Every PR needs **one approving review** (QA, Cole, reviews every PR) **and a green `CI passed` check** before Eissa merges it. GitHub blocks the merge button until both are done.
- Tasks are tracked on the **GitHub Projects** board (To Do → In Progress → In Review → Done).

```bash
git checkout -b feature/my-feature
# ...edit, then:
git add .
git commit -m "Add my feature"
git push -u origin feature/my-feature
# open a Pull Request on GitHub and request a reviewer
```

## Backlog (future enhancements)

Done in Project Activity 4 (Sprint 2): ~~"Where am I?" map link~~, ~~"Your IP changed!" alert~~,
~~Subnet/CIDR calculator~~, ~~GitHub Actions CI~~.

Still planned, in priority order:

1. **CGNAT detector** – compare the router's WAN IP with the public IP
2. **Batch lookup** from a text/CSV file of IPs
3. **Reverse DNS (PTR) and WHOIS** details
4. **Command-line options** – `python app.py --ip 8.8.8.8 --json`
5. **Local network info** – private IP, gateway, DNS servers
6. **GUI (Tkinter) or web version (Flask)**
7. **Caching and Docker** (and deploy a container image from the pipeline)

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognized, or it opens the Microsoft Store | Install Python from python.org with "Add to PATH" ticked, then open a new terminal |
| `ModuleNotFoundError: rich` / `requests` | Activate the venv and run `pip install -r requirements.txt` |
| IPv6 says "Not available" | Your network has no IPv6. That's normal on many networks |
| "Rate limit reached" | The free APIs limit requests. The app already tries the second API; if both are limited, wait a minute |
| "IP changed" alert after connecting to a VPN or another Wi-Fi | That's expected: your public IP really did change. Delete `~/.ipeekaboo_last_ip.json` to start over |
| Peek-a-Boo says a normal IP is a proxy | These flags come from ip-api.com's database and are estimates, not proof |
