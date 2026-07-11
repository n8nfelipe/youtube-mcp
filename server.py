#!/usr/bin/env python3
import sys
from mcp.server.fastmcp import FastMCP

from auth import load_auth
from client import YouTubeClient

auth = load_auth()
if not auth.is_valid:
    print("Error: YOUTUBE_API_KEY must be set in .env file.", file=sys.stderr)
    sys.exit(1)

client = YouTubeClient(auth)
mcp = FastMCP(
    "youtube-mcp",
    instructions="Interact with YouTube: search videos, get transcripts, find trending content, explore AI communities.",
)


@mcp.tool()
def search_videos(query: str, max_results: int = 10) -> str:
    """Search for YouTube videos by keyword.

    Args:
        query: Search query string
        max_results: Number of results (max 50, default 10)
    """
    return str(client.search_videos(query, max_results))


@mcp.tool()
def get_trending_videos(region_code: str = "BR", category_id: str = "") -> str:
    """Get trending YouTube videos for a region.

    Args:
        region_code: ISO 3166-1 alpha-2 country code (default BR)
        category_id: YouTube video category ID (optional)
    """
    return str(client.get_trending_videos(region_code, category_id))


@mcp.tool()
def get_video_details(video_id: str) -> str:
    """Get detailed metadata about a specific video.

    Args:
        video_id: YouTube video ID
    """
    return str(client.get_video_details(video_id))


@mcp.tool()
def get_video_transcript(video_id: str, lang: str = "pt") -> str:
    """Get the transcript/subtitles of a YouTube video.

    Args:
        video_id: YouTube video ID
        lang: Language code (default pt). Falls back to auto if not found.
    """
    return str(client.get_video_transcript(video_id, lang))


@mcp.tool()
def get_channel_info(channel_id: str) -> str:
    """Get information about a YouTube channel.

    Args:
        channel_id: YouTube channel ID
    """
    return str(client.get_channel_info(channel_id))


@mcp.tool()
def get_channel_videos(channel_id: str, max_results: int = 10) -> str:
    """Get the latest videos from a YouTube channel.

    Args:
        channel_id: YouTube channel ID
        max_results: Number of videos (max 50, default 10)
    """
    return str(client.get_channel_videos(channel_id, max_results))


@mcp.tool()
def get_video_comments(video_id: str, max_results: int = 20) -> str:
    """Get comments from a YouTube video, sorted by relevance.

    Args:
        video_id: YouTube video ID
        max_results: Number of comments (max 100, default 20)
    """
    return str(client.get_video_comments(video_id, max_results))


@mcp.tool()
def search_ai_communities(query: str = "artificial intelligence", max_results: int = 10) -> str:
    """Search for AI-focused YouTube channels/communities, sorted by subscribers.

    Args:
        query: Search query for AI communities (default 'artificial intelligence')
        max_results: Number of results (max 50, default 10)
    """
    return str(client.search_ai_communities(query, max_results))


if __name__ == "__main__":
    mcp.run()
