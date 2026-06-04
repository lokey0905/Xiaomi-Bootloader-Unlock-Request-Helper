import subprocess
import sys
import time
import os

required_packages = ["selenium", "tkinter"]
for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        print(f"[!] Installing missing package: {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tkinter as tk
from tkinter import ttk

tokens_dir = "token"
chrome_link = "https://c.mi.com/global" # dont change this 
mi_id_cookie_keys = {"cuserid", "userid", "uid", "user_id", "miuid"}

def show_taskbar_prompt(title, message, ok_text="OK"):
    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)
    width, height = 420, 140
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.attributes("-topmost", True)
    root.after(200, lambda: root.attributes("-topmost", False))
    frm = ttk.Frame(root, padding=12)
    frm.pack(expand=True, fill=tk.BOTH)
    lbl = ttk.Label(frm, text=message, wraplength=width - 30, justify=tk.LEFT)
    lbl.pack(pady=(6, 12), anchor=tk.W)
    result = {"ok": False}
    def on_ok():
        result["ok"] = True
        root.destroy()
    btn = ttk.Button(frm, text=ok_text, command=on_ok)
    btn.pack(side=tk.BOTTOM)
    root.update_idletasks()
    root.deiconify()
    root.lift()
    root.mainloop()
    return result["ok"]

def extract_chrome_service_token_and_id(link, label):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    show_taskbar_prompt(
        f"Login required - Chrome ({label})",
        "Please log in on c.mi.com/global in the opened Chrome window.\nPress OK after logging in. The login fields may be laggy for a few seconds."
    )
    try:
        cookies = driver.get_cookies()
        cookie_map = {c["name"].lower(): (c.get("value") or "") for c in cookies}
        service_token = cookie_map.get("new_bbs_servicetoken")

        mi_id = None
        for key in mi_id_cookie_keys:
            value = (cookie_map.get(key) or "").strip()
            if value.isdigit():
                mi_id = value
                break
    except Exception as e:
        print(f"[!] Error reading Chrome cookies ({label}): {e}")
        service_token = None
        mi_id = None
    driver.quit()

    if service_token:
        print(f"[✔] Service token found in Chrome ({label})!")
    else:
        print(f"[✖] Service token not found in Chrome ({label})!")

    if mi_id and not str(mi_id).isdigit():
        mi_id = None
    return service_token, mi_id

def prompt_mi_id(default_value=None):
    while True:
        if default_value:
            prompt = f"Enter Xiaomi ID for the token file name [{default_value}]: "
        else:
            prompt = "Enter Xiaomi ID for the token file name: "
        mi_id = input(prompt).strip()
        if not mi_id and default_value:
            return default_value
        if mi_id:
            return mi_id
        print("Xiaomi ID cannot be empty.")

def update_token_file(token_a, token_b, file_name):
    lines = [
        token_a or "N/A",
        token_b or "N/A",
        token_a or "N/A",
        token_b or "N/A"
    ]
    os.makedirs(tokens_dir, exist_ok=True)
    token_path = os.path.join(tokens_dir, f"{file_name}.txt")
    with open(token_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Token file saved: {token_path}")

if __name__ == "__main__":
    print("GetTokens V2 - by byBestix on xdaforums")
    token_a, mi_id_a = extract_chrome_service_token_and_id(chrome_link, "Account 1")
    if not token_a:
        print("[✖] Account 1 token not found!")
    token_b, mi_id_b = extract_chrome_service_token_and_id(chrome_link, "Account 2")
    if not token_b:
        print("[✖] Account 2 token not found!")

    if mi_id_a and mi_id_b:
        if mi_id_a == mi_id_b:
            file_name = mi_id_a
            print(f"[OK] Xiaomi ID detected: {file_name}")
        else:
            file_name = f"{mi_id_a}_{mi_id_b}"
            print(f"[OK] Xiaomi IDs detected: {mi_id_a}, {mi_id_b}")
            print(f"[OK] Using file name: {file_name}.txt")
    elif mi_id_a:
        file_name = mi_id_a
        print(f"[OK] Xiaomi ID detected: {file_name}")
    elif mi_id_b:
        file_name = mi_id_b
        print(f"[OK] Xiaomi ID detected: {file_name}")
    else:
        file_name = prompt_mi_id()

    update_token_file(token_a, token_b, file_name)
    print("Next step: run StartSend.py to launch request scripts.")
