import os
from typing import Any, Literal, Optional, Union

from aws_lambda_powertools.logging import Logger

from tweet_cleaner.twitter import TwitterClient
from tweet_cleaner.user_config import DESTROY_RULES, UserConfig

logger = Logger(service="tweet-cleaner")


def response(
    status_code: int,
    content_type: Optional[Literal["text/plain"]] = None,
    body: Optional[str] = None,
) -> dict[str, Any]:
    dic: dict[str, Any] = {"statusCode": status_code}
    if content_type is not None:
        dic["headers"] = {"Content-Type": content_type}
    if body is not None:
        dic["body"] = body
    return dic


@logger.inject_lambda_context
def handler(event, context) -> dict[str, Union[int, str, dict[str, str]]]:
    if event.get("API_KEY", "") != os.environ["LAMBDA_API_KEY"]:
        return response(status_code=401)

    USER_CONFIG_KEYS = os.environ["USER_CONFIG_KEYS"].split(",")
    lambda_status = 200

    for user_config_key in USER_CONFIG_KEYS:
        config = UserConfig.from_user_config_key(user_config_key)
        logger.info(config)

        client = TwitterClient(user_config_key)
        will_discard = DESTROY_RULES[config.destroy_type]

        max_trial = 2
        max_tweet_id: Optional[str] = None
        finished = False
        while max_trial:
            try:
                while True:
                    tweets = client.get_user_timeline(config.screen_name, max_tweet_id)
                    logger.info(
                        {
                            "screen_name": config.screen_name,
                            "number of fetched tweets": len(tweets),
                        }
                    )
                    discard_count = 0
                    for tweet in tweets:
                        if will_discard(config, tweet):
                            logger.info(
                                {
                                    "tweet_id": tweet.tweet_id,
                                    "created_at": tweet.created_at,
                                    "text": tweet.text,
                                    "delete_status": client.destroy(tweet),
                                }
                            )
                            discard_count += 1
                    logger.info({"discard_count": discard_count})
                    if len(tweets) == TwitterClient.MAX_FETCH_COUNT:
                        max_tweet_id = tweets[-1].tweet_id
                        continue
                    if discard_count == 0:
                        finished = True
                        break
            except Exception as ex:
                lambda_status = 500
                logger.exception(ex)

            if finished:
                break
            max_trial -= 1

    return response(
        status_code=lambda_status,
        content_type="text/plain",
        body={
            200: "successfully tweets were deleted",
            500: "some issues happened",
        }.get(lambda_status),
    )
