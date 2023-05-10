import sys
import pyaudio
import wave
import time
import numpy as np
import sounddevice as sd
import queue


# NB! VB Audio Cable must be setup on the system prior to use of program!

######################
### Initialization ###
######################

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Size of each read-in chunk
CHUNK = 1024
SAMPLE_RATE = 44100
FORMAT = pyaudio.paInt16

# Identify the Output device index of VB-Cable
devices = []
for i in range(audio.get_device_count()):
    devices.append(audio.get_device_info_by_index(i))
    if devices[-1]["name"] == "VB-Cable":
        vb_device_index = devices[-1]["index"]
print("VB-Cable device index:", vb_device_index)

# Select WAV audio file, static for now.
FILE_NAME = "Astrowav.wav"
media_file = wave.open(FILE_NAME, 'rb')
media_stream = None
CHANNELS = media_file.getnchannels()

###############################
### Media Callback function ###
###############################

def media_callback(in_data, frame_count, time_info, status):
    data = media_file.readframes(frame_count)
    if len(data) == 0:
        return (None, pyaudio.paComplete)
    data = np.frombuffer(data, dtype=np.int16)
    data = data.reshape((frame_count, media_file.getnchannels()))
    return (data, pyaudio.paContinue)

#############################
### Voice Capture and Mix ###
#############################

# Define function for starting and reading from microphone
def start_and_read_microphone():
    # A queue for the mixed audio data from the virtual cable input
    vb_input_queue = queue.Queue()
    # Callback function for microphone input stream
    def microphone_callback(indata, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
    #If there is mixed audio data in the que, add to input

        if not vb_input_queue.empty():
            vb_data = vb_input_queue.get()
            mixed_data = indata + vb_data

            audio_data = media_file.readframes(frames)
            # If there is not enough data left in the file, rewind to the beginning and read again

            if len(audio_data) < frames * CHANNELS * 2:
                media_file.rewind()
                audio_data += media_file.readframes(frames - len(audio_data) // 2)

            audio_data = np.frombuffer(audio_data, dtype=np.int16)
            audio_data = audio_data.reshape((frames, CHANNELS))
            audio_data = audio_data[:, 0]  # extract only one channel

            mixed_data = np.concatenate((mixed_data, audio_data[:, np.newaxis]), axis=1)
            # Write the mixed data to the output stream
            outdata[:] = mixed_data
        else:
            outdata[:] = indata
    # media stream starts here
    global media_stream 
    media_stream = audio.open(
        format=audio.get_format_from_width(media_file.getsampwidth()),
        channels=CHANNELS,
        rate=media_file.getframerate(),
        output_device_index=vb_device_index,
        output=True,
        stream_callback=media_callback
    )

    with sd.Stream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=microphone_callback,
        blocksize=CHUNK):
        print('#' * 80)
        print('Press Ctrl+C to quit')
        print('#' * 80)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    media_stream.stop_stream()
    media_stream.close()
    audio.terminate()

start_and_read_microphone()
