import feedparser
import re
from datetime import datetime

FEED_URL = "https://medium.com/feed/@cucyzx"
README   = "README.md"
START    = "<!-- MEDIUM:START -->"
END      = "<!-- MEDIUM:END -->"

feed = feedparser.parse(FEED_URL)

if not feed.entries:
    print("No Medium entries found — skipping update")
    exit(0)

def get_thumbnail(entry):
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0]["url"]
    if hasattr(entry, "media_content") and entry.media_content:
        return entry.media_content[0].get("url")
    html = (entry.get("content") or [{}])[0].get("value", "") or entry.get("summary", "")
    m = re.search(r'<img[^>]+src="([^"]+)"', html)
    return m.group(1) if m else None

def format_date(entry):
    try:
        return datetime(*entry.published_parsed[:6]).strftime("%b %d, %Y")
    except Exception:
        return ""

def cell(entry):
    thumb = get_thumbnail(entry)
    title = entry.title
    link  = entry.link
    date  = format_date(entry)
    img   = f'<a href="{link}"><img src="{thumb}" width="260" /></a><br/><br/>' if thumb else ""
    return f"""\
<td width="50%" align="center" valign="top">
{img}<a href="{link}"><b>{title}</b></a><br/>
<sub>{date}</sub>
</td>"""

entries = feed.entries[:2]
cells   = "\n".join(cell(e) for e in entries)

card = f"""\
<table width="100%" border="0" cellpadding="16" cellspacing="0">
<tr>
{cells}
</tr>
</table>"""

with open(README) as f:
    content = f.read()

new_block = f"{START}\n{card}\n{END}"
updated   = re.sub(
    re.escape(START) + r".*?" + re.escape(END),
    new_block,
    content,
    flags=re.DOTALL,
)

with open(README, "w") as f:
    f.write(updated)

print(f"Updated README with {len(entries)} articles")
