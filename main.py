import tweepy
import requests
import json
from io import BytesIO

# Use your actual API credentials for Twitter
bearer_token = "YOUR_BEARER_TOKEN"
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

        # Extract the subscriber count
        subscriber_count = data.get("subscriberCount")

        # Extract the highest quality profile picture URL from the list of avatars
        profile_pics = data.get("avatar")
        if profile_pics and isinstance(profile_pics, list):
            profile_pic_url = profile_pics[-1].get("url")  # Choose the largest available picture
        else:
            profile_pic_url = None

        return subscriber_count, profile_pic_url

    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for channel {channel_id}: {str(e)}")
        if response:
            print(f"Response content: {response.text}")
        return None, None

def check_and_tweet():
    # Load channel data from JSON file
    with open('channel_data.json', 'r') as f:
        channels = json.load(f)

    tweets_sent = False
    for channel in channels:
        current_count, profile_pic_url = fetch_channel_details(channel["id"])
        if current_count and channel["subscribers"] is not None:
            # Round down to the nearest million for both current and stored counts
            current_milestone = (current_count // 1000000) * 1000000
            previous_milestone = (channel["subscribers"] // 1000000) * 1000000

            if current_milestone > previous_milestone:  # Check if a new million milestone has been crossed
                tweet_text = (f"{channel['name']} has crossed {current_milestone // 1000000} Million subscribers on YouTube!\n"
                              f"#{channel['name'].replace(' ', '')} #youtuber")

                try:
                    # Upload profile picture and tweet with media (if available)
                    if profile_pic_url:
                        response = requests.get(profile_pic_url)
                        response.raise_for_status()  # Raise an exception for bad status codes
                        image_bytes = BytesIO(response.content)

                        # Upload the image from in-memory bytes
                        media_id = api.media_upload(filename="profile_pic.jpg", file=image_bytes).media_id_string
                        
                        # Create tweet with image using API v2
                        client.create_tweet(text=tweet_text, media_ids=[media_id])
                    else:
                        # Just tweet text if no profile picture is available
                        client.create_tweet(text=tweet_text)

                    print(f"Tweeted: {tweet_text}")
                    tweets_sent = True

                except requests.exceptions.RequestException as e:
                    print(f"Error downloading image for {channel['name']}: {str(e)}")
                    if response:
                        print(f"Response content: {response.text}")

                except tweepy.TweepyException as e:
                    print(f"Error tweeting for {channel['name']}: {str(e)}")
                    # Check if Twitter API response has more detailed error
                    if e.api_code:
                        print(f"API Code: {e.api_code}")
                    if e.response:
                        print(f"Response content: {e.response.text}")

                # Update the subscriber count in the channel data
                channel["subscribers"] = current_count

    # Save the updated channel data back to the JSON file
    with open('channel_data.json', 'w') as f:
        json.dump(channels, f, indent=4)

    if tweets_sent:
        print("Tweets sent for the following channels.")
    else:
        print("No tweets were sent.")

if __name__ == "__main__":
    check_and_tweet()
