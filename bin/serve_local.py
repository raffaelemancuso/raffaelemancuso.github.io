#!/usr/bin/env python3
"""Serve the built site from the host, bypassing Docker's port forwarding.

Docker Desktop's port proxy is unreliable on this machine: `docker compose up`
maps 8080 correctly and the container answers on it, yet every request from the
host times out. This script sidesteps Docker networking entirely -- it builds
the site inside the container (the host has no Ruby), copies the output out,
and serves it with a plain Python HTTP server the browser can actually reach.

Usage:
    python bin/serve_local.py                 # build, then serve on :4000
    python bin/serve_local.py --port 8000     # serve on a different port
    python bin/serve_local.py --no-build      # reuse the previous build
    python bin/serve_local.py --dev           # JEKYLL_ENV=development
    python bin/serve_local.py --open          # open a browser when ready

Ctrl-C stops the server. The container is left running so the next build is
fast; stop it with `docker compose down`.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import shutil
import socket
import socketserver
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / ".preview_site"
SERVICE = "jekyll"
CONTAINER_DEST = "/tmp/preview"


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, text=True, **kw)


def capture(cmd: list[str]) -> str:
    p = run(cmd, capture_output=True)
    return p.stdout.strip() if p.returncode == 0 else ""


def die(msg: str) -> None:
    sys.exit(f"error: {msg}")


def ensure_container() -> str:
    """Return the container id, starting the stack if it is not up."""
    if not shutil.which("docker"):
        die("docker is not on PATH")
    if run(["docker", "info"], capture_output=True).returncode != 0:
        die("the Docker daemon is not running -- start Docker Desktop first")

    cid = capture(["docker", "compose", "ps", "-q", SERVICE])
    if not cid:
        print("starting the container ...")
        if run(["docker", "compose", "up", "-d"]).returncode != 0:
            die("`docker compose up -d` failed")
        cid = capture(["docker", "compose", "ps", "-q", SERVICE])
    if not cid:
        die(f"could not find the '{SERVICE}' container")

    # entry_point.sh may still be running `bundle install` on a cold image.
    for _ in range(180):
        probe = run(
            ["docker", "compose", "exec", "-T", SERVICE, "bash", "-c", "command -v bundle"],
            capture_output=True,
        )
        if probe.returncode == 0:
            return cid
        time.sleep(1)
    die("the container never became ready")


def build(dev: bool) -> None:
    env = "development" if dev else "production"
    print(f"building (JEKYLL_ENV={env}) ...")
    script = (
        f"rm -rf {CONTAINER_DEST} && "
        f"JEKYLL_ENV={env} bundle exec jekyll build --destination {CONTAINER_DEST}"
    )
    p = run(
        ["docker", "compose", "exec", "-T", SERVICE, "bash", "-c", script],
        capture_output=True,
    )
    if p.returncode != 0:
        tail = "\n".join((p.stdout + p.stderr).splitlines()[-25:])
        die(f"the Jekyll build failed:\n{tail}")
    for line in p.stdout.splitlines():
        if "done in" in line:
            print(" ", line.strip())


def copy_out(cid: str) -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    if run(["docker", "cp", f"{cid}:{CONTAINER_DEST}", str(OUT)], capture_output=True).returncode:
        die("`docker cp` failed")
    files = sum(1 for _ in OUT.rglob("*") if _.is_file())
    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"  copied {files:,} files ({size / 1_048_576:,.1f} MiB) to {OUT.name}/")


def free_port(port: int) -> int:
    for candidate in range(port, port + 20):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", candidate)) != 0:
                return candidate
        print(f"  port {candidate:,} is busy, trying the next one")
    die(f"no free port in {port:,}-{port + 19:,}")


def serve(port: int, open_browser: bool) -> None:
    if not (OUT / "index.html").exists():
        die(f"{OUT} has no index.html -- run without --no-build first")

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))

    class Server(socketserver.TCPServer):
        allow_reuse_address = True

        def handle_error(self, request, client_address):
            exc = sys.exc_info()[1]
            if not isinstance(exc, (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)):
                super().handle_error(request, client_address)

    with Server(("127.0.0.1", port), handler) as httpd:
        url = f"http://localhost:{port}/"
        print(f"\n  serving at {url}")
        print("  Ctrl-C to stop\n")
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


def main() -> None:
    # Unbuffered, so progress is visible when stdout is redirected or piped.
    sys.stdout.reconfigure(line_buffering=True)

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=4000, help="host port (default: 4000)")
    ap.add_argument("--no-build", action="store_true", help="serve the previous build")
    ap.add_argument("--dev", action="store_true", help="build with JEKYLL_ENV=development")
    ap.add_argument("--open", action="store_true", help="open a browser once serving")
    args = ap.parse_args()

    if not args.no_build:
        cid = ensure_container()
        build(args.dev)
        copy_out(cid)

    serve(free_port(args.port), args.open)


if __name__ == "__main__":
    main()
