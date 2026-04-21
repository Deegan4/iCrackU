import shutil
import subprocess
from typing import Callable, Optional

def check_tool(name: str) -> bool:
    return shutil.which(name) is not None

def run_tool(
    name: str,
    args: list[str],
    query: str,
    on_line: Optional[Callable[[str], None]],
) -> dict:
    if not check_tool(name):
        return {"tool": name, "query": query, "returncode": -1, "output": f"{name} not found — skipping"}

    cmd = [name] + args
    output_lines = []

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    for line in proc.stdout:
        line = line.rstrip()
        output_lines.append(line)
        if on_line:
            on_line(line)

    proc.wait()
    return {
        "tool": name,
        "query": query,
        "returncode": proc.returncode,
        "output": "\n".join(output_lines),
    }
