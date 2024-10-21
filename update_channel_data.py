import json
import requests

def get_subscriber_count(channel_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return int(data["items"][0]["statistics"]["subscriberCount"])
    return None

with open('channel_data.json', 'r') as file:
    channels = json.load(file)

API_KEY = os.environ['YOUTUBE_API_KEY']  

for channel in channels:
    if 'subscribers' not in channel or channel['subscribers'] is None:
        subscriber_count = get_subscriber_count(channel['id'], API_KEY)
        
        if subscriber_count is not None:
            channel['subscribers'] = subscriber_count
            channel['last_tweeted_milestone'] = subscriber_count
            print(f"Updated {channel['name']} with {subscriber_count} subscribers.")
        else:
            print(f"Failed to fetch data for {channel['name']}")

with open('channel_data.json', 'w') as file:
    json.dump(channels, file, indent=4)

print("Channel data updated successfully.")
