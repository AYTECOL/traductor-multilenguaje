import gradio as gr
import speech_recognition as sr                     # Libreria de Audio 
from ttsmms import TTS
from deep_translator import GoogleTranslator

import subprocess                                   # Libreria para procesamiento de comandos cmd para video 
import os
import time                                         # Libreria para manejo de tiempos
import math                                         # Libreria matemática, usada para redondeo de cifras
from threading import Thread                        # Librería para manejo de Hilos de procesamiento

# Idioma de ingreso
input_language = 'es-ES'

# Inicializa el modelo TTS para los idiomas soportados 
spanish = TTS("data/spa")    #español
english = TTS("data/eng")    #inglés
misak = TTS("data/gum")      #misak
quechua = TTS("data/quz")    #quechua

# Crea la lista de idiomas soportados para traducir y su modelo TTS correspondiente
#langs = [{"lang": 'spanish', "tts": spanish}, {"lang": 'english', "tts": english}, {"lang": 'guarani', "tts": misak}, {"lang": 'quechua', "tts": quechua}]
langs = [{"lang": 'english', "tts": english}, {"lang": 'quechua', "tts": quechua}, {"lang": 'spanish', "tts": spanish}]

# *************************** MÉTODOS ***************************     
# TEXT TO TEXT: Función que convierte texto a texto
def text_to_text(text, lang, logs_file):
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Traduciendo el texto a texto en el idioma seleccionado...")
    logs_file.write(tiempo[3] + " - Traduciendo el texto a texto en el idioma seleccionado...\n")
    selected_lang = next((lang_item for lang_item in langs if lang_item["lang"] == lang), None)   # Busca el idioma seleccionado en la lista de idiomas disponibles
    if selected_lang is None:
        raise ValueError(f"Lenguaje '{lang}' no disponible.")
    text_translated = GoogleTranslator(source='auto', target=lang).translate(text)   # Traduce el texto al idioma seleccionado usando Google Translator
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Texto traducido: ", text_translated)
    logs_file.write(tiempo[3] + " - Texto traducido: " + text_translated + "\n")
    return text_translated

# TEXT TO AUDIO: Función que convierte texto a audio
def text_to_audio(text, lang, logs_file):
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Convirtiendo el texto extraido a audio en el idioma seleccionado...")
    logs_file.write(tiempo[3] + " - Convirtiendo el texto extraido a audio en el idioma seleccionado...\n")
    selected_lang = next((lang_item for lang_item in langs if lang_item["lang"] == lang), None)   # Busca el idioma seleccionado en la lista de idiomas disponibles
    if selected_lang is None:
        raise ValueError(f"Lenguaje '{lang}' no disponible.")
    selected_tts = selected_lang["tts"]
    text_translated = text_to_text(text, lang, logs_file)                                       # Traduce el texto al idioma seleccionado usando Google Translator
    wav_path = "output.wav"
    selected_tts.synthesis(text_translated, wav_path=wav_path)                       # Genera el audio y lo graba como un archivo WAV
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Audio traducido generado: ",wav_path)
    logs_file.write(tiempo[3] + " - Audio traducido generado: " + wav_path + "\n")
    return wav_path, text_translated

# AUDIO TO TEXT: Función que convierte audio a texto usando Google's speech recognition API
def audio_to_text(audio_file, logs_file):
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Convirtiendo el audio a texto...")
    logs_file.write(tiempo[3] + " - Convirtiendo el audio a texto...\n")
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language=input_language)
        tiempo = time.ctime().split()
        print(tiempo[3] + " - Reconocimiento de texto obtenido del audio: ",text)
        logs_file.write(tiempo[3] + " - Reconocimiento de texto obtenido del audio: " + text + "\n")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition no pudo transcribir el audio.")
        logs_file.write("Google Speech Recognition no pudo transcribir el audio.\n")
        return None
    except sr.RequestError:
        print("Reconocimiento de audio no disponible.")
        logs_file.write("Reconocimiento de audio no disponible.\n")
        return None

# VIDEO TO AUDIO: Función que extrae el audio del video
def video_to_audio(video_file, output_audio_ext, logs_file):
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Extrayendo el audio del video...")
    logs_file.write(tiempo[3] + " - Extrayendo el audio del video...\n")
    filename, ext = os.path.splitext(video_file)                            # Se extrae el nombre del archivo y su extensión
    subprocess.call(["ffmpeg", "-y", "-i", video_file, "-ar", "16000", "-ac", "1", f"{filename+'_audio'}.{output_audio_ext}"],  # Se extrae el archivo de audio del video
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT)
    audio_video = filename + "_audio." + output_audio_ext
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Audio extraido: ",audio_video)
    logs_file.write(tiempo[3] + " - Audio extraido: " + audio_video + "\n")
    return audio_video

# VIDEO TO VIDEO: Función que concatena audio con el video traducido
def video_to_video(video_file, audio_file_traslated, output_video_ext, logs_file):
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Procesando el video para obtenerlo sin audio...")
    logs_file.write(tiempo[3] + " - Procesando el video para obtenerlo sin audio...\n")
    filename, ext = os.path.splitext(video_file)                            # Se extrae el nombre del archivo y su extensión   
    subprocess.call(["ffmpeg", "-y", "-i", video_file, "-an", f"{filename+'_muted'}.{output_video_ext}"],   
                stdout=subprocess.DEVNULL,                                  # Se extrae el video sin audio
                stderr=subprocess.STDOUT)
    video_mute = filename + "_muted." + output_video_ext

    tiempo = time.ctime().split()
    print(tiempo[3] + " - Doblando el video con el audio traducido...")
    logs_file.write(tiempo[3] + " - Doblando el video con el audio traducido...\n")
    subprocess.call(["ffmpeg", "-y", "-i", video_mute, "-i", audio_file_traslated, "-shortest", f"{filename+'_traslated'}.{output_video_ext}"],   
                stdout=subprocess.DEVNULL,                                  # Se concatena el video sin audio con el audio traducido
                stderr=subprocess.STDOUT)
    video_traslated = filename + "_traslated." + output_video_ext
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Video traducido: ",video_traslated)
    logs_file.write(tiempo[3] + " - Video traducido: " + video_traslated + "\n")
    return video_traslated

# VIDEO TO VIDEO SUBTITULADO: Función que coloca subtitulos traducidos al video
def video_to_video_subtitled(video_file, text_traslated, output_video_ext, logs_file):
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Procesando el video subtitulado...")
    logs_file.write(tiempo[3] + " - Procesando el video subtitulado...\n")
    subtitles = text_traslated.split()
    filename, ext = os.path.splitext(video_file)                            # Se extrae el nombre del archivo y su extensión   
    #filedir = os.path.dirname(video_file)
    #subtitles_file = open(f"{filename+'_subtitles'}.srt","w+")
    length_video = get_length_video(video_file)
    length_line_subtitle = math.ceil(len(subtitles)/length_video)           # Rate de palabras por segundo de video
    i=0
    j=0
    subtitles_line = []
    while i < length_video//length_line_subtitle:                           # Ciclo para timming de subtítulos
        while j < len(subtitles):
            line = ' '.join(subtitles[j:j+length_line_subtitle])            # Concatena palabras en una frase de acuerdo al rate de palabras
            subtitles_line.append(line)                                     # Inserta la frase en el vector final de subtítulos
            j += length_line_subtitle
        i += 1

    subtitles_file = open(f"{'video_subtitles'}.srt","w+")                  # Se genera el archivo de subtítulos .srt
    i=0
    while i < len(subtitles_line):
        subtitles_content = (''''''+str(i+1)+'''
'''+ time.strftime('%H:%M:%S', time.gmtime(i)) + ''',001 --> ''' + time.strftime('%H:%M:%S', time.gmtime(i+1)) + ''',000 --> ''' +
'''
''''''<b>'''+ subtitles_line[i] +'''</b>'''
'''
''')
        subtitles_file.write(subtitles_content)
        i += 1

    subtitles_file.close()
    #subtitles_file = filename + "_subtitles.srt"
    subprocess.call(["ffmpeg", "-y", "-copyts", "-i", video_file, "-vf", "subtitles=video_subtitles.srt:force_style='Fontname=Futura,Fontsize=20,MarginV=50,Shadow=1'", f"{filename+'_subtitled'}.{output_video_ext}"],   
                stdout=subprocess.DEVNULL,                                  # Se insertan los subtitulos al video con el audio original
                stderr=subprocess.STDOUT)
    
    video_subtitled = filename + "_subtitled." + output_video_ext
    tiempo = time.ctime().split()
    print(tiempo[3] + " - Video subtitulado: ",video_subtitled)
    logs_file.write(tiempo[3] + " - Video subtitulado: " + video_subtitled + "\n")
    return video_subtitled

def get_length_video(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

# *************************** MAIN ***************************
# ************************** ROUTER **************************
# ROUTER: Función para transcribir video, audio y texto al lenguaje seleccionado
def multimedia_to_multimedia_app(lang_input, video_file_upload, audio_file_upload, video_file_webcam, audio_file_microphone, text_input):
    tiempo = time.ctime().split()
    logs_file = open("logs.txt","w+")
    logs_file.write("LOGS TRADUCTOR MULTILENGUAJE\n")
    if video_file_webcam and lang_input:
        print("PROCESANDO GRABACIÓN VIDEO DE LA WEBCAM")
        logs_file.write("PROCESANDO GRABACIÓN VIDEO DE LA WEBCAM\n")
        print(tiempo[3] + " - Traduciendo el video grabado: " + video_file_webcam + " al idioma " + lang_input)
        logs_file.write(tiempo[3] + " - Traduciendo el video grabado: " + video_file_webcam + " al idioma " + lang_input + "\n")
        text_transcribed = convert_video_to_text_app(lang_input, video_file_webcam, logs_file)
        audio_traslated, text_translated = text_to_audio(text_transcribed, lang_input, logs_file)
        #video_subtitled = convert_video_to_video_subtitled_app(video_file_webcam, text_translated, logs_file)
        #video_traslated = convert_video_to_video_app(video_file_webcam, audio_traslated, logs_file)
        return_video_subtitled = [None]*1
        return_video_traslated = [None]*1
        hilo_video_subtitled = Thread(target=convert_video_to_video_subtitled_app, args=(video_file_webcam, text_translated,logs_file,return_video_subtitled,))
        hilo_video_traslated = Thread(target=convert_video_to_video_app, args=(video_file_webcam, audio_traslated,logs_file,return_video_traslated,))
        hilo_video_subtitled.start()
        hilo_video_traslated.start()
        hilo_video_subtitled.join()
        hilo_video_traslated.join()
        video_subtitled = return_video_subtitled[0]
        video_traslated = return_video_traslated[0]
        print("FIN PROCESO GRABACIÓN VIDEO DE LA WEBCAM")
        logs_file.write("FIN PROCESO GRABACIÓN VIDEO DE LA WEBCAM\n")
        logs_file.close()
        return text_transcribed, text_translated, audio_traslated, video_subtitled, video_traslated
    if audio_file_microphone and lang_input:
        print("PROCESANDO GRABACIÓN AUDIO DEL MICRÓFONO")
        logs_file.write("PROCESANDO GRABACIÓN AUDIO DEL MICRÓFONO\n")
        print(tiempo[3] + " - Traduciendo el audio grabado " + audio_file_microphone + " al idioma " + lang_input)
        logs_file.write(tiempo[3] + " - Traduciendo el audio grabado " + audio_file_microphone + " al idioma " + lang_input + "\n")
        text_translated, text_transcribed, audio_traslated = convert_audio_to_audio_app(lang_input,audio_file_microphone,logs_file)
        video_subtitled = None
        video_traslated = None
        print("FIN PROCESO GRABACIÓN AUDIO DEL MICRÓFONO")
        logs_file.write("FIN PROCESO GRABACIÓN AUDIO DEL MICRÓFONO\n")
        logs_file.close()
        return text_transcribed, text_translated, audio_traslated, video_subtitled, video_traslated
    if video_file_upload and lang_input:
        print("PROCESANDO ARCHIVO DE VIDEO")
        logs_file.write("PROCESANDO ARCHIVO DE VIDEO\n")
        print(tiempo[3] + " - Traduciendo el video ingresado " + video_file_upload + " al idioma " + lang_input)
        logs_file.write(tiempo[3] + " - Traduciendo el video ingresado " + video_file_upload + " al idioma " + lang_input + "\n")
        text_transcribed = convert_video_to_text_app(lang_input,video_file_upload,logs_file)
        audio_traslated, text_translated = text_to_audio(text_transcribed, lang_input,logs_file)
        #video_subtitled = convert_video_to_video_subtitled_app(video_file_upload, text_translated,logs_file)
        #video_traslated = convert_video_to_video_app(video_file_upload, audio_traslated,logs_file)
        return_video_subtitled = [None]*1
        return_video_traslated = [None]*1
        hilo_video_subtitled = Thread(target=convert_video_to_video_subtitled_app, args=(video_file_upload, text_translated,logs_file,return_video_subtitled,))
        hilo_video_traslated = Thread(target=convert_video_to_video_app, args=(video_file_upload, audio_traslated,logs_file,return_video_traslated,))
        hilo_video_subtitled.start()
        hilo_video_traslated.start()
        hilo_video_subtitled.join()
        hilo_video_traslated.join()
        video_subtitled = return_video_subtitled[0]
        video_traslated = return_video_traslated[0]

        print("FIN PROCESO ARCHIVO DE VIDEO")
        logs_file.write("FIN PROCESO ARCHIVO DE VIDEO\n")
        logs_file.close()
        return text_transcribed, text_translated, audio_traslated, video_subtitled, video_traslated
    if audio_file_upload and lang_input:
        print("PROCESANDO ARCHIVO DE AUDIO")
        logs_file.write("PROCESANDO ARCHIVO DE AUDIO\n")
        print(tiempo[3] + " - Traduciendo el audio ingresado " + audio_file_upload + " al idioma " + lang_input)
        logs_file.write(tiempo[3] + " - Traduciendo el audio ingresado " + audio_file_upload + " al idioma " + lang_input + "\n")
        text_translated, text_transcribed, audio_traslated = convert_audio_to_audio_app(lang_input,audio_file_upload,logs_file)
        video_subtitled = None
        video_traslated = None
        print("FIN PROCESO ARCHIVO DE AUDIO")
        logs_file.write("FIN PROCESO ARCHIVO DE AUDIO\n")
        logs_file.close()
        return text_transcribed, text_translated, audio_traslated, video_subtitled, video_traslated
    if text_input and lang_input:
        print("PROCESANDO TEXTO INGRESADO")
        logs_file.write("PROCESANDO TEXTO INGRESADO\n")
        print(tiempo[3] + " - Traduciendo el texto ingresado " + text_input + " al idioma " + lang_input)
        logs_file.write(tiempo[3] + " - Traduciendo el texto ingresado " + text_input + " al idioma " + lang_input + "\n")
        audio_traslated, text_translated = text_to_audio(text_input, lang_input, logs_file)
        video_subtitled = None
        video_traslated = None
        print("FIN PROCESO TEXTO INGRESADO")
        logs_file.write("FIN PROCESO TEXTO INGRESADO\n")
        logs_file.close()
        return text_input, text_translated, audio_traslated, video_subtitled, video_traslated
    if not lang_input:
        print("Error - Lenguaje no ingresado")
        raise gr.Error("Debes ingresar el idioma a traducir")
    
# *************************** SERVICIOS ***************************
# t2t: Traducir el texto a texto en el idioma deseado
def convert_text_to_text_app(lang_input, text_to_translate, logs_file):
    if text_to_translate:
        print("Traduciendo texto " + text_to_translate + " al idioma " + lang_input)
        logs_file.write("Traduciendo texto " + text_to_translate + " al idioma " + lang_input + "\n")
        text_translated = text_to_text(text_to_translate, lang_input, logs_file)
        return text_translated

# a2t: Transcribir el audio a texto
def convert_audio_to_text_app(lang_input, audio_file, logs_file):
    if audio_file:
        print("Convirtiendo audio " + audio_file + " al idioma " + lang_input)
        logs_file.write("Convirtiendo audio " + audio_file + " al idioma " + lang_input + "\n")
        text_translated = audio_to_text(audio_file, logs_file)
        return text_translated   

# a2a: Transcribir el audio a texto y de texto al audio traducido
def convert_audio_to_audio_app(lang_input, audio_file, logs_file):
    if audio_file:
        print("Traduciendo audio " + audio_file + " al idioma deseado...")
        logs_file.write("Traduciendo audio " + audio_file + " al idioma deseado...\n")
        text_transcribed = audio_to_text(audio_file, logs_file)
        audio_traslated, text_translated = text_to_audio(text_transcribed, lang_input, logs_file)
        return text_translated, text_transcribed, audio_traslated

# v2t: Convertir video a audio usando 'ffmpeg' con módulo 'subprocess'
def convert_video_to_text_app(lang_input,video_file, logs_file, output_audio_ext="wav"):
    print("Procesando video " + video_file + " para convertirlo a texto...")
    logs_file.write("Procesando video " + video_file + " para convertirlo a texto...\n")
    audio_video = video_to_audio(video_file, output_audio_ext, logs_file)
    text_translated = convert_audio_to_text_app(lang_input,audio_video, logs_file)
    return text_translated

# v2v: Convertir video a video
def convert_video_to_video_app(video_file, audio_file_traslated, logs_file, return_video_traslated, output_video_ext="webm"):
    print("Procesando video " + video_file + " para traducirlo...")
    logs_file.write("Procesando video " + video_file + " para traducirlo...\n")
    video_traslated = video_to_video(video_file, audio_file_traslated, output_video_ext,logs_file)
    return_video_traslated[0] = video_traslated
    #return video_traslated

# v2vs: Convertir video a video subtitulado
def convert_video_to_video_subtitled_app(video_file, text_translated, logs_file, return_video_subtitled, output_video_ext="webm"):
    print("Procesando video " + video_file + " para subtitularlo...")
    logs_file.write("Procesando video " + video_file + " para subtitularlo...\n")
    video_subtitled = video_to_video_subtitled(video_file, text_translated, output_video_ext, logs_file)
    return_video_subtitled[0] = video_subtitled
    #return video_subtitled

# *************************** INTERFAZ ***************************
# Entradas y salidas en la interfaz Gradio
lang_input = gr.inputs.Dropdown(choices=[lang["lang"] for lang in langs], label="Selecciona el idioma al cual deseas traducir:*")
#video_input_file = gr.Video(label= "Noticias Caracol", value="https://www.caracoltv.com/senal-vivo")
<<<<<<< HEAD
video_input_file = gr.Video(label= "Noticias Caracol", value="C:/Noticias/noticias_caracol_1.mp4", type="mp4")
#video_input_file = gr.Video(label= "Noticias Caracol", source="upload", type="mp4")
video_input_webcam = gr.Video(label= "Noticias Caracol en vivo", type="mp4", source="webcam", include_audio=1, optional=1)
audio_input_file = gr.Audio(label="Caracol Radio", value="C:/Noticias/caracol_radio.mp3", type="filepath")
audio_input_microphone = gr.Audio(label="Caracol Radio en vivo", source="microphone", type="filepath")
=======
video_input_file = gr.Video(label= "Noticias Caracol", value="D:/Noticias/noticias_caracol_long.mp4", type="mp4")
#video_input_file = gr.Video(label= "Noticias Caracol", source="upload", type="mp4")
video_input_webcam = gr.Video(label= "Noticias Caracol en vivo", type="mp4", source="webcam", include_audio=1, optional=1)
audio_input_file = gr.Audio(label="Blue Radio", value="D:/Noticias/caracol_radio.mp3", type="filepath")
audio_input_microphone = gr.Audio(label="Blue Radio en vivo", source="microphone", type="filepath")
>>>>>>> 9e38eecdc076892e866e18daa8c9dbf54ab6f7cc
text_input = gr.inputs.Textbox(label="Noticia a traducir:")
output_text_transcribed = gr.outputs.Textbox(label="Transcripción")
output_text_traslated = gr.outputs.Textbox(label="Traducción")
output_audio = gr.outputs.Audio(label="Audio traducido", type='filepath')
output_video_subtitled = gr.outputs.Video(label="Noticia subtitulada", type="webm")
output_video_traslated = gr.outputs.Video(label="Noticia traducida", type="webm")

"""""""""
embed_html = '<iframe width="560" height="315" src="https://www.youtube.com/embed/EngW7tLk6R8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
with gr.Blocks() as interface:
    gr.HTML(embed_html)
"""""""""

# Crea la interfaz Gradio para multimedia_to_multimedia_app
interface = gr.Interface(
    fn=multimedia_to_multimedia_app,
    inputs=[lang_input, video_input_file, audio_input_file, video_input_webcam, audio_input_microphone, text_input],
    outputs=[output_text_transcribed, output_text_traslated, output_audio, output_video_subtitled, output_video_traslated],
    title="TRADUCTOR MULTILENGUA DE NOTICIAS | AYTÉ - CARACOL",
    description="Ingresa la noticia que deseas traducir:",
    #theme = gr.themes.Soft()
    theme=gr.themes.Default(primary_hue="blue")
)
#interface.launch()              # Lanza la interfaz
interface.launch(share=True, auth=("caracol", "caracol"), server_name=("127.0.0.1"), server_port=(7860), favicon_path=())
