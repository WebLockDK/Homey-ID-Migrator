import sqlite3
import shutil
import os
import sys
import time
import ctypes
from ctypes import wintypes

# --- ROBUST IMPORT (CRASH-PROOF) ---
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    USE_COLORS = True
except ImportError:
    USE_COLORS = False
    class Fore:
        RED = YELLOW = GREEN = CYAN = BLUE = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""

# --- KONFIGURATION ---
DB_FILENAME = "db.sqlite" 
KEYS_TO_MIGRATE = ["config", "cloud-certificate", "system-name"]
ICON_FILENAME = "icon.ico" # Navnet på din fil i mappen

# --- SYSTEM FUNKTIONER ---

def resource_path(relative_path):
    """ Finder absolut sti til ressourcer i exe (MEIPASS) eller script """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def set_console_icon(icon_name):
    """ Sætter ikon på vinduet via Windows API med tvungen skalering """
    icon_path = resource_path(icon_name)
    
    if not os.path.exists(icon_path):
        return

    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if not hwnd: return

        # Konstanter
        WM_SETICON = 0x80
        ICON_SMALL = 0
        ICON_BIG = 1
        LR_LOADFROMFILE = 0x10
        IMAGE_ICON = 1

        # 1. Indlæs det lille ikon (Tvinger 16x16 til Titlebar)
        h_icon_small = ctypes.windll.user32.LoadImageW(
            None, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE
        )
        
        # 2. Indlæs det store ikon (Tvinger 32x32 til Taskbar)
        h_icon_big = ctypes.windll.user32.LoadImageW(
            None, icon_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE
        )

        # Send beskederne til vinduet
        if h_icon_big:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_icon_big)
        
        if h_icon_small:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_icon_small)

    except Exception:
        pass 

# Sæt titel og forsøg at sætte ikon
ctypes.windll.kernel32.SetConsoleTitleW("Homey.guide - Homey ID Migrator")
set_console_icon(ICON_FILENAME)

# --- UI FUNKTIONER ---

def print_rainbow_logo():
    logo_art = [
        r"   _    _  ____  __  __  ______ __     __     _____ _    _ _____ _____  ______ ",
        r"  | |  | |/ __ \|  \/  ||  ____|\ \   / /    / ____| |  | |_   _|  __ \|  ____|",
        r"  | |__| | |  | | \  / || |__    \ \ / /    | |  __| |  | | | | | |  | | |__   ",
        r"  |  __  | |  | | |\/| ||  __|    \ \ /     | | |_ | |  | | | | | |  | |  __|  ",
        r"  | |  | | |__| | |  | || |____    | |   _  | |__| | |__| |_| |_| |__| | |____ ",
        r"  |_|  |_|\____/|_|  |_||______|   |_|  |_|  \_____|\____/|_____|_____/|______|"
    ]

    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n")
    
    for i, line in enumerate(logo_art):
        c = colors[i % len(colors)] if USE_COLORS else ""
        print(f"{c}{Style.BRIGHT}{line}")
        time.sleep(0.1) 
        
    print(f"\n{Fore.WHITE}{Style.DIM}   >>> THE UNOFFICIAL HOMEY PRO 202X/SHS ID-MIGRATION TOOL - V.1.0.3 <<<{Style.RESET_ALL}\n")
    print(f"{Fore.WHITE}{Style.DIM}   - Crafted for you by https://Homey.guide - brian@homey.guide{Style.RESET_ALL}\n\n")

def log_msg(msg, type="info"):
    prefix = ""
    if type == "info": prefix = f"{Fore.CYAN}[i]{Style.RESET_ALL}"
    elif type == "ok": prefix = f"{Fore.GREEN}[OK]{Style.RESET_ALL}"
    elif type == "warn": prefix = f"{Fore.YELLOW}[!]{Style.RESET_ALL}"
    elif type == "error": prefix = f"{Fore.RED}[X]{Style.RESET_ALL}"
    elif type == "input": prefix = f"{Fore.MAGENTA}[?]{Style.RESET_ALL}"
    print(f"{prefix} {msg}")

def pause_exit(code=0):
    print("\n" + "-"*60)
    input(f"{Style.BRIGHT}Hit [ENTER] to exit...{Style.RESET_ALL}")
    sys.exit(code)

# --- LOGIK ---

def get_db_value(db_path, id_name):
    if not os.path.exists(db_path): return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM Entry WHERE id=?", (id_name,))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else None
    except Exception: return None

def update_db_value(db_path, id_name, new_value):
    if new_value is None: return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Entry WHERE id=?", (id_name,))
        if cursor.fetchone():
            cursor.execute("UPDATE Entry SET value=? WHERE id=?", (new_value, id_name))
            log_msg(f"Updated ID: {Style.BRIGHT}{id_name}", "ok")
        else:
            cursor.execute("INSERT INTO Entry (id, value) VALUES (?, ?)", (id_name, new_value))
            log_msg(f"Created new ID: {Style.BRIGHT}{id_name}", "ok")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_msg(f"Write error {id_name}: {e}", "error")
        return False

def main():
    print_rainbow_logo()
    
    if not USE_COLORS:
        print("NOTE: 'colorama' not found. Running in B&W mode.\n")

    # --- DRAG & DROP INPUT ---
    log_msg("Drag & Drop Homey SHS sqlite folder here:", "input")
    fresh_path = input(f"{Fore.YELLOW}   > {Fore.RESET}").strip().replace('"', '')
    
    print("")
    log_msg("Drag & Drop Homey Pro Backup sqlite folder here:", "input")
    target_path = input(f"{Fore.YELLOW}   > {Fore.RESET}").strip().replace('"', '')

    fresh_db = os.path.join(fresh_path, DB_FILENAME)
    target_db = os.path.join(target_path, DB_FILENAME)

    print("")
    if not os.path.exists(fresh_db):
        log_msg(f"Missing '{DB_FILENAME}' in source!", "error")
        pause_exit(1)
    if not os.path.exists(target_db):
        log_msg(f"Missing '{DB_FILENAME}' in target!", "error")
        pause_exit(1)

    log_msg("READY TO CLONE", "info")
    print(f"    Source: {fresh_db}")
    print(f"    Target: {target_db}")
    
    print("")
    confirm = input(f"{Fore.MAGENTA}[?]{Fore.RESET} Type 'yes' to start: ")
    if confirm.lower() not in ['ja', 'yes', 'j', 'y']:
        log_msg("Cancelled.", "warn")
        pause_exit()

    # Backup
    try:
        shutil.copy2(target_db, target_db + ".bak")
        log_msg("Backup created.", "ok")
    except Exception as e:
        log_msg(f"Backup failed: {e}", "error")
        pause_exit(1)

    # Migrate
    count = 0
    for key in KEYS_TO_MIGRATE:
        val = get_db_value(fresh_db, key)
        if val:
            print(f"   Transplanting {key}...")
            time.sleep(0.5)
            if update_db_value(target_db, key, val): count += 1
        else:
            log_msg(f"Missing '{key}' in source.", "warn")

    print("\n" + "-"*30 + " DONE " + "-"*30 + "\n")
    if count == len(KEYS_TO_MIGRATE):
        print(f"{Fore.GREEN}SUCCESS! Backup patched.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Finished with warnings.{Style.RESET_ALL}")
    
    pause_exit()

if __name__ == "__main__":
    main()