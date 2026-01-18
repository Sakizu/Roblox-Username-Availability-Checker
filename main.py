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

SYLLABLES = [
    "ba","be","bi","bo","bu",
    "ca","ce","ci","co","cu",
    "da","de","di","do","du",
    "ga","ge","gi","go","gu",
    "ka","ke","ki","ko","ku",
    "la","le","li","lo","lu",
    "ma","me","mi","mo","mu",
    "na","ne","ni","no","nu",
    "ra","re","ri","ro","ru",
    "sa","se","si","so","su",
    "ta","te","ti","to","tu",
    "va","ve","vi","vo","vu",
    "za","ze","zi","zo","zu"
]

def generate_random_username(length, use_numbers, use_underscores):
    chars = string.ascii_letters
    if use_numbers:
        chars += string.digits
    if use_underscores:
        chars += "_"

    while True:
        u = ''.join(random.choice(chars) for _ in range(length))
        if u[0].isdigit():
            continue
        if use_underscores:
            if u.startswith("_") or u.endswith("_"):
                continue
            if u.count("_") > 1:
                continue
        return u

def generate_syllable_username(length, use_numbers, use_underscores):
    word = ""
    while len(word) < length:
        word += random.choice(SYLLABLES)
    word = word[:length]

    if use_underscores and random.random() < 0.3:
        extra = "_" + random.choice(SYLLABLES)
        if len(word) + len(extra) <= length:
            word += extra

    if use_numbers and random.random() < 0.4:
        num = str(random.randint(0, 999))
        if len(word) + len(num) <= length:
            word += num

    return word

def generate_username(length, use_numbers, use_underscores, use_syllables):
    if use_syllables:
        return generate_syllable_username(length, use_numbers, use_underscores)
    return generate_random_username(length, use_numbers, use_underscores)

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
        use_numbers = input("Use numbers at end? (y/n): ").lower() == "y"
        use_underscores = input("Use underscores? (y/n): ").lower() == "y"
        use_syllables = input("Use syllables? (y/n): ").lower() == "y"
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

                    username = generate_username(
                        length,
                        use_numbers,
                        use_underscores,
                        use_syllables
                    )

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
