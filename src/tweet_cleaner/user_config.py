from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass

from .twitter import Tweet


@dataclass(frozen=True)
class Config:
    screen_name: str
    days_wait: int
    favorite_threshold: int
    retweet_threshold: int
    destroy_type: str

    @classmethod
    def from_user_config_key(cls, user_config_key: str) -> Config:
        configs = os.environ[user_config_key].split(",")
        screen_name, days_wait, favorite_threshold, retweet_threshold, destroy_type = configs
        return cls(
            screen_name,
            int(days_wait),
            int(favorite_threshold),
            int(retweet_threshold),
            destroy_type,
        )


DESTROY_RULES: dict[str, Callable[[Config, Tweet], bool]] = {
    "owner": (
        lambda config, tweet: (
            tweet.elapsed.days >= config.days_wait
            and tweet.favorite_count < config.favorite_threshold
            and tweet.retweet_count < config.retweet_threshold
        )
    ),
}
