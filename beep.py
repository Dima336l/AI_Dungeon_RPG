import numpy as np
from scipy.io.wavfile import write

sample_rate = 44100  # samples per second
duration = 0.1  # seconds
frequency = 440  # Hz (A4 note)

t = np.linspace(0, duration, int(sample_rate * duration), False)
note = 0.3 * np.sin(frequency * 2 * np.pi * t)

# Convert to 16-bit data
audio = (note * (2**15 - 1)).astype(np.int16)

write("beep.wav", sample_rate, audio)
print("beep.wav created!")
