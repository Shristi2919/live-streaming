import socket
import threading
import cv2
import numpy as np
import pyaudio

clients = []
UDP_PORT_SEND_VIDEO = 5005
UDP_PORT_SEND_AUDIO = 5006  # Port for audio
sock_send_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_send_audio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Open the camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

print("Server is running, waiting for clients...")

# Audio setup
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()


def receive_connections():
    while True:
        try:
            # Receiving clients for video stream
            addr = (input("Enter client's IP: "), UDP_PORT_SEND_VIDEO)
            if addr not in clients:
                clients.append(addr)
                print(f"New client connected: {addr}")
        except Exception as e:
            print(f"Error receiving connection: {e}")


# Start receiving thread for UDP connections
threading.Thread(target=receive_connections, daemon=True).start()


def stream_video():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        _, buffer = cv2.imencode('.jpg', frame)
        data = buffer.tobytes()

        for client in clients:
            try:
                sock_send_video.sendto(data, client)
                print(f"Sent video frame to {client}")
            except Exception as e:
                print(f"Error sending video to {client}: {e}")

        cv2.imshow("Server Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


# Start video streaming thread
threading.Thread(target=stream_video, daemon=True).start()


def stream_audio():
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        try:
            audio_data = stream.read(CHUNK)
            for client in clients:
                try:
                    sock_send_audio.sendto(audio_data, (client[0], UDP_PORT_SEND_AUDIO))
                except Exception as e:
                    print(f"Error sending audio to {client}: {e}")
        except Exception as e:
            print(f"Error capturing audio: {e}")
            break

    stream.stop_stream()
    stream.close()


# Start audio streaming thread
threading.Thread(target=stream_audio, daemon=True).start()

# Keep the server running
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Server shutting down...")

# Clean up resources
cap.release()
sock_send_video.close()
sock_send_audio.close()
cv2.destroyAllWindows()
p.terminate()
