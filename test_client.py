
import pytest
import respx

from auth import YouTubeAuth
from client import YouTubeClient

API_BASE = "https://www.googleapis.com/youtube/v3"


@pytest.fixture
def auth() -> YouTubeAuth:
    return YouTubeAuth(api_key="test_key")


@pytest.fixture
def client(auth: YouTubeAuth) -> YouTubeClient:
    return YouTubeClient(auth)


@respx.mock
def test_search_videos(client: YouTubeClient) -> None:
    route = respx.get(f"{API_BASE}/search").respond(
        200,
        json={
            "items": [
                {
                    "id": {"videoId": "abc123"},
                    "snippet": {
                        "title": "Test Video",
                        "description": "A test",
                        "channelId": "ch1",
                        "channelTitle": "Channel",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "thumbnails": {},
                    },
                }
            ]
        },
    )
    result = client.search_videos("test")
    assert route.called
    assert len(result) == 1
    assert result[0]["title"] == "Test Video"
    assert result[0]["video_id"] == "abc123"


@respx.mock
def test_get_trending_videos(client: YouTubeClient) -> None:
    route = respx.get(f"{API_BASE}/videos").respond(
        200,
        json={
            "items": [
                {
                    "id": "trend1",
                    "snippet": {"title": "Trending", "channelId": "ch1", "channelTitle": "Ch", "publishedAt": "", "tags": [], "categoryId": "", "thumbnails": {}},
                    "statistics": {"viewCount": "1000", "likeCount": "100", "commentCount": "10"},
                    "contentDetails": {"duration": "PT5M"},
                }
            ]
        },
    )
    result = client.get_trending_videos("US")
    assert route.called
    assert len(result) == 1
    assert result[0]["title"] == "Trending"
    assert result[0]["view_count"] == 1000
    assert result[0]["duration"] == "PT5M"


@respx.mock
def test_get_video_details(client: YouTubeClient) -> None:
    respx.get(f"{API_BASE}/videos").respond(
        200,
        json={
            "items": [
                {
                    "id": "vid1",
                    "snippet": {"title": "Detail", "channelId": "ch1", "channelTitle": "Ch", "publishedAt": "", "tags": [], "categoryId": "", "thumbnails": {}},
                    "statistics": {"viewCount": "500", "likeCount": "50", "commentCount": "5"},
                    "contentDetails": {"duration": "PT10M"},
                }
            ]
        },
    )
    result = client.get_video_details("vid1")
    assert result["title"] == "Detail"
    assert result["like_count"] == 50


@respx.mock
def test_get_video_details_not_found(client: YouTubeClient) -> None:
    respx.get(f"{API_BASE}/videos").respond(200, json={"items": []})
    with pytest.raises(Exception, match="Video not found"):
        client.get_video_details("invalid")


@respx.mock
def test_get_channel_info(client: YouTubeClient) -> None:
    respx.get(f"{API_BASE}/channels").respond(
        200,
        json={
            "items": [
                {
                    "id": "ch1",
                    "snippet": {"title": "My Channel", "description": "Desc", "customUrl": "@my", "publishedAt": "", "thumbnails": {"default": {"url": "img.jpg"}}, "country": "BR"},
                    "statistics": {"subscriberCount": "10000", "videoCount": "50", "viewCount": "500000"},
                }
            ]
        },
    )
    result = client.get_channel_info("ch1")
    assert result["title"] == "My Channel"
    assert result["subscriber_count"] == 10000
    assert result["channel_id"] == "ch1"


@respx.mock
def test_get_channel_info_not_found(client: YouTubeClient) -> None:
    respx.get(f"{API_BASE}/channels").respond(200, json={"items": []})
    with pytest.raises(Exception, match="Channel not found"):
        client.get_channel_info("invalid")


@respx.mock
def test_get_channel_videos(client: YouTubeClient) -> None:
    route = respx.get(f"{API_BASE}/search").respond(
        200,
        json={
            "items": [
                {
                    "id": {"videoId": "v1"},
                    "snippet": {"title": "Vid", "description": "D", "channelId": "ch1", "channelTitle": "Ch", "publishedAt": "", "thumbnails": {}},
                }
            ]
        },
    )
    result = client.get_channel_videos("ch1", 5)
    assert route.called
    assert len(result) == 1


@respx.mock
def test_get_video_comments(client: YouTubeClient) -> None:
    route = respx.get(f"{API_BASE}/commentThreads").respond(
        200,
        json={
            "items": [
                {
                    "id": "c1",
                    "snippet": {
                        "topLevelComment": {
                            "snippet": {
                                "authorDisplayName": "User",
                                "textDisplay": "Great video!",
                                "likeCount": "5",
                                "publishedAt": "2024-01-01T00:00:00Z",
                            }
                        }
                    },
                }
            ]
        },
    )
    result = client.get_video_comments("v1")
    assert route.called
    assert result[0]["author"] == "User"
    assert result[0]["text"] == "Great video!"
    assert result[0]["like_count"] == 5


@respx.mock
def test_search_ai_communities(client: YouTubeClient) -> None:
    respx.get(f"{API_BASE}/search").respond(
        200,
        json={
            "items": [
                {
                    "id": {"channelId": "ch_ai"},
                    "snippet": {"title": "AI Channel", "description": "AI content", "channelId": "ch_ai"},
                }
            ]
        },
    )
    respx.get(f"{API_BASE}/channels").respond(
        200,
        json={
            "items": [
                {
                    "id": "ch_ai",
                    "snippet": {"title": "AI Channel", "description": "AI", "customUrl": "", "publishedAt": "", "thumbnails": {}, "country": ""},
                    "statistics": {"subscriberCount": "50000", "videoCount": "200", "viewCount": "1000000"},
                }
            ]
        },
    )
    result = client.search_ai_communities("AI", 5)
    assert len(result) == 1
    assert result[0]["channel_id"] == "ch_ai"
    assert result[0]["subscriber_count"] == 50000


@respx.mock
def test_api_key_invalid(client: YouTubeClient) -> None:
    respx.get(f"{API_BASE}/videos").respond(403)
    with pytest.raises(Exception, match="API key is invalid"):
        client.get_video_details("vid1")


@respx.mock
def test_rate_limit(client: YouTubeClient) -> None:
    respx.get(f"{API_BASE}/videos").respond(429)
    with pytest.raises(Exception, match="quota exceeded"):
        client.get_video_details("vid1")


@respx.mock
def test_get_video_transcript(client: YouTubeClient, mocker) -> None:
    mock_api = mocker.patch("client.YouTubeTranscriptApi")
    mock_instance = mocker.MagicMock()
    mock_api.return_value = mock_instance
    mock_segment = mocker.MagicMock()
    mock_segment.text = "Hello world"
    mock_segment.start = 0.0
    mock_segment.duration = 2.0
    mock_instance.fetch.return_value = [mock_segment]
    result = client.get_video_transcript("abc123", "en")
    assert len(result) == 1
    assert result[0]["text"] == "Hello world"
    assert result[0]["start"] == 0.0
