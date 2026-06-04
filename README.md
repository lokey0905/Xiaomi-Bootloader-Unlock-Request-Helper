# Xiaomi Bootloader Unlock Request Helper

> Original discussion/source: [XDA - How to unlock bootloader on Xiaomi HyperOS, all devices except CN](https://xdaforums.com/t/how-to-unlock-bootloader-on-xiaomi-hyperos-all-devices-except-cn.4654009/)  
> GitHub reference / modified version: [matedon/xiaomi_bypass_bootloader_unlock_quota](https://github.com/matedon/xiaomi_bypass_bootloader_unlock_quota)

English version: [README_EN.md](README_EN.md)

這個專案是 Xiaomi HyperOS / Xiaomi Community Global 解鎖申請流程的輔助工具。它會取得 `new_bbs_serviceToken`，依照 `timeshift.txt` 內設定的毫秒偏移量，對齊北京時間 UTC+8，在每日 00:00 附近向 Xiaomi API 送出 bootloader unlock authorization request。

目前這份分支的主要流程是：

- 使用 `GetTokens.py` 從 Chrome 登入後擷取 Xiaomi Community Global token。
- 將 token 依 Xiaomi ID 存成 `token/<Xiaomi ID>.txt`。
- 使用 `StartSend.py` 針對 `token/` 內所有帳號批次啟動多個 `NScript.py` 視窗。
- 使用 `CloseSend.bat` 關閉由 `StartSend.py` 啟動的請求視窗。

## 重要聲明

- 本工具是非官方工具，與 Xiaomi、Mi Community、HyperOS 或 XDA 無官方關係。
- 請只用在你自己的 Xiaomi 帳號與裝置上。使用自動化方式呼叫服務 API 可能違反服務條款，帳號或裝置風險由使用者自行承擔。
- 本工具只處理申請授權流程，不會直接替你的手機完成 bootloader 解鎖。申請通過後仍需依照官方 Mi Unlock 流程操作。
- 解鎖 bootloader 可能清除資料、降低裝置安全性、影響保固或造成部分服務不可用。執行任何解鎖動作前請先備份重要資料。
- Xiaomi 的 API、配額與檢查規則可能隨時變更，成功率不保證。
- XDA 原討論串標題說明此流程適用於非 CN 裝置；中國區裝置請勿假設可用。

## 系統需求

- Windows
- Python 3.10 或更新版本
- Google Chrome
- 可正常連線至 Xiaomi Community Global、Xiaomi API 與 NTP server
- Python 套件：
  - `selenium`
  - `requests`
  - `ntplib`
  - `pytz`
  - `urllib3`
  - `icmplib`
  - `colorama`

腳本會在缺少套件時嘗試自動執行 `pip install`。如果自動安裝失敗，請手動安裝：

```cmd
python -m pip install selenium requests ntplib pytz urllib3 icmplib colorama
```

`tkinter` 通常隨 Windows 版 Python 一起安裝。如果 `GetTokens.py` 提示缺少 `tkinter`，建議改用 python.org 的官方 Windows installer 安裝 Python，並確認安裝選項包含 Tcl/Tk。

## 檔案說明

| 檔案 | 用途 |
| --- | --- |
| `GetTokens.py` | 開啟 Chrome，登入小米社區後擷取 token，並輸出到 `token/<Xiaomi ID>.txt`。 |
| `ManageTokens.py` | 列出、檢視或刪除 `token/` 內的 token 檔。 |
| `StartSend.py` | 對 `token/` 內所有 `.txt` 檔依指定 row 批次啟動 `NScript.py`。 |
| `NScript.py` | 主要送出申請腳本；會檢查帳號狀態、同步北京時間，並在目標時間送出申請。 |
| `Script.py` | 備用或舊版送出腳本；一般情況請優先使用 `NScript.py`。 |
| `CloseSend.bat` | 讀取 `send_pids.txt`，關閉由 `StartSend.py` 啟動的請求程序。 |
| `timeshift.txt` | 每一行代表對應 token row 的送出時間偏移量，單位為毫秒。 |
| `Ping.bat` | 輔助測試網路延遲。 |

## 快速開始

以下範例以 `python <file>.py` 為主。如果你的 Windows 已經把 `.py` 檔正確關聯到 Python，也可以在 cmd 直接輸入檔名執行，例如 `GetTokens.py` 或 `StartSend.py`。

### 1. 取得 token

執行：

```cmd
python GetTokens.py
```

流程：

1. 腳本會開啟 Chrome 到 `https://c.mi.com/global`。
2. 在 Chrome 中登入 Xiaomi 帳號。
3. 登入完成後，回到跳出的提示視窗按 `OK`。
4. 腳本會再開一次 Chrome 擷取第二組 token。
5. 完成後會建立 `token/<Xiaomi ID>.txt`。

產生的 token 檔通常會有 4 行：

```text
token_from_account_1
token_from_account_2
token_from_account_1
token_from_account_2
```

請勿把 `token/` 內的檔案上傳或分享給任何人。這些檔案含有登入 cookie。

### 2. 確認 token 檔

列出所有 token 檔：

```cmd
python ManageTokens.py list
```

檢視指定 Xiaomi ID 的 token row：

```cmd
python ManageTokens.py show --miid 123456789
```

刪除指定 Xiaomi ID 的 token：

```cmd
python ManageTokens.py delete --miid 123456789
```

刪除全部 token：

```cmd
python ManageTokens.py delete --all
```

### 3. 設定送出時間偏移

編輯 `timeshift.txt`。每一行對應 token 檔的同一個 row，單位是毫秒。

範例：

```text
500
200
30
-200
```

偏移量規則：

- `500` 表示在北京時間 00:00 前 500 ms 送出。
- `30` 表示在北京時間 00:00 前 30 ms 送出。
- `-200` 表示在北京時間 00:00 後 200 ms 送出。

如果你使用 `--rows 1-4`，`timeshift.txt` 至少要有 4 行。

### 4. 批次啟動送出視窗

預設會讀取 `token/` 內所有 `.txt` 檔，並啟動 row `1-4`：

```cmd
python StartSend.py
```

常用參數：

```cmd
python StartSend.py --tokens-dir token --rows 1-4 --cols 100 --lines 25
```

備註：`--cols` 與 `--lines` 會透過 Windows `mode con` 設定 console 視窗大小，建議使用舊版命令提示字元視窗（classic conhost / Legacy Console）。Windows Terminal 或新版命令提示字元環境可能會忽略此設定，視窗大小不一定會套用。

只使用指定 row：

```cmd
python StartSend.py --rows 1,3
```

使用範圍：

```cmd
python StartSend.py --rows 1-4
```

`StartSend.py` 會替每個 token 檔、每個 row 開啟一個獨立 console 視窗，並把 PID 記錄到 `send_pids.txt`。

### 5. 停止批次視窗

執行：

```cmd
CloseSend.bat
```

或直接雙擊 `CloseSend.bat`。它會讀取 `send_pids.txt`，並關閉由 `StartSend.py` 啟動的程序樹。

## 單獨執行一個 token row

如果只想測試某個帳號、某一行 token：

```cmd
python NScript.py --token-file .\token\123456789.txt --timeshift-file .\timeshift.txt --row 1
```

也可以指定 console 大小。這個功能同樣建議在舊版命令提示字元視窗使用；Windows Terminal 或新版命令提示字元可能不會套用 `--cols` / `--lines`：

```cmd
python NScript.py --token-file .\token\123456789.txt --row 1 --cols 100 --lines 25
```

## 常見訊息

| 訊息 | 說明 |
| --- | --- |
| `Cookie expired, need an updated one.` | token 已失效，重新執行 `GetTokens.py`。 |
| `The account was created less than 30 days ago.` | 帳號建立時間不足 30 天。 |
| `Blocked to send requests until ...` | 帳號目前被限制送出申請，訊息會顯示解除日期。 |
| `Request not sent, The limit has been reached.` | 當日或當期配額已滿，依訊息日期再嘗試。 |
| `Request approved, verifying status...` | 申請可能已通過，腳本會再次查詢帳號狀態。 |
| `The request may have been approved, checking status...` | API 回傳狀態不明，但可能已通過，腳本會重新查詢。 |

## Credits

- Original XDA discussion/source: [How to unlock bootloader on Xiaomi HyperOS, all devices except CN](https://xdaforums.com/t/how-to-unlock-bootloader-on-xiaomi-hyperos-all-devices-except-cn.4654009/)
- GitHub reference / modified version: [matedon/xiaomi_bypass_bootloader_unlock_quota](https://github.com/matedon/xiaomi_bypass_bootloader_unlock_quota)
- `GetTokens.py` 內標示：`GetTokens V2 - by byBestix on xdaforums`
