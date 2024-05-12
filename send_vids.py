from telegram.constants import ParseMode
from get_token import get_token
from telegram import Bot
import logging
import os

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def send_videos(bot: Bot, video_path: str) -> None:
    """
    Sends all videos ending with "_merged.mp4" in the specified path to the chat.
    """
    try:
        chat_id = 853162659
        for filename in os.listdir(video_path):
            if filename.endswith("_merged.mp4"):
                video_file = os.path.join(video_path, filename)
                await bot.send_video(chat_id=chat_id, video=video_file, caption=filename)
    except Exception as e:
        logger.warning(f"An error occurred while sending the videos: {e}")

async def sv_main(path) -> None:
    """Run the bot."""

    bot_token = get_token()
    bot = Bot(bot_token)
    await send_videos(bot, path)