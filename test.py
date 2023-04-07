import os
import requests
from tqdm import tqdm
from telegram import InputFile, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# your bot token
TOKEN = "your_bot_token_here"
# chat id of the user or group to send the files to
CHAT_ID = "your_chat_id_here"

# function to download the files
def download_files():
    with open('links.txt') as f:
        links = f.read().splitlines()

    for i, url in enumerate(links, start=1):
        file_name = f"{i}.mp4"
        if os.path.exists(file_name):
            print(f"{file_name} already exists, skipping...")
            continue
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

        with open(file_name, 'wb') as f:
            for data in response.iter_content(chunk_size=1024):
                progress_bar.update(len(data))
                f.write(data)

        progress_bar.close()
        upload_to_telegram(file_name)

# function to upload the files to Telegram
def upload_to_telegram(file_name):
    # create an instance of the Updater class
    updater = Updater(TOKEN)
    # get the chat to send the files to
    chat = updater.bot.get_chat(CHAT_ID)
    # create an InputFile instance from the file
    input_file = InputFile(file_name)
    # send the file to the chat
    chat.send_document(input_file)
    # remove the file from local directory
    os.remove(file_name)

# handler function for the /download command
def download_command_handler(update: Update, context: CallbackContext) -> None:
    download_files()
    update.message.reply_text("Files downloaded and uploaded to Telegram!")

# create an instance of the Updater class
updater = Updater(TOKEN)
# add a handler for the /download command
updater.dispatcher.add_handler(CommandHandler("download", download_command_handler))

# start the bot
updater.start_polling()
