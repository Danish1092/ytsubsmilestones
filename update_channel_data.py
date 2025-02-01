import json
import requests
from supabase import create_client, Client
import os

def get_subscriber_count(channel_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return int(data["items"][0]["statistics"]["subscriberCount"])
    return None

# Initialize Supabase client
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_KEY']
supabase: Client = create_client(url, key)

# Fetch channels from Supabase
channels = supabase.table('channels').select('*').execute().data

API_KEY = os.environ['YOUTUBE_API_KEY']

for channel in channels:
    if 'subscribers' not in channel or channel['subscribers'] is None:
        subscriber_count = get_subscriber_count(channel['id'], API_KEY)
        
        if subscriber_count is not None:
            channel['subscribers'] = subscriber_count
            channel['last_tweeted_milestone'] = subscriber_count
            print(f"Updated {channel['name']} with {subscriber_count} subscribers.")
            # Update channel data in Supabase
            supabase.table('channels').update({
                'subscribers': subscriber_count,
                'last_tweeted_milestone': subscriber_count
            }).eq('id', channel['id']).execute()
        else:
            print(f"Failed to fetch data for {channel['name']}")

print("Channel data updated successfully.")
