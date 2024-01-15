import tkinter as tk
from pytube import YouTube
from pytube import exceptions
import requests
from PIL import Image, ImageTk
from io import BytesIO
import unicodedata
import re
import webbrowser


def openVidToBrowser(url):
    webbrowser.open_new(url)

def slugify(value, allow_unicode=False):
    '''
        Taken from https://github.com/django/django/blob/master/django/utils/text.py
        It helps to convert an validate the filename when downloading an mp3 or mp4 file
    '''
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def update_options(new_options):
    # Clear current options
    quality_select.set('')
    quality_menu['menu'].delete(0, 'end')
    # Add new options
    for option in new_options:
        quality_menu['menu'].add_command(label=option, command=tk._setit(quality_select, option))

    # Displays initial value selected
    quality_select.set(new_options[0])

def on_option_change(*args):
    # Updates vidoptmenu whenever the user changes their selected option
    selected_option = vidopt_select.get()
    res = get_vid_resolutions(yt, selected_option)
    update_options(res)
                            
def get_vid_resolutions(yt_obj, type):
    try:
        resolutions = set()
        # Resolutions for default
        if type == "Default":
            for stream in yt_obj.streams.filter(progressive=True).all():
                resolutions.add(str(stream.resolution))
            return list(resolutions)
        
        # Resolutions for video only
        elif type == "Video only":
            video_streams = yt_obj.streams.filter(file_extension='mp4').all()
            print("bidonly bro")

        # Returns empty list for audio only
        else:
            return ['']
        # Extract resolutions
        for stream in video_streams:
            resolutions.add(str(stream.resolution))

        resolutions.remove('None')
        return list(resolutions)

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def on_progress(video_stream, total_size, bytes_remaining):
    total_size = video_stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percent = (bytes_downloaded / total_size) * 100
    print("\r" + "▌" * int(percent) + " " * (100 - int(percent)) + " {}%".format(int(percent)), end='')

def download(event):
    global yt
    quality = quality_select.get()
    option =  vidopt_select.get()
    print("Quality: " + quality)
    print("Option: " + option)
    print("downloading!")
    match option:
        case "Video only":
            yt.streams.filter(only_video=True, 
            res = quality).first().download("downloads/video only", filename= slugify(yt.title)+"_"+quality+"_only_video.mp4")
        case "Audio only":
            yt.streams.filter(only_audio=True).first().download("downloads/audio only", filename= slugify(yt.title) +"_"+quality+"_only_audio.mp3")
        case "Default":
            yt.streams.filter(progressive=True,res = quality,file_extension='mp4').first().download("downloads/default", filename=slugify(yt.title) + "_" +quality+".mp4")

def showThumbnail(url):
    try:
        response = requests.get(url)
        # Checks for bad responses
        response.raise_for_status() 

        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        img = img.resize((int(300*1.5), int(225*1.5)), Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(img)
        
        # Update the label with the new image
        # vid_title.config(text=yt.title)
        thumbnail.config(image=photo)
        thumbnail.image = photo  # Keep a reference to the image to prevent garbage collection
    except Exception as e:
        print(f"Error loading image: {e}")

def handle_urlSubmit(event):
    window.focus()
    url = yt_ent.get()
    unav_err = "The url you entered is unavailable."
    reg_err = "Please enter a valid URL."
    print("User submitted an input!")
    if(url != ""):
        try:
            global yt
            yt = YouTube(url, on_progress_callback=on_progress)
            # handles error when yt video is private or deleted
        except (exceptions.VideoUnavailable, exceptions.RegexMatchError) as e:
            message.config(text = unav_err if e == exceptions.VideoUnavailable else reg_err )
            # Resets program to initial state
            dl_btn['state'] = tk.DISABLED
            quality_menu.config(state=tk.DISABLED)
            vidopt_menu.config(state=tk.DISABLED)
            thumbnail.image = ""
            window.geometry("600x250")
            # handles error when url is invalid
        else:
            # Enable download button and option menus if video is available

            dl_btn['state'] = tk.NORMAL
            quality_menu.config(state=tk.NORMAL)
            vidopt_menu.config(state=tk.NORMAL)
            vid_quality = get_vid_resolutions(yt, vidopt_select.get())
            update_options(vid_quality)
            quality_select.set(vid_quality[0])
            # Shows title and thumbnail of the video
            vid_title = yt.title
            if len(yt.title) > 60:
                vid_title = yt.title[0:60] + "..."
            message.config(text=vid_title)
            showThumbnail(yt.thumbnail_url)
            thumbnail.bind("<Button-1>", lambda e: openVidToBrowser(url))
            window.geometry("600x410")
            dl_btn.bind('<Button-1>', download)
    else:
        # Resets program to initial state
        message.config(text="")
        dl_btn['state'] = tk.DISABLED
        quality_menu.config(state=tk.DISABLED)
        vidopt_menu.config(state=tk.DISABLED)
        thumbnail.image = ""
        window.geometry("600x250")


# Initialize yt
yt = None

# Initialize windows and frames
window = tk.Tk()
window.title("YTConvert")
window.geometry("600x250")
window.resizable(False, False)

prompt_frame = tk.Frame(master = window, width=150, height = 150)
dl_frame = tk.Frame()

# Display title of the app
title = tk.Label(text="YouTube to MP4 Converter", font=('Arial', 25))

## Elements for prompting user to enter YouTube video URLs
yt_ent = tk.Entry(master=prompt_frame,width = 40, font=('Arial', 16)) 
yt_ent.bind("<Return>", handle_urlSubmit)

# Download Button
dl_btn = tk.Button(text="Download", 
    fg = "white", 
    bg = "black",
    master=dl_frame,
    cursor="hand2",
    width = 15,
    font= ('Arial', 11),
    borderwidth= 5,
    state= tk.DISABLED,
    relief=tk.RAISED)

vid_quality = ['']
vid_options = ['Default','Audio only', 'Video only']
quality_select = tk.StringVar()
vidopt_select = tk.StringVar()
quality_select.set(vid_quality[0])
vidopt_select.set(vid_options[0])
quality_menu = tk.OptionMenu(dl_frame, quality_select, *vid_quality,)
vidopt_menu = tk.OptionMenu(dl_frame, vidopt_select, *vid_options)
vidopt_select.trace_add("write", on_option_change)

quality_menu.config(font=('Arial', 12), state=tk.DISABLED)
vidopt_menu.config(font=('Arial', 12), state=tk.DISABLED)

# YouTube Video title and thumbnail
# vid_title = tk.Label(font=('Arial', 13))
thumbnail = tk.Label(window, cursor="hand2")

# Show error or title
message = tk.Label(font=('Arial', 16))

# Add elements to the GUI
title.pack()
tk.Label(text="Enter YT video URL here: ", master=prompt_frame, font=('Arial', 16)).pack()
yt_ent.pack()
dl_btn.pack(pady=10)
quality_menu.pack(side=tk.LEFT)
vidopt_menu.pack(padx=2)
prompt_frame.pack()
dl_frame.pack()
# vid_title.pack()
message.pack()
thumbnail.pack(pady = 10)

window.mainloop()


