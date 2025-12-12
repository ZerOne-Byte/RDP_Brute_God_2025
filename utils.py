# utils.py
import aiofiles
import time
from datetime import timedelta
import psutil
from config import SAVE_INTERVAL  # <-- اضافه شد

async def load_ips(file_path):
    ips = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                ips.append(line)
    return ips

async def save_line(file_path, line):
    async with aiofiles.open(file_path, "a") as f:
        await f.write(line + "\n")

async def periodic_stats(stats, lock, cpu_proc, start_time):
    while True:
        await asyncio.sleep(SAVE_INTERVAL)
        async with lock:
            elapsed = time.time() - start_time
            speed = stats["scanned"] / elapsed if elapsed > 0 else 0
            eta = (stats["total"] - stats["scanned"]) / speed if speed > 0 else 999999
            cpu = cpu_proc.cpu_percent()
            print(f"\r[RDP Brute God] "
                  f"Scanned: {stats['scanned']:,}/{stats['total']:,} "
                  f"({stats['scanned']/stats['total']*100:.2f}%) | "
                  f"Success: {stats['success']:,} | "
                  f"Speed: {speed:,.0f} ips/s | "
                  f"CPU: {cpu:.1f}% | "
                  f"ETA: {str(timedelta(seconds=int(eta)))}      ", end="", flush=True)
