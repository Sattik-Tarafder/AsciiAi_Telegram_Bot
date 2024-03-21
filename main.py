from typing import Final
import os
import imgkit
from nudenet import NudeClassifier
from ascii_magic import AsciiArt
from telegram import Update
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext


TOKEN: Final = "7005939046:AAGkgfq6pg-IK9zGROBlvghVVR6qx6BGdAc"
BOT_USERNAME: Final = "@asciiai_bot"

#NSFW detector function
def nsfw(img):
    classifier = NudeClassifier()
    classification = classifier.classify(f'images/{img}')

    safe_prob = classification[f'images/{img}']['safe']
    unsafe_prob = classification[f'images/{img}']['unsafe']

    if safe_prob >= unsafe_prob:
        return 0
    else:
        return
 

#Image processing function 
def image_processing(id, image):
    Nsfw = nsfw(image)

    if Nsfw == 0:
        #Converting the img to ascii html file and deleting the img
        file_id_html = str(id) + ".html"
        html_file = AsciiArt.from_image(f"images/{image}")
        html_file.to_html_file(f"html_files/{file_id_html}")
        os.remove(f"images/{image}")


        #Converting the html file to img and deleting the html file
        file_id_ascii = str(id) + "ascii" + ".jpg"
        conf = imgkit.config(wkhtmltoimage="wkhtmltoimage/wkhtmltoimage.exe")
        imgkit.from_file(f'html_files/{file_id_html}', f'ascii/{file_id_ascii}', config=conf)
        os.remove(f'html_files/{file_id_html}')

        return file_id_ascii
        
    else:
        return 1

#Start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Send me a photo to convert it to ASCII Art')

#Main function to download, process and send the ascii art
async def ascii_image(update: Update, context: CallbackContext):
    #Checking if the msg is from group chat or not
    message_type: str = update.message.chat.type
    caption = update.message.caption

    #This if method is used to avoid TypeError: argument of type 'NoneType' is not iterable;
    #when checking for Bot username in caption
    if caption == None:
        caption = "Bot"

    if message_type == "group":
        if BOT_USERNAME in caption:

            #Downloading the image to the local dir
            image_file = await update.message.photo[-1].get_file()
            user_id = update.message.photo[-1].file_unique_id
            file_id_image = str(user_id) + ".jpg"
            await update.message.reply_text('Processing...')
            await image_file.download_to_drive(f"images/{file_id_image}")

            processed = image_processing(user_id, file_id_image)

            if processed == 1:
                reply = "Your image contains NSFW contents. ASCII AI does not support NSFW contents"
                await update.message.reply_text(reply)
                os.remove(f"images/{file_id_image}")

            else:
                photo = telegram.InputMediaPhoto(media=open(f"ascii/{processed}", "rb"), caption="Here is your Ascii Art")
                await update.message.reply_media_group([photo])
                os.remove(f'ascii/{processed}')

        else:
            return

    else:
        image_file = await update.message.photo[-1].get_file()
        user_id = update.message.photo[-1].file_unique_id
        file_id_image = str(user_id) + ".jpg"
        await update.message.reply_text('Processing...')
        await image_file.download_to_drive(f"images/{file_id_image}")

        processed = image_processing(user_id, file_id_image)

        if processed == 1:
            reply = "Your image contains NSFW contents. ASCII AI does not support NSFW contents"
            await update.message.reply_text(reply)
            os.remove(f"images/{file_id_image}")

        else:
            photo = telegram.InputMediaPhoto(media=open(f"ascii/{processed}", "rb"), caption="Here is your Ascii Art")
            await update.message.reply_media_group([photo])
            os.remove(f'ascii/{processed}')


if __name__ == '__main__':

    print('Starting...')
    app = Application.builder().token(TOKEN).build()

    #Commands
    app.add_handler(CommandHandler('start', start_command))

    #Messages
    app.add_handler(MessageHandler(filters.PHOTO, ascii_image))

    print('Polling...')
    app.run_polling()