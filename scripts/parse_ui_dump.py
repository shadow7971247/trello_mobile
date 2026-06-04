import re
import sys
from pathlib import Path

s = Path(sys.argv[1]).read_text(encoding="utf-8")
texts = [t for t in re.findall(r'text="([^"]+)"', s) if t.strip()]
for t in texts:
    print(t)
