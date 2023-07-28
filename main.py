import tkinter as tk
from tkinter import filedialog
import os
import vlc
import time
from VLC import *

class AudioSync:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio player and mic syncing.")
        self.root.geometry("500x400")
        
        # create the files array, add the menus on top of the proram
        self.files = []
        self.mainMenu = tk.Menu(root)
        self.fileMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.helpMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.fileMenu.add_command(label="Open", command=self.open_file)
        self.mainMenu.add_cascade(label="File", menu=self.fileMenu)
        self.mainMenu.add_cascade(label="Help", menu=self.helpMenu)
        self.helpMenu.add_command(label="About", command=self.about)
        self.root.config(menu=self.mainMenu)

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.X)
        
        #The buttons, start, pause and play, stop
        self.playBtn = tk.Button(self.frame, text="Start", command=self.play)
        self.playBtn.pack(side=tk.LEFT)

        self.pauseBtn = tk.Button(self.frame, text="Pause/Resume", command=self.pause)
        self.pauseBtn.pack(side=tk.LEFT)

        self.stopBtn = tk.Button(self.frame, text="Stop", command=self.stop)
        self.stopBtn.pack(side=tk.LEFT)
        
        
        # a scale for the volume, vlc takes % from 0 to 100 ( but works even above? ),
        self.volumeScale = tk.Scale(self.frame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, label="Volume", command=self.set_volume)
        # set default volume to 50%
        self.volumeScale.set(50)
        # to organise neatly on right side
        self.volumeScale.pack(side=tk.RIGHT)
        
        # the list for the songs
        self.listBox = tk.Listbox(self.root)
        self.listBox.pack(fill=tk.BOTH, expand=True)
        
        #Another scale, this one is for the track's time
        self.timeScale = tk.Scale(self.root, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, command= self.timescale_move, label="Time ( seconds )")
        #make it as long as the window allows
        self.timeScale.pack(fill=tk.X)
        
        # call a function when user presses the close button
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def open_file(self):
        # some audio file types for the program not to open unnecessary ones
        types = (("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("All files", "*.*"))
        # for some reason tk.filedialog does not work, so import filedialog separately
        path = filedialog.askopenfilename(initialdir=".", title="Select mp3 or wav file", filetypes= types)
        
        if path:
            self.files.append(path)
            filename = os.path.basename(path)
            # add the filename to the list
            self.listBox.insert(tk.END, filename)
       
    def timescale_move(self, timescale_var):
        #need to check if player instance is present
        if 'playerInstance' in globals() and playerInstance is not None:
            # This is to make sure it was the user that made the time adjustment, since the scale is updating when playing.
            moveDifference = int(timescale_var) - round(playerInstance.get_time()/1000)
            if moveDifference > 2 or moveDifference < -2:
                # vlc takes time in milliseconds, so need to multiply/divide seconds by 1000 dependig on use case
                playerInstance.set_time(int(timescale_var)*1000)

    def update_time_scale(self, event=None):
        # get the current time, divide by 1000 to remove the annoying milliseconds and get seconds
        currentTime = round(playerInstance.get_time()/1000)
        self.timeScale.set(currentTime)
        # need to update the position of the scale slider, constantly calling it once every second.
        # I have tested, sometimes it appears to skip a second, this is due to a delay in tkinter scale refresh and the current time.
        # they are not in perfect sync, may need to play arround with timings, millisecond roundings and delays more.
        self.root.after(1000, self.update_time_scale)
            
    def play(self):
        global playerInstance
        #this part is for starting again if a track is playing or starting a new track
        if 'playerInstance' in globals() and playerInstance is not None:
            #stop the audio and clear the playerInstance, since we either start over or start a new track
            stop_audio(playerInstance)
            playerInstance = None
        # check if a track is selected in the listbox
        if self.listBox.curselection():
            # get the value of a selected item, in this case we need the index of the song in the list
            index = self.listBox.curselection()[0]
            path = self.files[index]
            playerInstance = play_audio(path)
            #Set the default volume value
            self.volumeScale.set(50)
            # need a delay for the file data to load, otherwise get_length will not work
            time.sleep(0.1)
            # set the time scale's new maximum value, default is set to 100, but we need the track's length in sec
            max = round( playerInstance.get_length()/1000)
            self.timeScale.config(to=max-2)
            print("PLAYING")
            #also call the update scale function to update our time slider
            self.update_time_scale()
            
        
    # the pause function that we call to play/pause the current track
    def pause(self):
        if 'playerInstance' in globals() and playerInstance is not None:  
            pause_audio(playerInstance)

    def stop(self):
        if 'playerInstance' in globals() and playerInstance is not None:   
            stop_audio(playerInstance)
            print("STOP")
    # function to set the vlume depending on the slider's current value
    def set_volume(self, value):
        if 'playerInstance' in globals() and playerInstance is not None:
            set_Volume(playerInstance, int(value))

    def about(self):
        # the text for the about section. Feels useless, but still.
        text = "An audio and microphone mixer for all of your online sound streaming/sharing needs. Go File -> Open, select an mp3 track. Select it in the list, and click play."
        tk.messagebox.showinfo("About", text)

    def close(self):
        # ask if user wants to close this beautiful program
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            print("EXIT")
            quit()



root = tk.Tk()
syncInstance = AudioSync(root)
root.mainloop()


