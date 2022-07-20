from html import entities
import feedparser
from datetime import datetime
import pathlib
import urllib.request
import os
import re

URL = 'http://127.0.0.1:1200/xiaoyuzhou/podcast/60beb756ef742260587c883b?limit=1000'
ONLINE_PREFIX = 'https://podcastsarchive.github.io/babel-dict'
LOCAL_HOST_PREFIX = 'http://localhost:4000/babel-dict'
PREFIX = ONLINE_PREFIX
IMG_URL = 'https://podcastsarchive.github.io/babel-dict/image/img.jpg'
AUTHOR = ' BabelDict '
AUDIO_DIR = './source/audio/'

feed = feedparser.parse(URL)
audio_len = len(os.listdir(AUDIO_DIR))
all_entries = feed['entries']
entries_len = len(all_entries)
entries = all_entries
# entries = all_entries[:entries_len - audio_len]

print(f'new entries {len(entries)}')
print(f'loading podcast from {URL}')

size = index = entries_len

for entry in entries:
    link = entry['links'][1]['href']
    if pathlib.Path(f"./source/audio/vol{index}.m4a").exists():
        index -= 1
        continue
    urllib.request.urlretrieve(link, f"./source/audio/vol{index}.m4a")
    print(f'{index}.m4a /{size} {link}')
    index -= 1

index = size
playlist_items = []

# Generate All Items.
for entry in entries:
    title = entry['title'].replace('"', '')
    date = entry['published']
    date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    # audio = entry['links'][1]['href']
    audio = f'{PREFIX}/audio/vol{index}.m4a'
    detail = entry['title_detail']
    player = '{% aplayer ' + f'"{title}"' + AUTHOR + ' ' + audio + ' ' + IMG_URL + ' %}'
    summary = entry['summary']
    summary = re.sub('style=\".*?\"', '', summary)
    durnation = entry['itunes_duration']
    length = entry['links'][1]['length']
    playlist_items.append( f'{{"title": "{title}", "author": "{AUTHOR}", "url": "{audio}", "pic": "{IMG_URL}"}}')
    md_builder = \
    f'''---
title: "{title}"
date: {date}
duration: '{ durnation }'
media: { audio }
image: { IMG_URL }
length: { length }
type: 'audio/mpeg'
---

{player}

**[Link]({entry['id']})**

## Summary
{summary}
    '''

    pathlib.Path(f'source/_posts/vol{index}.md').write_text(md_builder)
    print(f'generate md file for source/_posts/vol{index}.md')
    index -= 1

# Generate Play List
playlist = \
f'''---
title: "PlayList"
---
{{% aplayerlist %}}
{{
    "narrow": false,
    "autoplay": false,
    "mode": "order",
    "mutex": true,
    "preload": "auto",
    "listmaxheight": "1000px",
    "music": [{','.join(playlist_items)}]
}}
{{% endaplayerlist %}}

'''
pathlib.Path(f'source/playlist.md').write_text(playlist)
