# iCrackU

Terminal OSINT lookup tool for Kali Linux. Aggregates Sherlock, Maigret, Holehe, theHarvester, PhoneInfoga, GHunt, social-analyzer, and Nominatim into a single colorized interface with auto-saving results.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python icrack.py                          # interactive menu
python icrack.py --email foo@bar.com
python icrack.py --username johndoe
python icrack.py --phone +15551234567
python icrack.py --name "John Doe"
python icrack.py --address "123 Main St, New York"
python icrack.py --check                  # show installed/missing tools
```

Results are auto-saved to `results/` as `.txt` and `.json`.

## External Tools

| Tool | Install |
|---|---|
| holehe | `pip install holehe` |
| theHarvester | `pip install theHarvester` |
| ghunt | `pip install ghunt` |
| sherlock | `pip install sherlock-project` |
| maigret | `pip install maigret` |
| social-analyzer | `pip install social-analyzer` |
| phoneinfoga | https://github.com/sundowndev/phoneinfoga |

Missing tools are skipped with a warning — the rest still run.

## Disclaimer

For authorized security research and ethical OSINT only.
