# Twitch Top Clips Downloader

This Python script allows you to download the most viewed Twitch clips from a specific game within a specified time frame. It offers several parameters for customisation, including the game, the time window (e.g. 24 hours, 7 days) and the number of clips to download. Subtitles are automatically generated if selected. To save space, all video folders older than 3 days are automatically deleted.  

## Compatibility

This project has been tested on Windows 10, and its behavior on other platforms may vary. Contributions to improve compatibility on other platforms are welcome.


## TODO

- Update skip function when video already exists (and print comment)
- general optimisation (like removing/fixing all the warnings)
- add creator name and number of views in the clip
- remove buttons from final message
- add cloud deployment (see issue #2)
- add option to download top clips from a streamer

## Requirements

- Latest Python
- Enabling a VPN is recommended to avoid possible IP bans.
- A Telegram Bot
- Twitch API access

## Setup

1. Clone this repository to your local machine.
2. Navigate to the directory you cloned the repository to.
3. Install the required dependencies using `pip install -r requirements.txt`.
4. Open get_token.py and replace all the placeholders with your own tokens and IDs.

## Usage

Execute the script with the following command

```bash
python main.py 
```

This will host the telegram bot until the script is terminated.  
Send "/send" via telegram. The command is handled in main.py and doesn't need to be registered in Telegram.  
Choose your settings by clicking on the buttons.  
After choosing subtitles, the bot will take a while to download the videos and add subtitles if they are selected.  
When it's done, it will send all videos via Telegram.  
Once all the videos have been sent, you can start again or close the terminal to stop hosting.  

https://github.com/Linus404/TwiTok/assets/138003283/d46d8415-0af1-4740-b107-bdb1bc2367ab

For real-world use cases, you can check out the YouTube channels:  

@BlizzardGuides, who curates a collection of videos and uploads them in a single compilation, averaging between 200k and 300k views per video.


## Output

The log is displayed in the terminal.
The videos and settings will be sent via Telegram.

## Disclaimer

Please note that using this script may violate Twitch's or veed.io's terms of service. It is not intended to be used. It is for educational and training purposes only.

veed.io sometimes hangs while uploading and exporting the video. I have not yet found out why and how to fix it. After a few tries it works again.

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
