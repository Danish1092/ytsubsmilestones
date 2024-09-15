import tweepy
import requests
import json
from io import BytesIO

# Twitter API credentials
bearer_token = "AAAAAAAAAAAAAAAAAAAAAO%2BIuQEAAAAAoKpWMVxs2qirbsdr3%2FZMaQCmt5g%3DjLb8hElyXKjXbAq3TF6iEGQtjdeXm8g3z39BrYgNFr3PhiDyQ9"
consumer_key = "eNmC7WvB9jroA2t8z7O1nYEJA"
consumer_secret = "RpL0Y6qtJmji9MlFRKxLUUuKsesjsHevSFOPYQAK5ZZ4DHMpFH"
access_token = "1802930626775093248-79sbETqyPswk4akrh7DIXSYiqH63px"
access_token_secret = "5f12eIWVCeavDgde90tsc6jvQuVrThfXtyrt2ZVS0lanQ"

# V1 Twitter API Authentication for media uploads
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# V2 Twitter API Authentication for creating tweets
client = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    wait_on_rate_limit=True,
)

# RapidAPI credentials
API_KEY = "2f8f894712msh7d82c6769d2fd10p198299jsn06206fa10e88"
API_HOST = "yt-api.p.rapidapi.com"

def fetch_channel_details(channel_id):
    url = "https://yt-api.p.rapidapi.com/channel/about"
    querystring = {"id": channel_id}
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        subscriber_count = data.get("subscriberCount")

        profile_pics = data.get("avatar")
        if profile_pics and isinstance(profile_pics, list):
            profile_pic_url = profile_pics[-1].get("url")
        else:
            profile_pic_url = None

        return subscriber_count, profile_pic_url

    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for channel {channel_id}: {str(e)}")
        return None, None

def check_and_tweet():
    with open('channel_data.json', 'r') as f:
        channels = json.load(f)

    tweets_sent = False
    for channel in channels:
        current_count, profile_pic_url = fetch_channel_details(channel["id"])
        if current_count and channel["subscribers"] is not None:
            current_milestone = (current_count // 1000000) * 1000000
            previous_milestone = (channel["subscribers"] // 1000000) * 1000000

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
