from unittest.mock import patch

from auth import YouTubeAuth


def test_auth_valid() -> None:
    auth = YouTubeAuth(api_key="key123")
    assert auth.is_valid is True


def test_auth_invalid() -> None:
    auth = YouTubeAuth()
    assert auth.is_valid is False


def test_auth_loading() -> None:
    with patch("auth.load_dotenv"):
        with patch("os.getenv", return_value="env_key"):
            from auth import load_auth

            a = load_auth()
            assert a.api_key == "env_key"


@patch("client.YouTubeClient._get")
def test_search_videos_tool(mock_get) -> None:
    mock_get.return_value = {
        "items": [
            {
                "id": {"videoId": "v1"},
                "snippet": {"title": "T", "description": "D", "channelId": "c1", "channelTitle": "C", "publishedAt": "2024-01-01T00:00:00Z", "thumbnails": {}},
            }
        ]
    }
    from client import YouTubeClient

    client = YouTubeClient(YouTubeAuth(api_key="k"))
    result = client.search_videos("test")
    assert result[0]["video_id"] == "v1"


@patch("client.YouTubeClient._get")
def test_trending_tool(mock_get) -> None:
    mock_get.return_value = {
        "items": [
            {
                "id": "t1",
                "snippet": {"title": "Trend", "channelId": "c1", "channelTitle": "C", "publishedAt": "", "tags": [], "categoryId": "", "thumbnails": {}},
                "statistics": {"viewCount": "100", "likeCount": "10", "commentCount": "1"},
                "contentDetails": {"duration": "PT1M"},
            }
        ]
    }
    from client import YouTubeClient

    client = YouTubeClient(YouTubeAuth(api_key="k"))
    result = client.get_trending_videos("BR")
    assert result[0]["title"] == "Trend"
    assert result[0]["view_count"] == 100
