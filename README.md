# YouTube Milestone Bot

YouTube Milestone Bot is an automated tool that tracks subscriber milestones for specified YouTube channels and tweets about their achievements.

## Features

- Monitors subscriber counts for multiple YouTube channels
- Detects when a channel reaches a new million-subscriber milestone
- Automatically tweets to celebrate the achievement
- Updates a Supabase database with the latest subscriber counts
- Runs automatically every 4 hours using GitHub Actions

## Technologies Used

- Python
- YouTube Data API
- Twitter API v2
- Supabase
- GitHub Actions

## Project Structure

- `main.py`: The main script that fetches YouTube subscriber counts, checks for milestones, and posts tweets.
- `update_channel_data.py`: A utility script to update the Supabase database with initial subscriber counts and last tweeted milestones. This script is used only for adding new channels to the Supabase database for tracking.
- `.github/workflows/schedule.yml`: The GitHub Actions workflow file that automates the bot's execution. It runs the `main.py` every 4 hours.

## File Descriptions

### main.py
This is the core script of the bot. It performs the following tasks:
- Fetches the latest subscriber counts for each channel from the Supabase database
- Checks if any channel has reached a new million-subscriber milestone
- Posts a tweet for each new milestone reached
- Updates the Supabase database with the latest subscriber counts and milestones

### update_channel_data.py
This utility script is used to initialize or update the Supabase database, especially when adding new channels to track. It:
- Fetches the existing channels from the Supabase database
- For each channel, especially newly added ones:
  - Fetches the current subscriber count from the YouTube API
  - Initializes or updates the 'subscribers' field with the current count
  - Sets the 'last_tweeted_milestone' to the current subscriber count (rounded down to the nearest million)
- Saves the updated data back to the Supabase database

This script is particularly useful when you've added new channels to the Supabase database and need to populate their current subscriber counts before running the main bot. It ensures that `main.py` has accurate starting data for comparison and milestone tracking.

### .github/workflows/schedule.yml
This YAML file defines the GitHub Actions workflow that automates the bot's execution. It:
- Runs the bot every 4 hours
- Sets up the Python environment
- Installs necessary dependencies
- Runs the main.py script

## Setting Up Supabase

1. **Sign Up and Create a New Project:**
   - Go to [Supabase](https://supabase.io/) and sign up for an account.
   - Create a new project and note down the project URL and anon key.

2. **Create a Table:**
   - Go to the "Table Editor" tab in the Supabase dashboard.
   - Create a new table named `channels` with the following columns:
     - `id` (type: `text`, primary key)
     - `name` (type: `text`)
     - `subscribers` (type: `integer`)
     - `last_tweeted_milestone` (type: `integer`)

3. **Insert Initial Data:**
   - You can insert initial data into the table using the "Table Editor" or by uploading a CSV file.

4. **Set Environment Variables:**
   - In your GitHub repository, go to "Settings" > "Secrets and variables" > "Actions".
   - Add the following secrets:
     - `SUPABASE_URL` with the value of your Supabase project URL.
     - `SUPABASE_KEY` with the value of your Supabase anon key.
     - `SUPABASE_SERVICE_ROLE_KEY` with the value of your Supabase service role key.

## Bot Link: x.com/YTSubsTracker
