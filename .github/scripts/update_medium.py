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

entry = feed.entries[0]
title = entry.title
link  = entry.link

# Extract thumbnail: try media fields first, then parse content HTML
thumb = None
if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
    thumb = entry.media_thumbnail[0]["url"]
elif hasattr(entry, "media_content") and entry.media_content:
    thumb = entry.media_content[0].get("url")
else:
    html = (entry.get("content") or [{}])[0].get("value", "") or entry.get("summary", "")
    m = re.search(r'<img[^>]+src="([^"]+)"', html)
    if m:
        thumb = m.group(1)

try:
    dt = datetime(*entry.published_parsed[:6])
    date_str = dt.strftime("%B %d, %Y")
except Exception:
    date_str = ""

if thumb:
    card = f"""\
<table border="0" cellpadding="0" cellspacing="0">
<tr>
<td width="140" valign="top">
<a href="{link}"><img src="{thumb}" width="130" /></a>
</td>
<td valign="middle" style="padding-left:20px">
<a href="{link}"><b>{title}</b></a><br/>
<sub>{date_str}</sub>
</td>
</tr>
</table>"""
else:
    card = f'<a href="{link}"><b>{title}</b></a><br/><sub>{date_str}</sub>'

with open(README) as f:
    content = f.read()

new_block  = f"{START}\n{card}\n{END}"
updated    = re.sub(
    re.escape(START) + r".*?" + re.escape(END),
    new_block,
    content,
    flags=re.DOTALL,
)

with open(README, "w") as f:
    f.write(updated)

print(f"Updated README with: {title}")
