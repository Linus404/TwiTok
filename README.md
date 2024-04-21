# Twitch Top Clips Downloader

This Python script allows you to download the most viewed Twitch clips from a specific game within a specified time frame. It offers several parameters for customization, including the game, time window (e.g., 24 hours, 7 days), number of clips to download, and an optional filter to download videos with specific language titles.

## Prerequisites

- Python 3.8+
- Activation of a VPN is recommended to avoid potential IP bans.

## Setup

1. Clone this repository to your local machine.
2. Navigate to the directory where you cloned the repository.
3. Install the required dependencies using `pip install -r requirements.txt`.

## Usage

Run the script with the following command:

```bash
python main.py 
```

Gamename, timewindow, number of clips and a language filter are hardcoded in lines 9-14 in main.py

This default command will download the top 6 most viewed Twitch clips for the game "League of Legends" from the past 24 hours

## Output

The script will create a folder in the directory where it is located, named with the current date and time frame (e.g., `Videos/2024-04-21_24hr`). It will automatically delete folders that are three days old to manage disk space efficiently.

## Disclaimer

Please note that using this script may violate Twitch's terms of service. Use it responsibly and at your own risk.

## License

TODO
