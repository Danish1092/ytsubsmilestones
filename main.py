import os
import tweepy
import requests
import json
from io import BytesIO

# Twitter API credentials
bearer_token = os.environ['TWITTER_BEARER_TOKEN']
consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

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

# YouTube Data API v3 Key
API_KEY = os.environ['YOUTUBE_API_KEY']

def fetch_channel_details(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            channel_info = data["items"][0]

            # Extracting subscriber count
            subscriber_count = int(channel_info["statistics"]["subscriberCount"])

            # Extracting profile picture URL
            profile_picture_url = channel_info["snippet"]["thumbnails"]["high"]["url"]
            return subscriber_count, profile_picture_url
        else:
            print(f"No details found for channel {channel_id}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for channel {channel_id}: {str(e)}")
        return None, None

def check_and_tweet():
    # Load the channel data from the JSON file
    with open('channel_data.json', 'r') as f:
        channels = json.load(f)

    tweets_sent = False

    # Loop through each channel in the JSON file
    for channel in channels:
        current_count, profile_pic_url = fetch_channel_details(channel["id"])
        if current_count is not None:
            # Calculate the next million milestone
            current_milestone = (current_count // 1000000) * 1000000
            previous_milestone = channel.get("last_tweeted_milestone", 0)

            # Debugging: Checking the milestone calculation
            print(f"Checking {channel['name']} - Current Milestone: {current_milestone}, Previous Milestone: {previous_milestone}")

            # Check if the current milestone is greater than the previous one
            if current_milestone > previous_milestone:
                tweet_text = (f"{channel['name']} has crossed {current_milestone // 1000000} Million subscribers on YouTube!\n"
                              f"#{channel['name'].replace(' ', '')} #youtube")

                try:
                    # Tweet with profile picture if available
                    if profile_pic_url:
                        response = requests.get(profile_pic_url)
                        response.raise_for_status()
                        image_bytes = BytesIO(response.content)
                        media_id = api.media_upload(filename="profile_pic.jpg", file=image_bytes).media_id_string
                        client.create_tweet(text=tweet_text, media_ids=[media_id])
                    else:
                        # Tweet without image if no profile picture is available
                        client.create_tweet(text=tweet_text)

                    print(f"Tweet sent: {tweet_text}")
                    tweets_sent = True

                    # Update the last tweeted milestone after a successful tweet
                    channel["last_tweeted_milestone"] = current_milestone

                except requests.exceptions.RequestException as e:
                    print(f"Error downloading image for {channel['name']}: {str(e)}")
                except tweepy.TweepyException as e:
                    print(f"Error tweeting for {channel['name']}: {str(e)}")
                    if e.api_code:
                        print(f"API Code: {e.api_code}")
                    if e.response:
                        print(f"Response content: {e.response.text}")

            # Always update the subscriber count to the latest one
            channel["subscribers"] = current_count

    # Write the updated channel data back to the JSON file
    with open('channel_data.json', 'w') as f:
        json.dump(channels, f, indent=4)

    if not tweets_sent:
        print("No new milestones reached. Channel data updated.")

if __name__ == "__main__":
    check_and_tweet()
