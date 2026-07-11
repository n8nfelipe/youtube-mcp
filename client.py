import json
from typing import Any
from urllib.parse import urlencode

import httpx
from youtube_transcript_api import YouTubeTranscriptApi

from auth import YouTubeAuth
from models import Channel, Comment, Video

API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeClient:
    def __init__(self, auth: YouTubeAuth) -> None:
        self.api_key = auth.api_key
        self.client = httpx.Client(timeout=30.0)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if params is None:
            params = {}
        params["key"] = self.api_key
        url = f"{API_BASE}/{path}?{urlencode(params, doseq=True)}"
        resp = self.client.get(url)
        if resp.status_code == 403:
            raise Exception("YouTube API key is invalid or quota exceeded.")
        if resp.status_code == 429:
            raise Exception("YouTube API quota exceeded. Try again later.")
        resp.raise_for_status()
        return resp.json()

    def search_videos(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        data = self._get("search", {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max_results, 50),
        })
        return [self._parse_search_item(item) for item in data.get("items", [])]

    def get_trending_videos(self, region_code: str = "BR", category_id: str = "") -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region_code.upper(),
            "maxResults": 50,
        }
        if category_id:
            params["videoCategoryId"] = category_id
        data = self._get("videos", params)
        return [self._parse_video(item) for item in data.get("items", [])]

    def get_video_details(self, video_id: str) -> dict[str, Any]:
        data = self._get("videos", {
            "part": "snippet,statistics,contentDetails",
            "id": video_id,
        })
        items = data.get("items", [])
        if not items:
            raise Exception(f"Video not found: {video_id}")
        return self._parse_video(items[0])

    def get_channel_info(self, channel_id: str) -> dict[str, Any]:
        data = self._get("channels", {
            "part": "snippet,statistics",
            "id": channel_id,
        })
        items = data.get("items", [])
        if not items:
            raise Exception(f"Channel not found: {channel_id}")
        return self._parse_channel(items[0])

    def get_channel_videos(self, channel_id: str, max_results: int = 10) -> list[dict[str, Any]]:
        data = self._get("search", {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "maxResults": min(max_results, 50),
        })
        return [self._parse_search_item(item) for item in data.get("items", [])]

    def get_video_comments(self, video_id: str, max_results: int = 20) -> list[dict[str, Any]]:
        data = self._get("commentThreads", {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(max_results, 100),
            "order": "relevance",
        })
        return [self._parse_comment(item) for item in data.get("items", [])]

    def get_video_transcript(self, video_id: str, lang: str = "pt") -> list[dict[str, Any]]:
        try:
            transcript = YouTubeTranscriptApi.fetch(video_id, languages=[lang])
        except Exception:
            transcript = YouTubeTranscriptApi.fetch(video_id)
        return [{"text": t.text, "start": t.start, "duration": t.duration} for t in transcript]

    def search_ai_communities(self, query: str = "artificial intelligence", max_results: int = 10) -> list[dict[str, Any]]:
        data = self._get("search", {
            "part": "snippet",
            "q": query,
            "type": "channel",
            "maxResults": min(max_results, 50),
        })
        results = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            channel_id = snippet["channelId"]
            try:
                info = self.get_channel_info(channel_id)
            except Exception:
                info = {}
            results.append({
                "channel_id": channel_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:300],
                "subscriber_count": info.get("subscriber_count", 0),
                "video_count": info.get("video_count", 0),
            })
        results.sort(key=lambda x: x["subscriber_count"], reverse=True)
        return results

    def _parse_search_item(self, item: dict[str, Any]) -> dict[str, Any]:
        snippet = item["snippet"]
        return {
            "video_id": item["id"]["videoId"],
            "title": snippet.get("title", ""),
            "description": snippet.get("description", "")[:200],
            "channel_id": snippet.get("channelId", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnails": snippet.get("thumbnails", {}),
        }

    def _parse_video(self, item: dict[str, Any]) -> dict[str, Any]:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        return {
            "video_id": item["id"],
            "title": snippet.get("title", ""),
            "description": snippet.get("description", "")[:300],
            "channel_id": snippet.get("channelId", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "tags": snippet.get("tags", []),
            "category_id": snippet.get("categoryId", ""),
            "duration": content.get("duration", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "thumbnails": snippet.get("thumbnails", {}),
        }

    def _parse_channel(self, item: dict[str, Any]) -> dict[str, Any]:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        return {
            "channel_id": item["id"],
            "title": snippet.get("title", ""),
            "description": snippet.get("description", "")[:300],
            "custom_url": snippet.get("customUrl", ""),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "country": snippet.get("country", ""),
        }

    def _parse_comment(self, item: dict[str, Any]) -> dict[str, Any]:
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        return {
            "comment_id": item["id"],
            "author": snippet.get("authorDisplayName", ""),
            "text": snippet.get("textDisplay", "")[:500],
            "like_count": int(snippet.get("likeCount", 0)),
            "published_at": snippet.get("publishedAt", ""),
        }

    def close(self) -> None:
        self.client.close()
