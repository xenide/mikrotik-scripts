# WireGuard Client Generator

Utility script to create a new WireGuard client on a MikroTik router and export its configuration as a QR code.

## Prerequisites

* Python 3.10+
* [uv](https://github.com/astral-sh/uv) installed globally (follow instructions in the repository)

After cloning the repository, install dependencies and create the virtual environment with:

```bash
uv sync              # installs packages from uv.lock (or resolves and locks if none exists)
```

## Running the script

Execute the script inside the managed virtual environment with `uv run`:

```bash
uv run python generate-new-client-wireguard2.py [options]
```

Replace `[options]` with any flags or arguments the script accepts.

## Development

To add or update dependencies:

```bash
uv pip install <package>
uv lock                # updates uv.lock
```

---

Generated and maintained with ❤️ using `uv`. 
