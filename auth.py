import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class YouTubeAuth:
    api_key: str = ""

    @property
    def is_valid(self) -> bool:
        return bool(self.api_key)


def load_auth() -> YouTubeAuth:
    return YouTubeAuth(
        api_key=os.getenv("YOUTUBE_API_KEY", ""),
    )
