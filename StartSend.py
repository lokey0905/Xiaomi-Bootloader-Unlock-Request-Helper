import argparse
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PID_FILE = BASE_DIR / "send_pids.txt"


def strip_outer_quotes(value):
    if value is None:
        return value
    s = str(value).strip()
    while len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1].strip()
    return s


def resolve_path(value):
    p = Path(strip_outer_quotes(value))
    if p.is_absolute():
        return p
    return BASE_DIR / p


def parse_rows(rows_text):
    rows = []
    for part in str(rows_text).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            step = 1 if end >= start else -1
            rows.extend(range(start, end + step, step))
        else:
            rows.append(int(part))

    cleaned = []
    seen = set()
    for r in rows:
        if r > 0 and r not in seen:
            cleaned.append(r)
            seen.add(r)
    return cleaned


def main():
    parser = argparse.ArgumentParser(description="Launch request scripts for each token file.")
    parser.add_argument("--tokens-dir", default="token", help="Folder that contains token files.")
    parser.add_argument("--script", default="NScript.py", help="Request script to run, e.g. NScript.py.")
    parser.add_argument("--timeshift-file", default="timeshift.txt", help="Path to timeshift file.")
    parser.add_argument("--rows", default="1-4", help="Token rows to use, e.g. 1-4 or 1,3.")
    parser.add_argument("--cols", type=int, default=100, help="Console width.")
    parser.add_argument("--lines", type=int, default=25, help="Console height.")
    parser.add_argument("--delay", type=float, default=0.03, help="Delay between opening windows, seconds.")
    args = parser.parse_args()

    tokens_dir = resolve_path(args.tokens_dir)
    script_path = resolve_path(args.script)
    timeshift_file = resolve_path(args.timeshift_file)

    if not tokens_dir.exists():
        print(f"Tokens directory not found: {tokens_dir}")
        sys.exit(1)
    if not script_path.exists():
        print(f"Request script not found: {script_path}")
        sys.exit(1)
    if not timeshift_file.exists():
        print(f"Timeshift file not found: {timeshift_file}")
        sys.exit(1)

    token_files = sorted(tokens_dir.glob("*.txt"))
    if not token_files:
        print(f"No token files found in: {tokens_dir}")
        sys.exit(1)

    rows = parse_rows(args.rows)
    if not rows:
        print("No valid rows provided.")
        sys.exit(1)

    python_exe = str(Path(sys.executable).resolve())
    creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)

    pids = []

    for token_file in token_files:
        mi_id = token_file.stem
        print(f"Launching for token file: {token_file}")

        for row in rows:
            # Direct launch avoids cmd.exe quote parsing problems in paths with spaces.
            cmd = [
                python_exe,
                str(script_path),
                "--token-file", str(token_file),
                "--timeshift-file", str(timeshift_file),
                "--row", str(row),
                "--cols", str(args.cols),
                "--lines", str(args.lines),
            ]

            proc = subprocess.Popen(
                cmd,
                creationflags=creation_flags,
                cwd=str(BASE_DIR),
            )

            pids.append(proc.pid)
            print(f"  {mi_id} row {row}: PID {proc.pid}")
            time.sleep(max(0.0, args.delay))

    with PID_FILE.open("w", encoding="utf-8") as f:
        f.write("# PIDs created by StartSend_direct.py\n")
        f.write(f"# base={BASE_DIR}\n")
        for pid in pids:
            f.write(f"{pid}\n")

    print()
    print(f"Saved PIDs to: {PID_FILE}")
    print("PIDs:", ", ".join(str(pid) for pid in pids))


if __name__ == "__main__":
    main()
