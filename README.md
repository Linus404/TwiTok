# Twitch Top Clips Downloader

This Python script allows you to download the most viewed Twitch clips from a specific game within a specified time frame. It offers several parameters for customization, including the game, time window (e.g., 24 hours, 7 days), number of clips to download, and an optional filter to download videos with specific language titles. Subtitles are generated automatically (currently only available for english videos - a language recognition is needed)

## TODO
- Update the skiping function when video already exists (and print comment)
- overall optimization
- add creator name and view count
- remove buttons from final telegram message

## Prerequisites

- latest Python
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

This will host the telegram bot until the script is terminated. 
The bot will send multiple questions which are answered with buttons.
After the last answer the bot downloads and edits the videos. 
When it's done it will send all videos.

## Output

The log willbe displayed in the terminal.

## Disclaimer

Please note that using this script may violate Twitch's terms of service. It is not intended to being used. It is only for educational and training purposes.

veed.io sometimes get stuck at uploading the video and exporting. I have yet not found out why and how to fix. After some tries it just works again.

## License

Copyright 2024 github.com/Linus404

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.