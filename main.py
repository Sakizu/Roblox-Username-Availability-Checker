import asyncio
import aiohttp
import random
import string
import sys
import os
import ctypes

if os.name == "nt":
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

CONCURRENCY = 60
TIMEOUT = 10

def generate_username(length, use_numbers, use_underscores):
    chars = string.ascii_letters
    if use_numbers:
        chars += string.digits
    if use_underscores:
        chars += "_"
    while True:
        u = ''.join(random.choice(chars) for _ in range(length))
        if use_underscores:
            if u.startswith("_") or u.endswith("_"):
                continue
            if u.count("_") > 1:
                continue
        return u

async def check_username(session, username):
    url = (
        "https://auth.roblox.com/v2/usernames/validate"
        f"?request.username={username}"
        "&request.birthday=04%2F15%2F02"
        "&request.context=Signup"
    )
    try:
        async with session.get(url) as r:
            data = await r.json()
            return data.get("message") == "Username is valid"
    except:
        return False

async def main():
    try:
        length = int(input("Username length: "))
        use_numbers = input("Use numbers? (y/n): ").lower() == "y"
        use_underscores = input("Use underscores? (y/n): ").lower() == "y"
        target = int(input("How many valid usernames?: "))
    except (KeyboardInterrupt, EOFError):
        print(f"\n{RED}Exit requested. Goodbye!{RESET}")
        sys.exit(0)

    open("valid.txt", "a").close()
    found = 0

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False)

    try:
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={"User-Agent": "Mozilla/5.0"}
        ) as session:

            sem = asyncio.Semaphore(CONCURRENCY)

            async def worker():
                nonlocal found
                async with sem:
                    if found >= target:
                        return
                    username = generate_username(length, use_numbers, use_underscores)
                    if await check_username(session, username):
                        found += 1
                        with open("valid.txt", "a") as f:
                            f.write(username + "\n")
                        print(f"{GREEN}[{found}/{target}] VALID → {username}{RESET}")

            while found < target:
                await asyncio.gather(*[worker() for _ in range(CONCURRENCY)])

    except KeyboardInterrupt:
        print(f"\n{RED}Stopped by user.{RESET}")
        sys.exit(0)

    print(f"\n{GREEN}DONE.{RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{RED}Program terminated.{RESET}")
        sys.exit(0)
