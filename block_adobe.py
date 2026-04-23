import os
import subprocess
import sys
from pathlib import Path

KEYWORDS = (
    "adobe",
    "photoshop",
    "creative cloud",
    "ccxprocess",
    "core sync",
)

SEARCH_ROOTS = [
    Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
    Path(os.environ.get("LOCALAPPDATA", "")),
    Path(os.environ.get("APPDATA", "")),
]

MANUAL_TARGET_DIRS = [
    Path(r"C:\Program Files\Adobe\Adobe Photoshop 2026"),
    Path(r"C:\Program Files\Adobe\Adobe Creative Cloud Experience"),
]


def is_admin() -> bool:
    try:
        import ctypes

        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def run_ps(command: str) -> tuple[bool, str]:
    full = (
        "[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
        "$ErrorActionPreference='Stop';"
        + command
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", full],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )
        ok = result.returncode == 0
        out = (result.stdout or "") + (result.stderr or "")
        return ok, out.strip()
    except Exception as exc:
        return False, str(exc)


def looks_like_adobe(path: Path) -> bool:
    p = str(path).lower()
    return any(k in p for k in KEYWORDS)


def _collect_exes_in_dir(root: Path) -> set[Path]:
    found = set()
    for base, _dirs, files in os.walk(root):
        for f in files:
            if f.lower().endswith(".exe"):
                found.add(Path(base) / f)
    return found


def _find_keyword_dirs_quick(root: Path) -> list[Path]:
    # Fast scan: only inspect top-level and second-level folders to avoid long full-disk walks.
    candidates = []
    try:
        level1 = [p for p in root.iterdir() if p.is_dir()]
    except Exception:
        return candidates

    for d1 in level1:
        d1_l = d1.name.lower()
        if any(k in d1_l for k in KEYWORDS):
            candidates.append(d1)
            continue
        try:
            for d2 in d1.iterdir():
                if d2.is_dir() and any(k in d2.name.lower() for k in KEYWORDS):
                    candidates.append(d2)
        except Exception:
            continue
    return candidates


def collect_target_exes() -> list[Path]:
    found = set()

    # Always include every executable from explicitly configured install folders.
    for target_dir in MANUAL_TARGET_DIRS:
        print(f"[SCAN] Fester Ordner: {target_dir}", flush=True)
        if not target_dir.exists():
            print("       -> nicht gefunden", flush=True)
            continue
        found.update(_collect_exes_in_dir(target_dir))

    for root in SEARCH_ROOTS:
        if not root or not root.exists():
            continue
        print(f"[SCAN] Schnellscan in: {root}", flush=True)
        for candidate_dir in _find_keyword_dirs_quick(root):
            found.update(_collect_exes_in_dir(candidate_dir))

    # Keep only relevant executables by path keyword.
    found = {p for p in found if looks_like_adobe(p)}
    return sorted(found)


def add_block_rule(rule_name: str, exe_path: Path, direction: str) -> tuple[bool, str]:
    p = str(exe_path).replace("'", "''")
    cmd = (
        f"if (-not (Get-NetFirewallRule -DisplayName '{rule_name}' -ErrorAction SilentlyContinue)) "
        "{" 
        f"New-NetFirewallRule -DisplayName '{rule_name}' -Direction {direction} "
        f"-Program '{p}' -Action Block -Profile Any | Out-Null; "
        "'CREATED'"
        "} else {"
        "'EXISTS'"
        "}"
    )
    return run_ps(cmd)


def set_existing_adobe_rules_to_block() -> tuple[bool, str]:
    filter_script = (
        "$targets = Get-NetFirewallRule | Where-Object {"
        "$_.DisplayName -match 'Adobe|Photoshop' -or $_.Name -match 'Adobe|Photoshop'"
        "};"
        "if ($targets) {"
        "$targets | Set-NetFirewallRule -Action Block | Out-Null;"
        "'UPDATED=' + $targets.Count"
        "} else {"
        "'UPDATED=0'"
        "}"
    )
    return run_ps(filter_script)


def main() -> int:
    if sys.platform != "win32":
        print("Nur auf Windows verfuegbar.")
        return 1

    if not is_admin():
        print("[FEHLER] Bitte als Administrator starten.")
        return 1

    print("Suche Adobe/Photoshop EXE-Dateien ...", flush=True)
    exes = collect_target_exes()
    if not exes:
        print("Keine Adobe/Photoshop EXE-Dateien gefunden.", flush=True)
    else:
        print(f"Gefunden: {len(exes)} EXE-Datei(en)", flush=True)

    created = 0
    for exe in exes:
        print(f"[RULE] {exe}", flush=True)
        safe_tag = str(exe).replace("\\", "/")
        in_name = f"BLOCK_ADOBE_IN::{safe_tag}"
        out_name = f"BLOCK_ADOBE_OUT::{safe_tag}"

        ok_in, out_in = add_block_rule(in_name, exe, "Inbound")
        ok_out, out_out = add_block_rule(out_name, exe, "Outbound")

        if ok_in and "CREATED" in out_in:
            created += 1
        if ok_out and "CREATED" in out_out:
            created += 1

        if not ok_in or not ok_out:
            print(f"[WARN] Regelproblem bei: {exe}")

    ok_existing, out_existing = set_existing_adobe_rules_to_block()
    if not ok_existing:
        print("[WARN] Konnte bestehende Adobe-Regeln nicht umstellen:")
        print(out_existing)

    print()
    print("Fertig.")
    print(f"Neu erstellte Block-Regeln: {created}")
    if out_existing:
        print(f"Bestehende Adobe/Photoshop-Regeln angepasst: {out_existing}")
    print("Hinweis: Nur Firewall/Netzwerkzugriff wird blockiert, Programme bleiben installiert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
