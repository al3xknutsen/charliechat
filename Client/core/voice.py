from pyaudio import PyAudio, paInt16
from core.thread import MultiThread
from time import sleep
# from socket import socket
# from core.global_vars import host, port


voice_buffer = ""

class VoiceManager:
    voice = PyAudio()
    
    
    def init_voice(self):
        self.recvstream = self.voice.open(format=paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024)
    
    
    def send_voice(self):
        while self.voice_activated:
            self.datastream.put(("send", {"datatype": "voice", "data": self.sendstream.read(1024)}))
    
    
    def recv_voice(self, data):
        global voice_buffer
        voice_buffer += data
        #self.recvstream.write(data)
    
    
    def empty_voicebuffer(self):
        global voice_buffer
        while True:
            if len(voice_buffer) > 0:
                self.recvstream.write(voice_buffer)
                voice_buffer = ""
            sleep(1)
    
    
    def toggle_voice(self, event):
        self.voice_activated = event.GetEventObject().GetValue()
                
        if self.voice_activated:
            self.sendstream = self.voice.open(format=paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
            MultiThread(self.send_voice).start()
        else:
            self.sendstream.stop_stream()
            self.sendstream.close()
        
        # ENABLE WHEN PUTTING UP OWN VOICE SERVER
#         if self.voice_activated:
#             voiceclient = socket()
#             voiceclient.connect(host, port + 1)
#         else:
#             voiceclient.close()