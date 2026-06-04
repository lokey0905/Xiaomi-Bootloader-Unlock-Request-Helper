# Xiaomi Bootloader Unlock Request Helper

> Original discussion/source: [XDA - How to unlock bootloader on Xiaomi HyperOS, all devices except CN](https://xdaforums.com/t/how-to-unlock-bootloader-on-xiaomi-hyperos-all-devices-except-cn.4654009/)  
> GitHub reference / modified version: [matedon/xiaomi_bypass_bootloader_unlock_quota](https://github.com/matedon/xiaomi_bypass_bootloader_unlock_quota)

Chinese version: [README.md](README.md)

This project is an unofficial helper for the Xiaomi HyperOS / Xiaomi Community Global bootloader unlock authorization request flow. It extracts `new_bbs_serviceToken`, uses millisecond offsets from `timeshift.txt`, syncs against Beijing time (UTC+8), and sends a bootloader unlock authorization request to the Xiaomi API near 00:00.

The main flow in this branch is:

- Use `GetTokens.py` to extract Xiaomi Community Global tokens from a logged-in Chrome session.
- Save tokens as `token/<Xiaomi ID>.txt`.
- Use `StartSend.py` to launch multiple `NScript.py` request windows for every token file under `token/`.
- Use `CloseSend.bat` to close the request windows started by `StartSend.py`.

## Important Notice

- This is an unofficial tool. It is not affiliated with Xiaomi, Mi Community, HyperOS, XDA, or the referenced GitHub repository.
- Use it only with your own Xiaomi account and device. Automated API requests may violate service terms, and account/device risk is your responsibility.
- This tool only handles the authorization request flow. It does not directly unlock your phone. If approved, you still need to use the official Mi Unlock process.
- Unlocking the bootloader may wipe data, reduce device security, affect warranty, or break some services. Back up important data before any unlock operation.
- Xiaomi may change API behavior, quota rules, or account checks at any time. Success is not guaranteed.
- The original XDA thread title states that the flow is for non-CN devices. Do not assume it works for China-region devices.

## Requirements

- Windows
- Python 3.10 or newer
- Google Chrome
- Network access to Xiaomi Community Global, Xiaomi API, and NTP servers
- Python packages:
  - `selenium`
  - `requests`
  - `ntplib`
  - `pytz`
  - `urllib3`
  - `icmplib`
  - `colorama`

The scripts try to install missing packages automatically. If automatic installation fails, install them manually:

```cmd
python -m pip install selenium requests ntplib pytz urllib3 icmplib colorama
```

`tkinter` is normally bundled with the official Windows build of Python. If `GetTokens.py` reports that `tkinter` is missing, install Python from python.org and make sure Tcl/Tk support is included.

## Files

| File | Purpose |
| --- | --- |
| `GetTokens.py` | Opens Chrome, logs in to Xiaomi Community Global, extracts `new_bbs_serviceToken`, and writes it to `token/<Xiaomi ID>.txt`. |
| `ManageTokens.py` | Lists, shows, or deletes token files under `token/`. |
| `StartSend.py` | Launches `NScript.py` in batch for all `.txt` token files and selected token rows. |
| `NScript.py` | Main request script. It checks account status, syncs Beijing time, and sends the request at the target time. |
| `Script.py` | Backup or older request script. In normal use, prefer `NScript.py`. |
| `CloseSend.bat` | Reads `send_pids.txt` and closes request processes started by `StartSend.py`. |
| `timeshift.txt` | One millisecond offset per token row. |
| `Ping.bat` | Helper for network latency checks. |

## Quick Start

The examples below use `python <file>.py` for cmd. If Windows has a working `.py` file association, you can also run the script file directly, such as `GetTokens.py` or `StartSend.py`.

### 1. Get Tokens

Run:

```cmd
python GetTokens.py
```

Flow:

1. The script opens Chrome at `https://c.mi.com/global`.
2. Log in with your Xiaomi account.
3. After login, return to the popup prompt and press `OK`.
4. The script opens Chrome again to extract a second token.
5. It saves the result as `token/<Xiaomi ID>.txt`.

The generated token file usually contains 4 lines:

```text
token_from_account_1
token_from_account_2
token_from_account_1
token_from_account_2
```

Do not upload or share files under `token/`. They contain login cookies.

### 2. Check Token Files

List all token files:

```cmd
python ManageTokens.py list
```

Show token rows for a Xiaomi ID:

```cmd
python ManageTokens.py show --miid 123456789
```

Delete one Xiaomi ID token file:

```cmd
python ManageTokens.py delete --miid 123456789
```

Delete all token files:

```cmd
python ManageTokens.py delete --all
```

### 3. Set Request Time Offsets

Edit `timeshift.txt`. Each line maps to the same row number in each token file. The unit is milliseconds.

Example:

```text
500
200
30
-200
```

Offset rules:

- `500` means send 500 ms before 00:00 Beijing time.
- `30` means send 30 ms before 00:00 Beijing time.
- `-200` means send 200 ms after 00:00 Beijing time.

If you use `--rows 1-4`, `timeshift.txt` must contain at least 4 lines.

### 4. Launch Request Windows

By default, this reads all `.txt` files under `token/` and launches rows `1-4`:

```cmd
python StartSend.py
```

Common options:

```cmd
python StartSend.py --tokens-dir token --rows 1-4 --cols 100 --lines 25
```

Note: `--cols` and `--lines` use Windows `mode con` to set the console window size. This works best with the classic Command Prompt window (classic conhost / Legacy Console). Windows Terminal or newer console environments may ignore the setting.

Use selected rows only:

```cmd
python StartSend.py --rows 1,3
```

Use a range:

```cmd
python StartSend.py --rows 1-4
```

`StartSend.py` opens one independent console window for each token file and row, then records process IDs in `send_pids.txt`.

### 5. Stop Request Windows

Run:

```cmd
CloseSend.bat
```

You can also double-click `CloseSend.bat`. It reads `send_pids.txt` and closes the process tree started by `StartSend.py`.

## Run One Token Row

To test a single account and token row:

```cmd
python NScript.py --token-file .\token\123456789.txt --timeshift-file .\timeshift.txt --row 1
```

You can also specify the console size. This also works best with the classic Command Prompt window; Windows Terminal or newer console environments may not apply `--cols` / `--lines`:

```cmd
python NScript.py --token-file .\token\123456789.txt --row 1 --cols 100 --lines 25
```

## Common Messages

| Message | Meaning |
| --- | --- |
| `Cookie expired, need an updated one.` | The token is expired. Run `GetTokens.py` again. |
| `The account was created less than 30 days ago.` | The account is less than 30 days old. |
| `Blocked to send requests until ...` | The account is temporarily blocked from sending requests. The message shows the unlock date. |
| `Request not sent, The limit has been reached.` | The quota is already full. Try again after the date shown by the response. |
| `Request approved, verifying status...` | The request may be approved. The script checks account status again. |
| `The request may have been approved, checking status...` | The API response is unclear, but approval is possible. The script checks account status again. |

## Credits

- Original XDA discussion/source: [How to unlock bootloader on Xiaomi HyperOS, all devices except CN](https://xdaforums.com/t/how-to-unlock-bootloader-on-xiaomi-hyperos-all-devices-except-cn.4654009/)
- GitHub reference / modified version: [matedon/xiaomi_bypass_bootloader_unlock_quota](https://github.com/matedon/xiaomi_bypass_bootloader_unlock_quota)
- `GetTokens.py` contains the note: `GetTokens V2 - by byBestix on xdaforums`
