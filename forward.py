from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# Constants
API_ID = 11573285
API_HASH = "f2cc3fdc32197c8fbaae9d0bf69d2033"
BOT_TOKEN = "5311900774:AAGjyqQ6JfjP5y2W-PD95txGoJ_e2Dsjugo"
STRING = "BQDMM2QACU_GXZJI0OW3QxgyK5KqNORx5gZlWYLc4a4XTnfy5i1TEJiaNlkFPi4OBz4P1qkW34NN71pPzg-MOIW5Cy7IwA-N9NY_GUmNv2G-7QCsIpVSQdKTxOJPbWeRZvXx9jocCxbZL8gUs4ULU9q5gh6AH8RW2afrXm2tgJ_He0xVLiLBJEaBxaFrMy_XTCYAA2K7qZIS-UCeg-J0PAYmaA72CZaKE6Dj5GxheDeE93BGpWr6jWvYHxzBvSFLwzs2KIi6-xxa3B6UeUYYfwSzKECvwtYs9i8GmUi6sz45XUNar_UD0OzWthmg2vwVKI2RmPKSCgI8WJBIGDFJD9dQRP79QAAAAAE3eMH7AA"
AUTOFORWARD_COMMAND = "/autoforward"
WATERMARK_TEXT = "@predictionthalateam11\n\n\n" * 30
WATERMARK_OPACITY_PERCENTAGE = 10  # Set your desired percentage here

# Configuration
source_channel_id = -1001449829482
target_channel_id = -1002013404164
target_channel_id1 = -1002002451120
whitelist_words = [""]
blacklist_words = ["atw786_bot"]
auto_forwarding = True

# Store id for update
store_id = {}

# Initialize the Pyrogram client
app = Client(
    name="ATW786",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    session_string=STRING
)


# Helper function to add watermark to an image
def add_watermark_to_image(image_path):
    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("D:\\AUTO PROVIDER\Regular.otf", 12)

    positions = [(0, 10), (180, 10), (360, 10), (540, 10)]
    # Convert opacity from percentage to the range [0, 255]
    opacity = int((WATERMARK_OPACITY_PERCENTAGE / 100) * 255)

    color = (255, 255, 0, opacity)

    for position in positions:
        draw.text(position, WATERMARK_TEXT, font=font, fill=color)

    photo = BytesIO()
    img.save(photo, format='PNG')
    photo.seek(0)
    return photo


# Command to start/stop auto-forwarding
@app.on_message(filters.command(["start"], ".") & filters.me)
async def start_command(_, message: Message):
    await message.edit_text("Hello, I am online.")


@app.on_message(filters.command(["autoforward"], ".") & filters.me)
async def autoforward_command(client: Client, message: Message):
    global auto_forwarding
    ex = await message.edit_text("Processing...")
    command = message.text.split()[1]
    if command == 'start':
        if not auto_forwarding:
            auto_forwarding = True
            await ex.edit('Auto-forwarding started.')
        else:
            await ex.edit('Auto-forwarding is already started.')
    elif command == 'stop':
        if auto_forwarding:
            auto_forwarding = False
            await ex.edit('Auto-forwarding stopped.')
        else:
            await ex.edit('Auto-forwarding is already stopped.')


# Function to forward text messages
@app.on_message(filters.chat(source_channel_id) & filters.text)
async def forward_text_message(client: Client, message: Message):
    global auto_forwarding
    text = message.text.lower()
    if any(word in text for word in blacklist_words) or not any(word in text for word in whitelist_words) or not auto_forwarding:
        return

    try:
        forwarded_message = await client.send_message(
            target_channel_id, message.text, disable_web_page_preview=True)
        store_id[message.id] = forwarded_message.id
    except Exception as e:
        print(f"Failed to forward text message: {e}")


# Function to forward photo messages
@app.on_message(filters.chat(source_channel_id) & filters.photo)
async def forward_photo_message(client: Client, message: Message):
    global auto_forwarding
    if not auto_forwarding:
        return

    file_id = await client.download_media(message)
    try:
        photo_with_watermark = add_watermark_to_image(file_id)
        forwarded_message = await client.send_photo(
            target_channel_id, photo_with_watermark,
            caption=message.caption
        )
        forwarded_message = await client.send_photo(
            target_channel_id1, file_id,
            caption=message.caption
        )

        store_id[message.id] = forwarded_message.id
    except Exception as e:
        print(f"Failed to forward photo message: {e}")
    finally:
        os.remove(file_id)


# Function to handle edited text messages
@app.on_edited_message(filters.chat(source_channel_id) & filters.text)
async def update_text_message(client: Client, message: Message):
    text = message.text.lower()
    if any(word in text for word in blacklist_words) or not any(word in text for word in whitelist_words) or not auto_forwarding:
        return

    message_id = store_id.get(message.id)
    try:
        await client.edit_message_text(
            target_channel_id, message_id, message.text, disable_web_page_preview=True)
    except Exception as e:
        print(f"Failed to update text message: {e}")


# Function to handle edited photo messages
# Function to handle forced edit of photo messages
@app.on_edited_message(filters.chat(source_channel_id) & filters.photo)
async def force_edit_photo_message(client: Client, message: Message):
    try:
        # Replace "message_id" with the actual message ID you want to force edit
        forwarded_message_id = store_id.get(message.id)
        if forwarded_message_id:
            # Use the 'message' object directly
            file_id = await client.download_media(message)
            photo_with_watermark = add_watermark_to_image(file_id)

            # Get the existing caption and reply markup
            existing_caption = (await client.get_messages(target_channel_id, forwarded_message_id)).caption

            try:
                # Force edit by updating with the same content
                await client.edit_message_media(
                    chat_id=target_channel_id,
                    message_id=forwarded_message_id,
                    media=InputMediaPhoto(photo_with_watermark)
                )
                print("Force edit successful.")
                os.remove(file_id)
            except Exception as edit_error:
                if "MESSAGE_NOT_MODIFIED" in str(edit_error):
                    print(
                        "Ignoring [400 MESSAGE_NOT_MODIFIED] error and continuing.")
                else:
                    print(f"Failed to force edit photo message: {edit_error}")

            # Update caption separately using edit_message_caption
            await client.edit_message_caption(
                chat_id=target_channel_id,
                message_id=forwarded_message_id,
                caption=existing_caption  # Use the existing caption
            )

            os.remove(file_id)
    except Exception as e:
        print("All Working ")


# Start the Pyrogram client
print("Bot is online and running.")
app.run()
