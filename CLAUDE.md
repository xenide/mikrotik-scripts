# CLAUDE.md

## Project overview

WireGuard client generator for MikroTik RouterOS. Single-script Python project that connects to a MikroTik router via the RouterOS API, creates a new WireGuard peer (auto-incrementing IP and name), and exports the config as a QR code copied to the macOS clipboard.

## Key files

- `generate-new-client-wireguard2.py` — main (and only) script
- `pyproject.toml` — project metadata and dependencies
- `uv.lock` — pinned dependency lockfile
- `.env` — router credentials (`USERNAME`, `PASSWORD`), gitignored

## Development

```bash
uv sync                          # install dependencies
uv run python generate-new-client-wireguard2.py  # run the script
```

## Configuration

The script reads `USERNAME` and `PASSWORD` from `.env` via `python-dotenv`. Router IP (`10.0.0.254`), port (`8728`), and WireGuard interface (`wireguard2`) are set as constants at the top of the script.

## Branch strategy

- Default branch is `dev` (not main/master)

## Notes

- macOS-only clipboard handling (uses `osascript`)
- No tests, no CI/CD
- When adding new peers via the RouterOS API, read-only fields from existing peers must be stripped before passing to `add()` (e.g. `last-handshake`, `tx`, `rx`, `current-endpoint-address`, etc.)
