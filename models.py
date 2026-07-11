from dataclasses import dataclass
from typing import Any


@dataclass
class Video:
    id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: str
    thumbnails: dict[str, Any]
    tags: list[str]
    category_id: str
    duration: str
    view_count: int
    like_count: int
    comment_count: int


@dataclass
class Channel:
    id: str
    title: str
    description: str
    custom_url: str
    published_at: str
    thumbnail: str
    subscriber_count: int
    video_count: int
    view_count: int
    country: str


@dataclass
class Comment:
    id: str
    author: str
    text: str
    like_count: int
    published_at: str
