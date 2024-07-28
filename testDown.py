from datetime import datetime
# from tqdm import tqdm
import requests
import re
import instaloader


def downloadinstagrampost(url):
    # Create an instance of Instaloader class
    loader = instaloader.Instaloader(max_connection_attempts=20
                                     ,
                                     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")

    # Login (optional)
    # loader.interactive_login("<your-username>")

    if re.search("reel", url):

        # Extract the post ID from the URL
        post_id = re.findall("/reel/([^/]+)/?", url)[0]
    else:
        post_id = re.findall("/p/([^/]+)/?", url)[0]

    # Get the post object by its ID
    post = instaloader.Post.from_shortcode(loader.context, post_id)

    # Download the post
    if post.is_video:
        # Get the URL of the highest quality version of the video
        media_url = post.video_url
        return download_img_or_video(media_url, False)
        # Download the video
        # loader.download_video(media_url, target=f"{post_id}.mp4")
        # print(media_url)
    else:
        # Get the URL of the highest quality version of the image
        media_url = post.url
        return download_img_or_video(media_url, True)
        # Download the image
        # loader.download_pic(media_url, target=f"{post_id}.jpg")
        # print(media_url)


def download_img_or_video(finalUrl, img):
    file_size_request = requests.get(finalUrl, stream=True)
    file_size = int(file_size_request.headers['Content-Length'])
    block_size = 1024
    filename = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
    if img == True:
        # t = tqdm(total=file_size, unit='B', unit_scale=True, desc=filename, ascii=True)
        # with open(filename + '.jpg', 'wb') as f:
        #     for data in file_size_request.iter_content(block_size):
        #         t.update(len(data))
        #         f.write(data)
        # t.close()
        response = requests.get(finalUrl)
        img_data = response.content
        return img_data
    else:
        # file_size_request = requests.get(finalUrl, stream=True)
        # file_size = int(file_size_request.headers['Content-Length'])
        # block_size = 1024
        # filename = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
        # t = tqdm(total=file_size, unit='B', unit_scale=True, desc=filename, ascii=True)
        # with open(filename + '.mp4', 'wb') as f:
        #     for data in file_size_request.iter_content(block_size):
        #         t.update(len(data))
        #         f.write(data)
        # t.close()
        response = requests.get(finalUrl)
        video_data = response.content
        return video_data

# Example usage:
# download_instagram_post("https://www.instagram.com/reel/CqNkmNwqayu/?utm_source=ig_web_copy_link")
