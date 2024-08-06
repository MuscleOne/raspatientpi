import os
import argparse
import wave
import time
import json
import shutil

import openai
import speech_recognition as sr
import pyaudio
import playsound
import paho.mqtt.client as mqtt

from raspatientpi.config import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
from django.conf import settings

class RaspatientPi:

    def __init__(self, openai_api_key, openai_assistant_id, gpt_model="gpt-4o", whisper_model="whisper-1", tts_model="tts-1", voice='nova', log_on_mqtt=False, use_avatar=False, mqtt_broker = "localhost", mqtt_port = 1883, mqtt_topic = "simul/raspatientpi"):
        self.api_key = openai_api_key
        self.assistant_id = openai_assistant_id
        self.models = {
            'gpt': gpt_model,
            'whisper': whisper_model,
            'tts': tts_model
        }
        self.voice = voice or 'nova'

        self.client = openai.OpenAI(api_key=self.api_key)

        self.input_sound_file = "input.wav"
        self.output_sound_file = "output.mp3"

        self.log_on_mqtt = log_on_mqtt

        if self.log_on_mqtt:
            self.setup_mqtt(mqtt_broker, mqtt_port, mqtt_topic)

        self.use_avatar = use_avatar

    def setup_mqtt(self, broker, port, topic):
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "PythonMQTTPublisher")
        self.mqtt_client.on_connect = self.on_connect_mqtt
        self.mqtt_client.connect(broker, port, 60)
        self.mqtt_client.loop_start()
        print("MQTT client set up!")

        self.mqtt_topic = topic

    def on_connect_mqtt(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

    def log(self, sender, msg, additional_data=None):
        if self.log_on_mqtt:
            result = self.mqtt_client.publish(self.mqtt_topic, json.dumps({"sender": sender, "message": msg, "additional_data": additional_data}))
            status = result[0]
            if status == 0:
                print(f"Sent `{msg}` to topic `{self.mqtt_topic}`")
            else:
                print(f"Failed to send message to topic {self.mqtt_topic}")

        print(sender, ":", msg)

    @staticmethod
    def list_devices():
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            print(i, dev['name'], dev['maxInputChannels'])

        '''
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        for i in range(0, numdevices):
            if(p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')):
                print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
        '''

    '''
    def record_alt():
        # Source: https://makersportal.com/blog/2018/8/23/recording-audio-on-the-raspberry-pi-with-python-and-a-usb-microphone
        form_1 = pyaudio.paInt16 # 16-bit resolution
        chans = 1 # 1 channel
        samp_rate = 44100 # 44.1kHz sampling rate
        chunk = 4096 # 2^12 samples for buffer
        record_secs = 3 # seconds to record
        dev_index = 1 # device index found by p.get_device_info_by_index(ii)
        wav_output_filename = input_sound_file # name of .wav file

        audio = pyaudio.PyAudio() # create pyaudio instantiation

        # create pyaudio stream
        stream = audio.open(format = form_1, rate = samp_rate, channels = chans, input_device_index = dev_index, input = True, frames_per_buffer=chunk)
        print("Recording", end = ' ... ', flush=True)
        frames = []

        # loop through stream and append audio chunks to frame array
        for ii in range(0,int((samp_rate/chunk)*record_secs)):
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)

        print("Done!")

        # stop the stream, close it, and terminate the pyaudio instantiation
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # save the audio frames as .wav file
        wavefile = wave.open(wav_output_filename,'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()
    '''

    def record(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.log('System', 'Speak! (say "stop" to exit)')
            audio = r.listen(source)
            self.log('System', 'Done!')

            with open(self.input_sound_file, "wb") as file:
                file.write(audio.get_wav_data())

    def play(self):
        playsound.playsound(self.output_sound_file)

    def openai_stt(self):
        audio_file= open(self.input_sound_file, "rb")
        transcription = self.client.audio.transcriptions.create(model=self.models['whisper'], file=audio_file)
        return transcription.text

    def openai_chatcompletion(self, text):
        response = self.client.chat.completions.create(
            model=self.models['gpt'],
            messages=[
                {"role": "user", "content": text}
            ]
        )

        return response.choices[0].message.content

    def openai_tts(self, text):
        with self.client.audio.speech.with_streaming_response.create(
            model=self.models['tts'],
            voice=self.voice,
            input=text,
        ) as response:
            print(response)
            response.stream_to_file(self.output_sound_file)

    def _transcribe_generated_audio(self):
        audio_file= open(self.output_sound_file, "rb")
        
        transcription = self.client.audio.transcriptions.create(
            model=self.models['whisper'], 
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"]
        )

        return {
            'file': settings.MEDIA_URL + self.output_sound_file, 
            'language': transcription.language[:2],
            'segments': transcription.segments,
            'words': transcription.words
        }

    def create_assistant(self):
        assistant = self.client.beta.assistants.create(
            name="Virtual Standardized Patient",
            instructions="You are a standardized patient, i.e., an actor playing a patient, based on a pre-defined scenario, that will be used in medical education and simulation. You will answer to input from a medical student playing a doctor, according to the symptoms and disease described in the scenario. You only uncover your symptoms, history, medication or other disease-related details when asked for, don't spoil everything at once!",
            model=self.models['gpt'],
        )

        return assistant.id

    def create_thread(self, scenario):
        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "assistant",
                    "content": scenario,
                }
            ]
        )

        return thread

    def send_message(self, thread, message):
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=self.assistant_id,
            additional_messages = [{ "role": "user", "content": message }]
        )

        if run.status == 'completed': 
            messages = self.client.beta.threads.messages.list(thread_id=thread.id, order="desc", limit=1)
            return messages.data[0].content[0].text.value
        else:
            return "Status: {}".format(run.status)

    def loop(self, thread, textual=False):
        while True:
            try:
                if not textual:
                    self.record()
                    message = self.openai_stt()
                    self.log("You", message)
                else:
                    message = input("> ")
                
                if len(message.strip()) == 0 or message.strip() == ".":
                    continue

                if message.strip().rstrip(".").lower() == "stop":
                    self.log("Patient", "Bye!")
                    self.openai_tts("Bye!")
                    self.play()
                    self.clean()  
                    break

                #response = self.openai_chatcompletion(s)
                response = self.send_message(thread, message)

                if not self.use_avatar:
                    self.log("Patient", response)

                if not textual:
                    self.openai_tts(response)

                    if self.use_avatar:
                        additional_data = self._transcribe_generated_audio()
                        shutil.copy(self.output_sound_file, settings.MEDIA_ROOT)
                        self.log("Patient", response, additional_data)
                    else:
                        self.play()
                    self.clean()            
            except (KeyboardInterrupt, EOFError):
                pass

    def clean(self):
        for f in [self.input_sound_file, self.output_sound_file]:
            if os.path.exists(f):
                os.remove(f)

    def openai_tts_with_captions(self, text):
        media_file = os.path.join(settings.MEDIA_ROOT, self.output_sound_file)

        with self.client.audio.speech.with_streaming_response.create(model=self.models['tts'], voice=self.voice, input=text) as response:
            response.stream_to_file(media_file)

            audio_file= open(media_file, "rb")
            
            transcription = self.client.audio.transcriptions.create(
                model=self.models['whisper'], 
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"]
            )

            return {
                'file': settings.MEDIA_URL + self.output_sound_file, 
                'language': transcription.language[:2],
                'segments': transcription.segments,
                'words': transcription.words
            }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RaspatientPi: A Raspberry Pi-based virtual standardized patient for medical education and simulation.')
    parser.add_argument("-s", "--scenario", help = "", required = False, default = None)
    parser.add_argument("-v", "--voice", help = "cf. https://platform.openai.com/docs/guides/text-to-speech/voice-options", required = False, default = None)
    args = parser.parse_args()

    #RaspatientPi.list_devices()
    
    test_scenario = "You are a 49-year old male called Bob Skinner who recently developed a strong cough. You don't smoke. You have had a temperature of 39°C over the last 24 hours. You took acetaminophen. You recently travelled to China."
    scenario = args.scenario if args.scenario else test_scenario

    pp = RaspatientPi(OPENAI_API_KEY, OPENAI_ASSISTANT_ID, voice=args.voice)
    #print(pp.create_assistant())

    thread = pp.create_thread(scenario)
    pp.loop(thread)
