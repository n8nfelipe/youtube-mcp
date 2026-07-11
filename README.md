# YouTube MCP Server

MCP (Model Context Protocol) server to interact with YouTube: search videos, get transcripts, find trending content, and explore AI communities.

## Features

- Search videos by keyword
- Get trending videos by region and category
- Fetch video transcripts/subtitles (no API key needed for transcripts)
- Get detailed video metadata
- Look up channel info and latest uploads
- Read video comments
- Discover and rank AI-focused communities by subscribers

## Prerequisites

- **YouTube Data API v3 key** — get one at https://console.cloud.google.com/apis/credentials
- Enable the YouTube Data API v3 in your Google Cloud project

## Quick Start

```bash
cp .env.example .env
# Edit .env with your YOUTUBE_API_KEY

pip install -r requirements.txt
python server.py
```

## Tools

| Tool | Description | Arguments |
|---|---|---|
| `search_videos` | Search videos by keyword | `query` (string, required), `max_results` (int, default 10, max 50) |
| `get_trending_videos` | Trending in a region | `region_code` (string, default BR), `category_id` (string, optional) |
| `get_video_details` | Full video metadata | `video_id` (string, required) |
| `get_video_transcript` | Video transcript/subtitles | `video_id` (string, required), `lang` (string, default pt) |
| `get_channel_info` | Channel profile and stats | `channel_id` (string, required) |
| `get_channel_videos` | Latest videos from channel | `channel_id` (string, required), `max_results` (int, default 10) |
| `get_video_comments` | Comments sorted by relevance | `video_id` (string, required), `max_results` (int, default 20, max 100) |
| `search_ai_communities` | Find AI communities, sorted by subscribers | `query` (string, default 'artificial intelligence'), `max_results` (int, default 10) |

## Register with opencode

```jsonc
{
  "mcpServers": {
    "youtube": {
      "command": "python3",
      "args": ["/caminho/para/youtube-mcp/server.py"],
      "env": {
        "YOUTUBE_API_KEY": "sua_chave"
      }
    }
  }
}
```

## How it works

Uses the YouTube Data API v3 for metadata, search, and comments, and `youtube-transcript-api` for subtitles (no extra auth needed).

## Tests

```bash
python -m pytest . -v
```
