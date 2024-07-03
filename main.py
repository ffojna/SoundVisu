import sounddevice as sd
import scipy.io.wavfile
import numpy as np
import scipy.fftpack
import os, keyboard
from PIL import Image, ImageTk
import tkinter as tk


# paths to images (mapujesz tutaj odpowiednie obrazy (ścieżki) do dźwięków)
NOTE_IMAGES = {
    "E2": "images/E2.png",
    "G2": "images/G2.png",
    "A2": "images/A2.png",
    "D3": "images/D3.png"
}

# general settings
SAMPLE_FREQ = 44100                         # sample frequency in Hz
WINDOW_SIZE = 44100                         # window size of the DFT in samples
WINDOW_STEP = 21050                         # step size of window
WINDOW_T_LEN = WINDOW_SIZE / SAMPLE_FREQ    # length of window in seconds
SAMPLE_T_LENGTH = 1 / SAMPLE_FREQ           # length between two samples in seconds (to też ze wzoru)
windowSamples = [0 for _ in range(WINDOW_SIZE)]
closestNote = ''
SAMPLE_DUR = 2      # sample length in seconds (tylko do testowania sounddevice)

# funciton to find closest note for given pitch
CONCERT_PITCH = 440
ALL_NOTES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch/CONCERT_PITCH) * 12))
    closest_note = ALL_NOTES[i%12] + str(4 + (i + 9) // 12) # ze wzoru na i
    closest_pitch = CONCERT_PITCH*2**(i/12)                 # ze wzoru na f(i)
    return closest_note, closest_pitch

# setting up the image display
def update_image(img_path):
    new_image = Image.open(img_path)
    new_display = ImageTk.PhotoImage(new_image)
    label.config(image=new_display)
    label.image = new_display

def callback(indata, frames, time, status):
    global windowSamples, closestNote
    if status:
        print(status)
    if any(indata):
        windowSamples = np.concatenate((windowSamples, indata[:, 0]))
        windowSamples = windowSamples[len(indata[:, 0]):]
        magnitudeSpec = abs(scipy.fftpack.fft(windowSamples)[:len(windowSamples)//2])
        
        for i in range(int(62/(SAMPLE_FREQ/WINDOW_SIZE))):
            magnitudeSpec[i] = 0
        
        maxInd = np.argmax(magnitudeSpec)
        maxFreq = maxInd * (SAMPLE_FREQ / WINDOW_SIZE)
        closestNote, closestPitch = find_closest_note(maxFreq)
        
        os.system('cls' if os.name=='nt' else 'clear')
        diffPitch = maxFreq - closestPitch
        print(f"Closest note: {closestNote} {diffPitch:.1f}")
    else:
        print("no input")

# stop the program button
running = True
def stop_loop():
    global running
    running = False
    print("Stopping...")
keyboard.add_hotkey('esc', stop_loop)

# main program
root = tk.Tk()
root.title("SoundVisu v1.5")

image = Image.open("images/init.png")
display = ImageTk.PhotoImage(image)
label = tk.Label(root, image=display)
label.pack()

try:
  with sd.InputStream(channels=1, callback=callback,
    blocksize=WINDOW_STEP,
    samplerate=SAMPLE_FREQ):
    while running:
        root.update_idletasks()
        root.update()
        if closestNote in NOTE_IMAGES:
            img_path = NOTE_IMAGES[closestNote]
            update_image(img_path)
except Exception as e:
    print(str(e))