import re
import sys

t = sys.stdin.read()
t = re.sub(
    r"(?mi)^Co-authored-by:\s*Cursor\s*<cursoragent@cursor\.com>\s*\r?\n",
    "",
    t,
)
sys.stdout.write(t)
