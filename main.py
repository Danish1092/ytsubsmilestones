import tweepy
import requests
import json

# Use your actual API credentials for Twitter
api_key = "eNmC7WvB9jroA2t8z7O1nYEJA"
api_secret = "RpL0Y6qtJmji9MlFRKxLUUuKsesjsHevSFOPYQAK5ZZ4DHMpFH"
access_token = "1802930626775093248-79sbETqyPswk4akrh7DIXSYiqH63px"
access_token_secret = "5f12eIWVCeavDgde90tsc6jvQuVrThfXtyrt2ZVS0lanQ"

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

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

        # Extract the subscriber count and profile picture URL
        subscriber_count = data.get("subscriberCount")
        profile_pic_url = data.get("avatar")

        return subscriber_count, profile_pic_url

    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for channel {channel_id}: {e}")
        return None, None

def check_and_tweet():
    # Load channel data from JSON file
    with open('channel_data.json', 'r') as f:
        channels = json.load(f)

    for channel in channels:
        current_count, profile_pic_url = fetch_channel_details(channel["id"])
        if current_count and channel["subscribers"] is not None:
            if current_count >= (channel["subscribers"] + 1000000):  # Check next million milestone
                milestone = (current_count // 1000000) * 1000000
                tweet_text = f"{channel['name']} has crossed {milestone // 1000000} Million subscribers on YouTube!"

                # Upload profile picture and tweet with media
                if profile_pic_url:
                    try:
                        response = requests.get(profile_pic_url)
                        with open("profile_pic.jpg", "wb") as f:
                            f.write(response.content)
                        media = api.media_upload(filename="profile_pic.jpg")
                        api.update_status(status=tweet_text, media_ids=[media.media_id])
                        print(f"Tweeted: {tweet_text}")
                    except Exception as e:
                        print(f"Error uploading profile picture for {channel['name']}: {e}")
                        api.update_status(status=tweet_text)
                else:
                    api.update_status(status=tweet_text)

                # Update the subscriber count in the channel data
                channel["subscribers"] = current_count

    # Save the updated channel data back to the JSON file
    with open('channel_data.json', 'w') as f:
        json.dump(channels, f, indent=4)

if __name__ == "__main__":
    check_and_tweet()
