#!/usr/bin/env python3
"""Post-install beginner guide for GenericAgent.

Runs after `assets/configure_mykey.py`. Reads the produced `mykey.py`, detects
which IM platforms the user enabled, checks whether their Python packages are
importable, and offers to install the missing ones.

- If no platform is configured yet, offers to (re)launch the configure wizard.
- If a platform that needs interactive QR login (e.g. WeChat iLink) had its
  dependencies installed just now, offers to re-run the wizard so the user can
  scan the QR.

This script is intentionally stdlib-only so it works on any Python the
installer brings (uv-managed 3.12 or the user's system Python).

Exit codes:
    0  always (failures are reported but do not break the installer)
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(
    os.environ.get("GENERICAGENT_HOME")
    or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
).resolve()
MYKEY_PATH = PROJECT_ROOT / "mykey.py"
WIZARD_PATH = PROJECT_ROOT / "assets" / "configure_mykey.py"

# (platform label, regex on mykey.py, list of (import_name, pip_name), requires_relogin)
PLATFORM_CHECKS: list[tuple[str, str, list[tuple[str, str]], bool]] = [
    (
        "WeChat (iLink)",
        r"wechat|wx_|ilink|WxBotClient",
        [("qrcode", "qrcode"), ("Crypto", "pycryptodome")],
        True,
    ),
    (
        "Telegram",
        r"tg_bot_token|tg_allowed_users",
        [("telegram", "python-telegram-bot")],
        False,
    ),
    (
        "QQ",
        r"qq_app_id|qq_app_secret",
        [("botpy", "qq-botpy")],
        False,
    ),
    (
        "Feishu / Lark",
        r"fs_app_id|fs_app_secret",
        [("lark_oapi", "lark-oapi")],
        False,
    ),
    (
        "WeCom",
        r"wecom_bot_id|wecom_secret",
        [("wecom_aibot_sdk", "wecom-aibot-sdk")],
        False,
    ),
    (
        "DingTalk",
        r"dingtalk_client_id|dingtalk_client_secret",
        [("dingtalk_stream", "dingtalk-stream")],
        False,
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Tiny ANSI helpers (no rich/colorama dependency).
# ──────────────────────────────────────────────────────────────────────────────

def _supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


def _c(code: str, text: str) -> str:
    if not _supports_color():
        return text
    return f"\033[{code}m{text}\033[0m"


def info(msg: str) -> None:
    print(f"{_c('36', '[post-install]')} {msg}")


def ok(msg: str) -> None:
    print(f"{_c('32', '[ok]')} {msg}")


def warn(msg: str) -> None:
    print(f"{_c('33', '[warn]')} {msg}")


# ──────────────────────────────────────────────────────────────────────────────
# Interactive helpers.
# ──────────────────────────────────────────────────────────────────────────────

def is_interactive() -> bool:
    if os.environ.get("GA_POST_INSTALL_NONINTERACTIVE") == "1":
        return False
    return sys.stdin.isatty()


def ask_yes_no(question: str, default_yes: bool = True) -> bool:
    # Non-interactive callers never get prompted; treat the answer as "no" so
    # we never accidentally launch sub-flows (wizard, pip install) without a
    # human there to react.
    if not is_interactive():
        return False
    suffix = "[Y/n]" if default_yes else "[y/N]"
    try:
        ans = input(f"{question} {suffix} ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    if not ans:
        return default_yes
    return ans in {"y", "yes"}


# ──────────────────────────────────────────────────────────────────────────────
# Detection.
# ──────────────────────────────────────────────────────────────────────────────

def read_mykey() -> str:
    if not MYKEY_PATH.exists():
        return ""
    try:
        return MYKEY_PATH.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def python_can_import(module: str) -> bool:
    return (
        subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def detect(content: str) -> tuple[list[str], list[str], bool]:
    """Return (enabled_platform_labels, missing_pip_names, needs_relogin)."""
    enabled: list[str] = []
    missing: list[str] = []
    relogin = False
    for label, pattern, deps, requires_relogin in PLATFORM_CHECKS:
        if not re.search(pattern, content):
            continue
        enabled.append(label)
        local_missing = [pip for imp, pip in deps if not python_can_import(imp)]
        if local_missing:
            missing.extend(local_missing)
            if requires_relogin:
                relogin = True
    # dedupe while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for name in missing:
        if name not in seen:
            seen.add(name)
            deduped.append(name)
    return enabled, deduped, relogin


# ──────────────────────────────────────────────────────────────────────────────
# Actions.
# ──────────────────────────────────────────────────────────────────────────────

def run_configure_wizard() -> None:
    if not WIZARD_PATH.exists():
        warn(f"configure_mykey.py not found at {WIZARD_PATH}")
        return
    info("Launching configure_mykey.py …")
    subprocess.run(
        [sys.executable, str(WIZARD_PATH)],
        cwd=str(PROJECT_ROOT),
        check=False,
    )


def _pick_pip_command() -> list[str]:
    """Prefer `uv pip` when available; fall back to `python -m pip`."""
    uv = shutil.which("uv")
    if uv:
        return [uv, "pip", "install", "--python", sys.executable]
    return [sys.executable, "-m", "pip", "install"]


def install_packages(packages: Iterable[str]) -> bool:
    pkgs = list(packages)
    if not pkgs:
        return True
    cmd = _pick_pip_command() + pkgs
    info("Running: " + " ".join(cmd))
    result = subprocess.run(cmd)
    return result.returncode == 0


# ──────────────────────────────────────────────────────────────────────────────
# Main flow.
# ──────────────────────────────────────────────────────────────────────────────

def offer_enable_platform() -> bool:
    info("No IM platform is configured in mykey.py yet.")
    info(
        "GenericAgent can chat with you through "
        "Telegram / WeChat / QQ / Feishu / WeCom / DingTalk."
    )
    return ask_yes_no("Enable a platform now?", default_yes=False)


def offer_install_missing(missing: list[str]) -> bool:
    warn("Configured platforms need extra Python packages:")
    for pkg in missing:
        warn(f"  - {pkg}")
    if not ask_yes_no("Install these now?", default_yes=True):
        info(
            "Skipped. Install later with: "
            + " ".join(_pick_pip_command() + missing)
        )
        return False
    return install_packages(missing)


def main() -> int:
    # Walk the user through this once; recursion is bounded by user input.
    for _round in range(3):  # safety cap
        content = read_mykey()
        if not content:
            if not is_interactive():
                info("mykey.py not configured yet; rerun this script in a terminal to start the wizard.")
                return 0
            if WIZARD_PATH.exists() and ask_yes_no(
                "mykey.py not found. Run the configure wizard now?",
                default_yes=True,
            ):
                run_configure_wizard()
                continue
            info(
                "Skipped. Run later: "
                f"{sys.executable} {WIZARD_PATH}"
            )
            return 0

        enabled, missing, relogin = detect(content)

        if not enabled:
            if is_interactive() and offer_enable_platform():
                run_configure_wizard()
                continue
            info(
                "You can enable a platform later with: "
                f"{sys.executable} {WIZARD_PATH}"
            )
            return 0

        ok("Enabled platforms: " + ", ".join(enabled))
        if not missing:
            ok("All required Python packages for these platforms are installed.")
            return 0

        if not is_interactive():
            warn(
                "Missing packages "
                f"({', '.join(missing)}); rerun this script interactively or "
                "install them manually."
            )
            return 0

        installed_ok = offer_install_missing(missing)
        if not installed_ok:
            return 0
        ok("Installed: " + ", ".join(missing))

        if relogin and ask_yes_no(
            "Re-run setup wizard now (e.g. to scan WeChat iLink QR)?",
            default_yes=True,
        ):
            run_configure_wizard()
        return 0

    warn("Reached round cap; bailing out to avoid loop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
