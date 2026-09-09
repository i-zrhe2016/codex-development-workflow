#!/usr/bin/env python3
"""Stream Codex review into recoverable, worktree-local Git metadata.

Exit 0 means execution completed, never that the review passed. The main
agent must inspect the saved conclusion and explicitly record its assessment.
"""

import argparse
import fcntl
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time
import uuid


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def save(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(path)


def choose_scope(base, head, previous, incremental):
    if (incremental and previous and previous.get("base") == base
            and previous.get("assessment") in ("pass", "blocking")
            and previous.get("head") != head
            and subprocess.run(["git", "merge-base", "--is-ancestor",
                                previous["head"], head]).returncode == 0):
        return previous["head"]
    return base


def stream(command, log_path, state, state_path, interval=300):
    started = last_output = time.monotonic()
    next_notice = started + interval
    child = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, start_new_session=True)
    state["child_pid"] = child.pid
    save(state_path, state)
    selector = selectors.DefaultSelector()
    selector.register(child.stdout, selectors.EVENT_READ)
    try:
        with log_path.open("wb") as log:
            while selector.get_map():
                for key, _ in selector.select(timeout=1):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    log.write(chunk)
                    log.flush()
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
                    last_output = time.monotonic()
                now = time.monotonic()
                if now >= next_notice:
                    print(f"\nReview elapsed={int(now-started)}s "
                          f"output_idle={int(now-last_output)}s log={log_path}",
                          flush=True)
                    if now - started >= 900:
                        print("Inspect progress/errors; silence alone is not a failure. "
                              "No automatic restart or pass.", flush=True)
                    next_notice = now + interval
        return child.wait()
    finally:
        selector.close()
        child.stdout.close()
        if child.poll() is None:
            import signal
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Actual PR base ref")
    parser.add_argument("--incremental", action="store_true",
                        help="Agent confirms only bounded fixes since last assessed review")
    parser.add_argument("--force-full", action="store_true",
                        help="Require new full coverage even when this head has a saved result")
    parser.add_argument("--record", choices=("pass", "blocking"))
    parser.add_argument("--note", help="Conclusion evidence, including prior finding resolution")
    args = parser.parse_args()
    if git("status", "--porcelain"):
        parser.error("Review requires a clean worktree")
    base = git("rev-parse", "--verify", args.base + "^{commit}")
    head = git("rev-parse", "HEAD")
    directory = Path(git("rev-parse", "--absolute-git-dir")) / "codex-review"
    directory.mkdir(mode=0o700, exist_ok=True)
    state_path = directory / "state.json"
    with (directory / "lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"Review already active; inspect {state_path}")
            return 2
        previous = json.loads(state_path.read_text()) if state_path.exists() else None
        same = previous and previous.get("base") == base and previous.get("head") == head
        if args.record:
            if not (same and previous.get("status") == "completed" and args.note):
                parser.error("Recording requires matching completed execution and --note evidence")
            previous.update(assessment=args.record, note=args.note)
            save(state_path, previous)
            print(json.dumps(previous, indent=2))
            return 0
        if same and previous.get("status") == "completed" and not args.force_full:
            print(json.dumps(previous, indent=2))
            print("Reuse saved execution; inspect log and explicitly assess if pending.")
            return 0
        if previous and previous.get("status") == "running":
            # A crashed parent can leave a review child alive. Do not duplicate it.
            try:
                os.kill(previous["child_pid"], 0)
            except (ProcessLookupError, KeyError):
                previous["status"] = "interrupted"
                save(state_path, previous)
            else:
                print(f"Previous child may still be active; inspect {state_path}")
                return 2
        scope = choose_scope(base, head, previous, args.incremental and not args.force_full)
        run_id = uuid.uuid4().hex
        log_path = directory / (run_id + ".log")
        if previous:
            save(directory / (previous["run_id"] + ".json"), previous)
        state = dict(run_id=run_id, base=base, head=head, scope=scope,
                     previous_run=previous.get("run_id") if scope != base else None,
                     status="running", assessment="pending", log=str(log_path),
                     started_at=time.time(), pid=os.getpid())
        save(state_path, state)
        print(f"Review {scope}..{head}; log={log_path}", flush=True)
        try:
            code = stream(["codex", "review", "--base", scope], log_path, state, state_path)
            unchanged = git("rev-parse", "HEAD") == head and not git("status", "--porcelain")
            state.update(exit_code=code, status="completed" if code == 0 and unchanged else "incomplete")
        except BaseException:
            state["status"] = "interrupted"
            raise
        finally:
            state["finished_at"] = time.time()
            save(state_path, state)
        print(f"\nExecution {state['status']}; assessment pending. Log: {log_path}")
        return 0 if state["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
