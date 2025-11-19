import argparse
import json
import sys
import re

import psutil


def find_processes(
    query,
    *,
    exact: bool = False,
    pid_mode: bool = False,
    use_regex: bool = False,
    use_cmd: bool = False,
):
    """
    Find processes matching the query.

    - If pid_mode is True, `query` is an int PID.
    - Otherwise, `query` is a pattern applied to either:
        * process name (default), or
        * full command line string (if use_cmd=True).

    Matching modes:
        * default: case-insensitive substring
        * exact:   case-insensitive equality (name/cmdline)
        * regex:   regex search (case-insensitive by default)
    """
    matches = []

    # Pre-compile regex if needed
    regex = None
    if use_regex and not pid_mode:
        # Case-insensitive by default; caller can override with (?i) in pattern.
        regex = re.compile(query, re.IGNORECASE)

    for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
        try:
            info = proc.info
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

        if pid_mode:
            if info["pid"] == query:
                matches.append(info)
            continue

        # Choose field to match against
        if use_cmd:
            field_raw = " ".join(info.get("cmdline") or [])
        else:
            field_raw = info.get("name") or ""

        if not field_raw:
            continue

        if use_regex:
            if regex.search(field_raw):
                matches.append(info)
            continue

        # Non-regex modes: case-insensitive substring or equality
        field = field_raw.lower()
        q = query.lower()

        if exact:
            if field == q:
                matches.append(info)
        else:
            if q in field:
                matches.append(info)

    return matches


def best_exe_path(info: dict) -> str:
    """
    Try to get the best guess at the executable path.
    Prefer info["exe"], fall back to cmdline[0] if needed.
    """
    exe = info.get("exe")
    if exe:
        return exe

    cmdline = info.get("cmdline") or []
    if cmdline:
        return cmdline[0]

    return ""


def print_table(matches, include_cmdline: bool = False, first_only: bool = False) -> int:
    if not matches:
        print("No matching processes found.", file=sys.stderr)
        return 1

    # If first_only, print a single compact line and exit
    if first_only:
        info = matches[0]
        exe = best_exe_path(info)
        if include_cmdline:
            cmdline_str = " ".join(info.get("cmdline") or [])
            print(f"{info['pid']} {info.get('name') or ''} {exe} [{cmdline_str}]")
        else:
            print(f"{info['pid']} {info.get('name') or ''} {exe}")
        return 0

    # Otherwise, print a simple table
    headers = ["PID", "NAME", "EXE"]
    if include_cmdline:
        headers.append("CMDLINE")

    rows = []
    for info in matches:
        exe = best_exe_path(info)
        row = [str(info["pid"]), info.get("name") or "", exe]
        if include_cmdline:
            row.append(" ".join(info.get("cmdline") or []))
        rows.append(row)

    # Determine column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Print header
    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in rows:
        print("  ".join(row[i].ljust(col_widths[i]) for i in range(len(headers))))

    return 0


def print_json(matches) -> int:
    # Normalize matches a bit and include best_exe_path
    out = []
    for info in matches:
        out.append(
            {
                "pid": info["pid"],
                "name": info.get("name"),
                "exe": best_exe_path(info),
                "cmdline": info.get("cmdline") or [],
            }
        )
    print(json.dumps(out, indent=2))
    return 0 if matches else 1


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Show the executable path for matching processes."
    )
    parser.add_argument(
        "query",
        help="Process name (substring), PID, or pattern.",
    )
    parser.add_argument(
        "--exact",
        action="store_true",
        help="Require exact (case-insensitive) match.",
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        help="Treat query as a regular expression (applied to name or cmdline).",
    )
    parser.add_argument(
        "--cmd",
        action="store_true",
        help="Match against full command line instead of process name.",
    )
    parser.add_argument(
        "--first",
        action="store_true",
        help="Stop after the first match and print a single line.",
    )
    parser.add_argument(
        "--cmdline",
        action="store_true",
        help="Include full command line in output.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of a table.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only the executable path of the first match.",
    )

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # Determine if query is PID
    pid_mode = False
    query_value = args.query
    try:
        pid = int(args.query)
        pid_mode = True
        query_value = pid
    except ValueError:
        pid_mode = False

    # --regex overrides --exact
    if args.regex and args.exact:
        print("Note: --regex specified; ignoring --exact.", file=sys.stderr)
        args.exact = False

    matches = find_processes(
        query_value,
        exact=args.exact,
        pid_mode=pid_mode,
        use_regex=args.regex,
        use_cmd=args.cmd,
    )

    # Quiet mode: only print exe of first match, nothing else
    if args.quiet:
        if not matches:
            sys.exit(1)
        info = matches[0]
        exe = best_exe_path(info)
        if exe:
            print(exe)
            sys.exit(0)
        else:
            sys.exit(1)

    # Normal output modes
    if args.json:
        rc = print_json(matches)
    else:
        rc = print_table(matches, include_cmdline=args.cmdline, first_only=args.first)

    sys.exit(rc)


if __name__ == "__main__":
    main()
