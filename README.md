# YouTube Milestone Bot

YouTube Milestone Bot is an automated tool that tracks subscriber milestones for specified YouTube channels and tweets about their achievements.

## Features

- Monitors subscriber counts for multiple YouTube channels
- Detects when a channel reaches a new million-subscriber milestone
- Automatically tweets to celebrate the achievement
- Updates a local JSON file with the latest subscriber counts
- Runs automatically every 4 hours using GitHub Actions

## Technologies Used

- Python
- YouTube Data API
- Twitter API v2
- GitHub Actions

## Project Structure

- `main.py`: The main script that fetches YouTube subscriber counts, checks for milestones, and posts tweets.
- `update_channel_data.py`: A utility script to update the `channel_data.json` file with initial subscriber counts and last tweeted milestones.
- `channel_data.json`: A JSON file containing the list of YouTube channels to monitor, along with their current subscriber counts and last tweeted milestones.
- `.github/workflows/youtube_milestone_bot.yml`: The GitHub Actions workflow file that automates the bot's execution.

## File Descriptions

### main.py
This is the core script of the bot. It performs the following tasks:
- Fetches the latest subscriber counts for each channel in `channel_data.json`
- Checks if any channel has reached a new million-subscriber milestone
- Posts a tweet for each new milestone reached
- Updates the `channel_data.json` file with the latest subscriber counts and milestones

### update_channel_data.py
This utility script is used to initialize or update the `channel_data.json` file, especially when adding new channels to track. It:
- Reads the existing `channel_data.json` file
- For each channel, especially newly added ones:
  - Fetches the current subscriber count from the YouTube API
  - Initializes or updates the 'subscribers' field with the current count
  - Sets the 'last_tweeted_milestone' to the current subscriber count (rounded down to the nearest million)
- Saves the updated data back to `channel_data.json`

This script is particularly useful when you've added new channels to `channel_data.json` and need to populate their current subscriber counts before running the main bot. It ensures that `main.py` has accurate starting data for comparison and milestone tracking.

### channel_data.json
This JSON file stores information about the YouTube channels being monitored. Each entry contains:
- `name`: The name of the YouTube channel
- `id`: The YouTube channel ID
- `subscribers`: The current subscriber count (populated by `update_channel_data.py`)
- `last_tweeted_milestone`: The last milestone (in millions) that was tweeted about (initialized by `update_channel_data.py`)

### .github/workflows/youtube_milestone_bot.yml
This YAML file defines the GitHub Actions workflow that automates the bot's execution. It:
- Runs the bot every 4 hours
- Sets up the Python environment
- Installs necessary dependencies
- Runs the main.py script
- Commits and pushes any changes to the channel_data.json file
