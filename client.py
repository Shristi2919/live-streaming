import socket
import cv2
import numpy as np
import pyaudio
import threading

# UDP setup
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
VIDEO_PORT = 5005
AUDIO_PORT = 5006

video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
video_sock.bind((UDP_IP, VIDEO_PORT))

print("Client is ready to receive video...")

# Audio setup
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
audio_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
audio_sock.bind((UDP_IP, AUDIO_PORT))
p = pyaudio.PyAudio()

# Audio playback function
def play_audio():
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)

    while True:
        try:
            audio_data, addr = audio_sock.recvfrom(CHUNK * 2)
            stream.write(audio_data)
        except Exception as e:
            print(f"Error receiving audio: {e}")
            break

    stream.stop_stream()
    stream.close()

# Start audio thread
audio_thread = threading.Thread(target=play_audio)
audio_thread.start()

while True:
    try:
        # Receive video frame
        data, addr = video_sock.recvfrom(65507)  # Buffer size
        np_data = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

        if frame is not None:
            cv2.imshow("Client Stream", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Error receiving video: {e}")
        break

# Clean up resources
video_sock.close()
audio_sock.close()
cv2.destroyAllWindows()
p.terminate()
