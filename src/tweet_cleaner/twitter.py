from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar, Optional, cast

from dateutil.parser import parse as dateutil_parse
from requests_oauthlib import OAuth1Session

from .cipher import decrypt


@dataclass
class Tweet:
    tweet_id: str
    user_id: str
    in_reply_to_user_id: str
    created_at: datetime
    text: str
    elapsed: timedelta
    favorite_count: int
    retweet_count: int
    is_quoted_rt: bool
    is_rt: bool
    is_reply: bool

    def __init__(self, tweet: dict[str, Any]) -> None:
        self.tweet_id = cast(str, tweet.get("id"))
        self.user_id = cast(str, tweet.get("user", {}).get("id"))
        self.in_reply_to_user_id = cast(str, tweet.get("in_reply_to_user_id"))
        self.created_at = dateutil_parse(tweet.get("created_at"))
        self.text = cast(str, tweet.get("text"))
        self.elapsed = datetime.now(timezone.utc) - self.created_at
        self.favorite_count = cast(int, tweet.get("favorite_count", 0))
        self.retweet_count = cast(int, tweet.get("retweet_count", 0))
        self.is_quoted_rt = bool(tweet.get("quoted_status"))
        self.is_rt = bool(tweet.get("retweeted_status")) and not self.is_quoted_rt
        self.is_reply = bool(self.in_reply_to_user_id and self.in_reply_to_user_id != self.user_id)


@dataclass
class TwitterClient:
    session: OAuth1Session
    MAX_FETCH_COUNT: ClassVar[int] = 200

    def __init__(self, user_config_key: str) -> None:
        self.session = OAuth1Session(
            decrypt("ENCRYPTED_API_KEY"),
            decrypt("ENCRYPTED_API_SECRET_KEY"),
            decrypt("ENCRYPTED_ACCESS_TOKEN", user_config_key),
            decrypt("ENCRYPTED_ACCESS_TOKEN_SECRET", user_config_key),
        )

    def get_user_timeline(
        self, screen_name: str, max_tweet_id: Optional[str] = None
    ) -> list[Tweet]:
        url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        params = {
            "screen_name": screen_name,
            "count": TwitterClient.MAX_FETCH_COUNT,
            "exclude_replies": False,
            "include_rts": True,
        }
        if max_tweet_id is not None:
            params |= {"max_id": max_tweet_id}
        res = self.session.get(url, params=params)
        res.raise_for_status()
        return list(map(Tweet, json.loads(res.text)))

    def destory(self, tweet: Tweet) -> int:
        url = f"https://api.twitter.com/1.1/statuses/destroy/{tweet.tweet_id}.json"
        res = self.session.post(url)
        res.raise_for_status()
        return res.status_code
