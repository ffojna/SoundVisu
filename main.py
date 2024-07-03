import sounddevice as sd
import scipy.io.wavfile
import numpy as np
import scipy.fftpack
import os, keyboard
from PIL import Image, ImageTk
import tkinter as tk
import threading


# paths to images (mapujesz tutaj odpowiednie obrazy (ścieżki) do dźwięków)
NOTE_IMAGES = {
    "E2": "images/E2.png",
    "F2": "images/F2.png",
    "F#2": "images/F#2.png",
    "G2": "images/G2.png",
    "G#2": "images/G#2.png",
    "A2": "images/A2.png",
    "A#2": "images/A#2.png",
    "B2": "images/B2.png",
    "C3": "images/C3.png",
    "C#3": "images/C#3.png",
    "D3": "images/D3.png",
    "D#3": "images/D#3.png",
    "E3": "images/E3.png",
    "F3": "images/F3.png",
    "F#3": "images/F#3.png",
    "G3": "images/G3.png",
    "G#3": "images/G#3.png",
    "A3": "images/A3.png",
    "A#3": "images/A#3.png",
    "B3": "images/B3.png",
    "C4": "images/C4.png",
    "C#4": "images/C#4.png",
    "D4": "images/D4.png",
    "D#4": "images/D#4.png",
    "E4": "images/E4.png",
    "F4": "images/F4.png",
    "F#4": "images/F#4.png",
    "G4": "images/G4.png",
    "G#4": "images/G#4.png",
    "A4": "images/A4.png",
    "A#4": "images/A#4.png",
    "B4": "images/B4.png",
    "C5": "images/C5.png",
    "C#5": "images/C#5.png",
    "D5": "images/D5.png",
    "D#5": "images/D#5.png",
    "E5": "images/E5.png"
}


# general settings
SAMPLE_FREQ = 44100                         # sample frequency in Hz
WINDOW_SIZE = 4096                         # window size of the DFT in samples
WINDOW_STEP = 2048                         # step size of window
WINDOW_T_LEN = WINDOW_SIZE / SAMPLE_FREQ    # length of window in seconds
SAMPLE_T_LENGTH = 1 / SAMPLE_FREQ           # length between two samples in seconds (to też ze wzoru)
NOISE_GATE_THRESHOLD = 0.05
NUM_OF_SAMLPES_AVG = 6
windowSamples = np.zeros(WINDOW_SIZE)
closestNote = ''
SAMPLE_DUR = 2      # sample length in seconds (tylko do testowania sounddevice)

# funciton to find closest note for given pitch
CONCERT_PITCH = 440
ALL_NOTES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch/CONCERT_PITCH) * 12))
    closest_note = ALL_NOTES[i % 12] + str(4 + (i + 9) // 12) # ze wzoru na i
    closest_pitch = CONCERT_PITCH*2**(i/12)                 # ze wzoru na f(i)
    return closest_note, closest_pitch

# setting up the image display
def update_image(img_path):
    new_image = Image.open(img_path)
    new_display = ImageTk.PhotoImage(new_image)
    label.config(image=new_display)
    label.image = new_display
    noteName.config(text=img_path)

recent_freqs = []

def callback(indata, frames, time, status):
    global windowSamples, closestNote
    if status:
        print(status)
    if any(indata):
        windowSamples = np.roll(windowSamples, -frames)
        windowSamples[-frames:] = indata[:, 0]
        magnitudeSpec = abs(scipy.fftpack.fft(windowSamples)[:len(windowSamples)//2])
        
        magnitudeSpec[:int(62 / (SAMPLE_FREQ / WINDOW_SIZE))] = 0
        
        maxInd = np.argmax(magnitudeSpec)
        maxFreq = maxInd * (SAMPLE_FREQ / WINDOW_SIZE)
        # new_closestNote, closestPitch = find_closest_note(maxFreq)
        
        recent_freqs.append(maxFreq)
        if len(recent_freqs) > NUM_OF_SAMLPES_AVG:
            recent_freqs.pop(0)
            
        # avgFreq = np.mean(recent_freqs)   # po średniej
        avgFreq = max(set(recent_freqs), key=recent_freqs.count)
        new_closestNote, closestPitch = find_closest_note(avgFreq)
        
        # noise gate
        if magnitudeSpec[maxInd] < NOISE_GATE_THRESHOLD:
            return
        
        if new_closestNote != closestNote:
            closestNote = new_closestNote
            os.system('cls' if os.name=='nt' else 'clear')
            diffPitch = maxFreq - closestPitch
            print(f"Closest note: {closestNote} {diffPitch:.1f}")
            print(recent_freqs)
            print(avgFreq)
            if closestNote in NOTE_IMAGES:
                img_path = NOTE_IMAGES[closestNote]
                update_image(img_path)
                
                
    else:
        print("no input")

# stop the program button
running = True
def stop_loop():
    global running
    running = False
    print("Stopping...")
    on_closing()
keyboard.add_hotkey('esc', stop_loop)

# main program
root = tk.Tk()
root.title("SoundVisu v1.8")

image = Image.open("images/init.png")
display = ImageTk.PhotoImage(image)
label = tk.Label(root, image=display)
label.pack()

noteName = tk.Label(root, text="ready")
noteName.pack()

def start_audio_stream():
    try:
        with sd.InputStream(channels=1, callback=callback, blocksize=WINDOW_STEP, samplerate=SAMPLE_FREQ):
            while running:
                root.update_idletasks()
                root.update()
    except Exception as e:
        print(str(e))

audio_thread = threading.Thread(target=start_audio_stream)
audio_thread.start()

def on_closing():
    global running
    running = False
    root.destroy()

# closing window
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

# ensure proper closing
running = False
audio_thread.join()