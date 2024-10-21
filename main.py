import os
import tweepy
import requests
import json
from io import BytesIO

bearer_token = os.environ['TWITTER_BEARER_TOKEN']
consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    wait_on_rate_limit=True,
)

API_KEY = os.environ['YOUTUBE_API_KEY']

def fetch_channel_details(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            channel_info = data["items"][0]

            subscriber_count = int(channel_info["statistics"]["subscriberCount"])

            profile_picture_url = channel_info["snippet"]["thumbnails"]["high"]["url"]
            return subscriber_count, profile_picture_url
        else:
            print(f"No details found for channel {channel_id}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for channel {channel_id}: {str(e)}")
        return None, None

def check_and_tweet():
    with open('channel_data.json', 'r') as f:
        channels = json.load(f)

    tweets_sent = False

    for channel in channels:
        current_count, profile_pic_url = fetch_channel_details(channel["id"])
        if current_count is not None:
            current_milestone = (current_count // 1000000) * 1000000
            previous_milestone = channel.get("last_tweeted_milestone", 0)

            print(f"Checking {channel['name']} - Current Milestone: {current_milestone}, Previous Milestone: {previous_milestone}")

            if current_milestone > previous_milestone:
                tweet_text = (f"{channel['name']} has crossed {current_milestone // 1000000} Million subscribers on YouTube!\n"
                              f"#{channel['name'].replace(' ', '')} #youtube")

                try:
                    if profile_pic_url:
                        response = requests.get(profile_pic_url)
                        response.raise_for_status()
                        image_bytes = BytesIO(response.content)
                        media_id = api.media_upload(filename="profile_pic.jpg", file=image_bytes).media_id_string
                        client.create_tweet(text=tweet_text, media_ids=[media_id])
                    else:
                        client.create_tweet(text=tweet_text)

                    print(f"Tweet sent: {tweet_text}")
                    tweets_sent = True

                    channel["last_tweeted_milestone"] = current_milestone

                except requests.exceptions.RequestException as e:
                    print(f"Error downloading image for {channel['name']}: {str(e)}")
                except tweepy.TweepyException as e:
                    print(f"Error tweeting for {channel['name']}: {str(e)}")
                    if e.api_code:
                        print(f"API Code: {e.api_code}")
                    if e.response:
                        print(f"Response content: {e.response.text}")
            channel["subscribers"] = current_count
    with open('channel_data.json', 'w') as f:
        json.dump(channels, f, indent=4)

    if not tweets_sent:
        print("No new milestones reached. Channel data updated.")

if __name__ == "__main__":
    check_and_tweet()
