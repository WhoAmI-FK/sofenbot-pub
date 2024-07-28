import re
import telegram
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton,InlineKeyboardMarkup, Video
from telegram.ext import ApplicationBuilder,Updater, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
import pyshorteners
from languages import *
import googleapiclient.discovery
from testDown import downloadinstagrampost

import logging


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

production_token = '' # YOUR TOKEN HERE
s = pyshorteners.Shortener()
video_link = ""
selected_lang = "EN"

# need to remake from API -> oauth

CLIENT_SECRET_FILE = 'client_secret.json' # YOU NEED TO ADD YOUR OWN CLIENT SECRET FILE
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']

# just using API (is limited way of working with utube api)
API_KEY = '' # YOUR API KEY HERE

async def startDownload(url, update, context):
    global file_size
    try:
        URL = url
        logging.info(f"Starting download for URL: {URL}")
        
        if not URL:
            logging.error("Invalid URL provided")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid URL provided.")
            return

        ob = YouTube(URL)
        logging.info("YouTube object created successfully")
        
        # Check if there are any streams available
        if not ob.streams:
            logging.error("No streams found for the given URL")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No streams available for the given URL.")
            return
        
        # Get the stream by itag
        strm = ob.streams.get_by_itag(22)
        if not strm:
            logging.error("Stream with itag 22 not found")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Stream with the specified itag not found.")
            return
        
        # Get all streams
        streams = ob.streams
        links = get_streams_links(streams)
        buttons = create_inline_keyboard(links)
        
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Choose video type and resolution: ",
                                 reply_markup=buttons)
        
        strm_direct_dlink = strm.url
        direct_link = strm.url
        
        logging.info("Stream URLs retrieved successfully")
        
        x = ob.description.split("|")
        
        # Uncomment these lines if needed
        file_size = strm.filesize
        strm.download()
        return strm_direct_dlink
        
    except VideoUnavailable:
        logging.error(f"VideoUnavailable error for URL: {url}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The video is unavailable.")
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while processing the video.")
        print(e)
        print('Error!!')

def create_inline_keyboard_s(videos, req, title):
    buttons = []
    row = []
    for video in videos:
        button_text = f"{video[1]}" # title
        # add here link to direct link transformation
        url = video[0] #link url
        callback_data = url
        button = InlineKeyboardButton(button_text, callback_data)
        row.append(button)
        if(len(row) == 2):
            buttons.append(row.copy())
            row.clear()
    if row:
        buttons.append(row.copy())
#    tempButton = InlineKeyboardButton(">", callback_data="Button")
#    buttons.append([tempButton])
    llist = []
    if req.get('prevPageToken') is not None:
        llist.append(InlineKeyboardButton("←", callback_data=f"token:{req['prevPageToken']};title:{title}"))
   # page_button = InlineKeyboardButton("1/4", callback_data="Button")
    if req.get('nextPageToken') is not None:
        llist.append(InlineKeyboardButton("→", callback_data=f"token:{req['nextPageToken']};title:{title}"))
    #buttons.append([left_button, page_button, right_button])
    buttons.append(llist)
    return InlineKeyboardMarkup(buttons)

async def start(update, context):
#     message = """Hello! I'm your Sofen chat bot, I can help you to to download youtube videos\n use the command /download
# then send me the youtube link \n I will reply back with a direct download link ! \n Have a good time."""
#     context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    # Create a list of InlineKeyboardButtons
    buttons = [
        InlineKeyboardButton("AR", callback_data="AR"),
        InlineKeyboardButton("EN", callback_data="EN")
    ]
    # Create an InlineKeyboardMarkup object and pass in the list of buttons
    keyboard = InlineKeyboardMarkup([buttons])

    # Send the keyboard to the user
    await context.bot.send_message(chat_id=update.effective_chat.id,
                             text="What is your preferred language?",
                             reply_markup=keyboard)


async def handle_callback_query(update, context):
    query = update.callback_query
    selected_lang = query.data
    if("token" in query.data):
        data = query.data.split(';')
        token = data[0].split(':')[1]
        title = data[1].split(':')[1]

        #req = getVideoInfoFromYouTube(title=title, maxRes=10)
        #video_link_array = [[f"https://www.youtube.com/watch?v={video['id']['videoId']}", video["snippet"]["title"] ]\
        #        for video in req['items']]
        #buttons = create_inline_keyboard_s(video_link_array, req=req)
        req = getPageFromYouTube(title,10,token)
        video_link_array = [[f"https://www.youtube.com/watch?v={video['id']['videoId']}", video["snippet"]["title"] ]\
                for video in req['items']]
        buttons = create_inline_keyboard_s(video_link_array, req=req, title=title)
        must_delete = query.message
        await context.bot.deleteMessage (message_id = must_delete.message_id,
                           chat_id = query.message.chat_id)
        await context.bot.send_message(chat_id=query.message.chat_id, text="Choose video", reply_markup=buttons)
    elif "regionCode" in query.data:
        regionCode = query.data.split(":")[1]
        req = getTrendingVByRegion(regionCode)
        video_link_array = [[f"https://www.youtube.com/watch?v={video['id']}", video["snippet"]["title"] ]\
                for video in req['items']]
        #print(req)
        must_delete = query.message
        await context.bot.deleteMessage (message_id = must_delete.message_id,
                           chat_id = query.message.chat_id)
        output = ""
        counter = 1
        for item in video_link_array:
           # to get views, need to work on it because it takes too long to retrieve data
           # yt = YouTube(item[0])
           # views = "?"
           # if yt.views != None:
           #     views = str(yt.views)
           # output += "----------\n" + str(counter) + ". "  + item[1] + " - " + item[0] + "\nViews: " + str(views) + "\n"
            output += "----------\n" + str(counter) + ". "  + item[1] + " - " + item[0] + "\n"
            counter+=1
        
        await context.bot.send_message(chat_id=query.message.chat_id, text=output)
    else:
        context.user_data['preferred_lang'] = selected_lang
        message = 'Your preferred language is '
        if selected_lang == 'AR':
            await context.bot.send_message(chat_id=query.message.chat_id,
                                 text=f"{translations[message]} {translations[selected_lang]}")
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"{message} {selected_lang}")
        await send_message(update, context)


async def send_message(update, context):
    # Get the user's preferred language from the context user_data
    preferred_lang = context.user_data.get('preferred_lang')
    welcome_message = "Welcome to Sofen bot"
    # Send a message in the user's preferred language
    if preferred_lang == "AR":
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=translations[welcome_message])
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=welcome_message)
    instruction_message = "Use the command /download then send me the youtube/ instagram link \n I will reply back with the video or direct download link! \n Have a good time."
    # Send a message with the download instructions in the user's preferred language
    if preferred_lang == "AR":
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=translations[instruction_message])
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=instruction_message)


async def help(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""Here are the available commands:\n/start - Start the bot\n /download - get direct link to download
/help - Show available commands
    """)


async def download(update, context):
    context.user_data['download_waiting'] = True
    # Get the user's preferred language from the context user_data
    preferred_lang = context.user_data.get('preferred_lang')

    # Send a message with the download instructions in the user's preferred language
    if preferred_lang == "AR":
       await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="أرسل رابط فيديو من  YouTube او instagram  للحصول على رابط التحميل المباشر.")

    elif preferred_lang == "EN":
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Send a YouTube / instagram video link to get direct download link.")
    # context.bot.send_message(chat_id=update.effective_chat.id, text="Send me a YouTube video link to download.")

async def trending(update, context):
    preferred_lang = context.user_data.get('preferred_lang')

    if preferred_lang == "AR":
        pass
    elif preferred_lang == "EN":
        buttons = create_trending_buttons()
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Pick the country.", reply_markup=buttons)

async def search(update, context):
    context.user_data['search_waiting'] = True
    preferred_lang = context.user_data.get('preferred_lang')

    if preferred_lang == "AR":
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="ابحث عن أخر ما نشر في يوتيوب بخصوص عنوان معين.")
    elif preferred_lang == "EN":
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Send a title to search.")

async def echo(update, context):
    video_link = update.message.text
    if context.user_data.get('download_waiting'):
        youtube_regex = r"(?P<url>https?://(?:www\.)?youtu(?:be\.com|\.be)(?:\S+))"
        match = re.search(youtube_regex, video_link)
        if match:
            message = await startDownload(video_link, update, context)
            # preview_url = f"https://api.telegram.org/bot{context.bot.token}/sendPhoto?chat_id={update.message.chat_id}&parse_mode=HTML&photo={ob.thumbnail_url}&title={ob.title}&caption={ob.description}"
            if message is None:
                logging.error("Received None message")
        # You can handle the None case here as you wish
                return
            try:
                short_url = s.tinyurl.short(message)
        # Continue with the rest of your function using short_url
            except Exception as e:
                logging.error(f"Error shortening URL: {e}")
        # Handle the exception as needed            await context.bot.send_message(chat_id=update.effective_chat.id, text=short_url)
            del context.user_data['download_waiting']
        else:
            Insta_regex = r"(?:(?:http|https):\/\/)?(?:www.)?(?:instagram.com|instagr.am|instagr.com)\/(\w+)"
            match = re.search(Insta_regex, video_link)
            if match:
                video = downloadinst(video_link, update, context)
                await context.bot.send_video(chat_id=update.effective_chat.id, video=video)

                del context.user_data['download_waiting']
    if context.user_data.get('search_waiting'):
        title = update.message.text
        req = getVideoInfoFromYouTube(title=title, maxRes=10)
        video_link_array = [[f"https://www.youtube.com/watch?v={video['id']['videoId']}", video["snippet"]["title"] ]\
                for video in req['items']]
        buttons = create_inline_keyboard_s(video_link_array, req=req, title=title)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose video:", reply_markup=buttons)
        del context.user_data['search_waiting']


def getVideoInfoFromYouTube(title, maxRes):
    request = service.search().list(
            part='id,snippet',
            type='video',
            q=title,
            order='viewCount',
            maxResults=maxRes
        )
    response = request.execute()
    #print(response)
    return (response)

def getPageFromYouTube(title, maxRes, PageToken):
    request = service.search().list(
        part='id,snippet',
        type='video',
        pageToken=PageToken,
        q=title,
        order='viewCount',
        maxResults=maxRes
    )
    response = request.execute()
    return (response)

# for now lets set to 20
def getTrendingVByRegion(region):
    request = service.videos().list(
        part='id,snippet',
        chart='mostPopular',
        maxResults=20,
        regionCode=region
    )
    response = request.execute()
    return (response)

def downloadinst(url, update, context):
    video_data = downloadinstagrampost(url)
    # video = Video(video_data)
    return video_data
    # context.bot.send_message(chat_id=update.effective_chat.id, video=video)


service = googleapiclient.discovery.build(API_NAME, API_VERSION, developerKey=API_KEY)

application = ApplicationBuilder().token(production_token).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help))
application.add_handler(CommandHandler('download', download))   
application.add_handler(CommandHandler('search', search))
application.add_handler(CommandHandler('trending', trending))
application.add_handler(CallbackQueryHandler(handle_callback_query))
application.run_polling()

direct_link = ""

def get_streams_links(streams):
    links = []
    for stream in streams:
        if stream.includes_audio_track == True:
            link = stream.url
            resolution = stream.resolution
            extension = stream.subtype
            links.append({'url': link, 'resolution': resolution, 'extension': extension})
    return links


def create_inline_keyboard(links):
    buttons = []
    row = []
    for link in links:
        resolution = link.get('resolution', 'Unknown resolution')
        file_extension = link.get('extension', 'Unknown extension')
        button_text = f"{resolution} ({file_extension})"
        short_url = s.tinyurl.short(str(link['url']))
        callback_data = short_url
        button = InlineKeyboardButton(button_text, callback_data)
        row.append(button)
        if len(row) == 3:
            buttons.append(row.copy())  # Create a copy of the row list before appending
            row.clear()  # Clear the row list for the next set of buttons
    if row:  # Append the last row if it's not empty
        buttons.append(row.copy())
    return InlineKeyboardMarkup(buttons)

def create_trending_buttons():
    # need to move it to another file regionCodes.py i.e.
    regionCode = [
        ["PL", r"🇵🇱"],
        ["US", r"🇺🇸"],
        ["RU", r"🇷🇺"],
        ["CZ", r"🇨🇿"],
        ["DE", r"🇩🇪"],
        ["EG", r"🇪🇬"]
    ]
    buttons = []

    for country in regionCode:
        print(country)
        buttons.append(InlineKeyboardButton(country[0] + " " + country[1], callback_data="regionCode:" + country[0])) # add callback_data
    return InlineKeyboardMarkup([buttons])
