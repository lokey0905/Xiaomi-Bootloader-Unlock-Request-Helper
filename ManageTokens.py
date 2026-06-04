import argparse
import sys
from pathlib import Path


def list_tokens(tokens_dir):
    if not tokens_dir.exists():
        print(f"Tokens directory not found: {tokens_dir}")
        return 1
    files = sorted(tokens_dir.glob("*.txt"))
    if not files:
        print(f"No token files found in: {tokens_dir}")
        return 0
    for path in files:
        print(f"{path.stem} -> {path}")
    return 0


def show_token(tokens_dir, mi_id):
    path = tokens_dir / f"{mi_id}.txt"
    if not path.exists():
        print(f"Token file not found: {path}")
        return 1
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            print(f"{idx}: {line.rstrip()}" )
    return 0


def delete_tokens(paths):
    if not paths:
        print("No token files selected for deletion.")
        return 1
    confirm = input(f"Type YES to delete {len(paths)} file(s): ").strip()
    if confirm != "YES":
        print("Cancelled.")
        return 1
    deleted = 0
    for path in paths:
        try:
            path.unlink()
            deleted += 1
        except Exception as e:
            print(f"Failed to delete {path}: {e}")
    print(f"Deleted {deleted} file(s).")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Manage token files.")
    parser.add_argument("--tokens-dir", default="token", help="Folder that contains token files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List token files.")

    show_parser = subparsers.add_parser("show", help="Show a token file.")
    show_parser.add_argument("--miid", required=True, help="Xiaomi ID (file name without extension).")

    delete_parser = subparsers.add_parser("delete", help="Delete token files.")
    delete_parser.add_argument("--miid", action="append", help="Xiaomi ID to delete.")
    delete_parser.add_argument("--all", action="store_true", help="Delete all token files.")

    args = parser.parse_args()
    tokens_dir = Path(args.tokens_dir)

    if args.command == "list":
        sys.exit(list_tokens(tokens_dir))

    if args.command == "show":
        sys.exit(show_token(tokens_dir, args.miid))

    if args.command == "delete":
        if args.all:
            targets = sorted(tokens_dir.glob("*.txt"))
            sys.exit(delete_tokens(targets))
        if args.miid:
            targets = [tokens_dir / f"{miid}.txt" for miid in args.miid]
            targets = [p for p in targets if p.exists()]
            sys.exit(delete_tokens(targets))
        print("Provide --miid or --all.")
        sys.exit(1)


if __name__ == "__main__":
    main()
