import time
import sounddevice as sd
import numpy as np

from pydag.adapters.audio.AudioAdapter import AudioAdapter
from pydag.buffers.ListBuffer import ListBuffer

def test_000():

    duration = 2  # seconds
    sample_rate = 44100  # standard CD-quality

    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    print("Recording finished.")

    # `audio` is a NumPy array with audio samples
    print(audio.shape)  # (sample_rate * duration, 1)
    
    # Playback
    print("Playing back...")
    sd.play(audio, samplerate=sample_rate)
    sd.wait()
    print("Playback finished.")

def test_001():
    d = sd.query_devices(None, 'input')
    print(len(d))
    
def test_002():
    a = AudioAdapter()
    print(a.config_options())    

    
def test_010():
    sample_rate = 44100
    block_size = 1024  # number of frames per buffer (about 23ms at 44.1kHz)

    st = int(time.time() * 1000)
    
    def audio_callback(indata, frames, time, status):
        if status:
            print("Stream status:", status)
        
        volume = np.linalg.norm(indata)  # simple RMS volume
        #print(indata)
        print(f"Volume: {volume:.3f}")

    with sd.InputStream(callback=audio_callback,
                        channels=1,
                        samplerate=sample_rate,
                        blocksize=block_size):
        print("Streaming... Press Ctrl+C to stop. Or wait for 3 seconds.")
        try:
            while True:
                if int(time.time() * 1000) - st > 3_000:
                    break
        except KeyboardInterrupt:
            print("Stopped.")
            
def test_011():
    sample_rate = 44100
    block_size = 512  # number of frames per buffer (about 23ms at 44.1kHz)
    st = int(time.time() * 1000)
    
    buf = ListBuffer(id="AUDIO", capacity=512)
    buf.install()
        
    def audio_callback(indata, frames, time, status):
        if status:
            print("Stream status:", status)
        
        buf.push(indata.tolist())
        #volume = np.linalg.norm(indata)  # simple RMS volume
        #print(indata)
        #print(f"Volume: {volume:.3f}")
        #print(buf.data())

    with sd.InputStream(callback=audio_callback,
                        channels=1,
                        samplerate=sample_rate,
                        blocksize=block_size):
        print("Streaming... Press Ctrl+C to stop. Or wait for 3 seconds.")
        try:
            while True:
                time.sleep(1)
                print(buf.data())
                if int(time.time() * 1000) - st > 3_000:
                    break
                
        except KeyboardInterrupt:
            print("Stopped.")
            
def test_020():
    audio = AudioAdapter(id="A1", sample_rate=16_000)
    audio.install()       
    audio.connect()
    
    print(audio.config_options())
    
    
def test_030():
    
    audio = AudioAdapter(id = "A1", sample_rate = 16_000)
    audio.install()
    audio.connect()
    
    print(audio.config_options())
    
    buf = ListBuffer(capacity=10000)
    buf.install()
    buffers = buf.to_dict()
    
    audio.subscribe(buffers, None, 0, 512)
    
    time.sleep(1)
    
    audio.unsubscribe()
    
    print(buf.data())

    
def test_031():
    
    sr = 16_000
    st = 1
    n = 512
    
    audio = AudioAdapter(id = "A1", sample_rate = sr)
    audio.install()
    audio.connect()
    
    print(audio.config_options())
    
    buf = ListBuffer(capacity=sr * 2)
    buf.install()
    buffers = buf.to_dict()
    
    audio.subscribe(buffers, None, 0, n)
    
    time.sleep(st)
    
    audio.unsubscribe()
    
    data = buf.data(persistent=True)
    print(data)
    assert buf.size() > sr * st - 2 * n
    