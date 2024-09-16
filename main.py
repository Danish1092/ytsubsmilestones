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
API_HOST = "youtube138.p.rapidapi.com"

def fetch_channel_details(channel_id):
    url = f"https://youtube138.p.rapidapi.com/channel/details/?id={channel_id}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extracting the subscriber count
        subscriber_count = data["stats"]["subscribers"]

        # Handling if subscriber count is an integer or string
        if isinstance(subscriber_count, str):
            subscriber_count = int(subscriber_count.replace('M', '000000').replace('K', '000').replace(',', ''))
        else:
            subscriber_count = int(subscriber_count)

        # Extracting profile picture URL
        profile_picture_url = data["avatar"][0]["url"] if data.get("avatar") else None
        return subscriber_count, profile_picture_url

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
        if current_count is not None and channel["subscribers"] is not None:
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

            # Always update the subscriber count
            channel["subscribers"] = current_count

    # Write the updated channel data back to the JSON file
    with open('channel_data.json', 'w') as f:
        json.dump(channels, f, indent=4)

    if not tweets_sent:
        print("No new milestones reached. Channel data updated.")

if __name__ == "__main__":
    check_and_tweet()
