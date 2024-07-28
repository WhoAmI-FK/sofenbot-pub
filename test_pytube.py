from pytube import YouTube
import logging
import traceback

# Configure logging to show info logs in the console
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_pytube(url):
    try:
        logging.info(f"Starting download for URL: {url}")

        ob = YouTube(url)
        logging.info("YouTube object created successfully")

        # Check if there are any streams available
        if not ob.streams:
            logging.error("No streams found for the given URL")
            return
        
        # Get the stream by itag
        strm = ob.streams.get_by_itag(22)
        if not strm:
            logging.error("Stream with itag 22 not found")
            return
        
        # Get all streams
        streams = ob.streams
        links = get_streams_links(streams)
        
        logging.info(f"Streams links: {links}")
        
        strm_direct_dlink = strm.url
        direct_link = strm.url
        
        logging.info("Stream URLs retrieved successfully")
        
        x = ob.description.split("|")
        
        logging.info("Test completed successfully")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())

def get_streams_links(streams):
    links = []
    for stream in streams:
        if stream.includes_audio_track:
            link = stream.url
            resolution = stream.resolution
            extension = stream.subtype
            links.append({'url': link, 'resolution': resolution, 'extension': extension})
    return links

# Replace with the actual YouTube URL you want to test
test_pytube("https://www.youtube.com/watch?v=vVwm0hZr9Iw")