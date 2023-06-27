import gradio as gr
import speech_recognition as sr                     # Libreria de Audio 
from ttsmms import TTS
from deep_translator import GoogleTranslator

import subprocess                                   # Librerias de video 
import os
import shutil                                       # Libreria para borrar archivos para limpiar la caché

# Inicializa el modelo TTS para los idiomas soportados 
spanish = TTS("data/spa")    #español
english = TTS("data/eng")    #inglés
misak = TTS("data/gum")      #misak
quechua = TTS("data/quz")    #quechua

# Crea la lista de idiomas soportados y su modelo TTS correspondiente
langs = [{"lang": 'spanish', "tts": spanish}, {"lang": 'english', "tts": english}, {"lang": 'guarani', "tts": misak}, {"lang": 'quechua', "tts": quechua}]

# *************************** BORRRAR CACHE ***************************     
def delete_cache():
    print("Borrando cache: ",os.getcwd())
    #shutil.rmtree('C:/Users/jorge/AppData/Local/Temp/gradio/')
"""""""""
    path = 'C:/Users/jorge/AppData/Local/Temp/gradio/'
    # checking whether the file is present in path or not
    if os.path.exists(path):
        for root_folder, folders, files in os.walk(path):               # iterating over each and every folder and file in the path
            # checking folder from the root_folder
            for folder in folders:
                folder_path = os.path.join(root_folder, folder)         # folder path
                shutil.rmtree(folder_path)                              # invoking the remove_folder function

            # checking the current directory files
            for file in files:          
                file_path = os.path.join(root_folder, file)             # file path
                shutil.rmtree(file_path)                                # invoking the remove_file function
    else:
        print(f'"{path}" is not found')                 # file/folder is not found
"""""""""

# *************************** MÉTODOS ***************************     
# TEXT TO TEXT: Función que convierte texto a texto
def text_to_text(text, lang):
    selected_lang = next((lang_item for lang_item in langs if lang_item["lang"] == lang), None)   # Busca el idioma seleccionado en la lista de idiomas disponibles
    if selected_lang is None:
        raise ValueError(f"Lenguaje '{lang}' no disponible.")
    text_translated = GoogleTranslator(source='auto', target=lang).translate(text)   # Traduce el texto al idioma seleccionado usando Google Translator
    print("Texto traducido: "+text_translated)
    return text_translated

# TEXT TO AUDIO: Función que convierte texto a audio
def text_to_audio(text, lang):
    selected_lang = next((lang_item for lang_item in langs if lang_item["lang"] == lang), None)   # Busca el idioma seleccionado en la lista de idiomas disponibles
    if selected_lang is None:
        raise ValueError(f"Lenguaje '{lang}' no disponible.")
    selected_tts = selected_lang["tts"]
    text_translated = text_to_text(text, lang)                                       # Traduce el texto al idioma seleccionado usando Google Translator
    wav_path = "output.wav"
    selected_tts.synthesis(text_translated, wav_path=wav_path)                       # Genera el audio y lo graba como un archivo WAV
    print("Audio traducido generado.")
    return wav_path

# AUDIO TO TEXT: Función que convierte audio a texto usando Google's speech recognition API
def audio_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        print("Reconocimiento de audio obtenido: ",text)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        print("Reconocimiento de audio no disponible.")
        return None

# VIDEO TO AUDIO: Función que extrae el audio del video
def video_to_audio(video_file, output_audio_ext):
    filename, ext = os.path.splitext(video_file)                            # Se extrae el nombre del archivo y su extensión
    subprocess.call(["ffmpeg", "-y", "-i", video_file, "ar", "16000", f"{filename+'_audio'}.{output_audio_ext}"],  # Se extrae el archivo de audio del video
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT)
    audio_video = filename + "_audio." + output_audio_ext  
    return audio_video

# VIDEO TO VIDEO: Función que concatena audio con el video traducido
def video_to_video(video_file, audio_file_traslated, output_video_ext):
    filename, ext = os.path.splitext(video_file)                            # Se extrae el nombre del archivo y su extensión   
    subprocess.call(["ffmpeg", "-y", "-i", video_file, "-an", f"{filename+'_muted'}.{output_video_ext}"],   
                stdout=subprocess.DEVNULL,                                  # Se extrae el video sin audio
                stderr=subprocess.STDOUT)
    video_mute = filename + "_muted." + output_video_ext
    video_length = get_length_video(video_file)
    print("Duración del video: ",video_length)
 
    subprocess.call(["ffmpeg", "-y", "-i", video_mute, "-i", audio_file_traslated, "-shortest", f"{filename+'_traslated'}.{output_video_ext}"],   
                stdout=subprocess.DEVNULL,                                  # Se concatena el video sin audio con el audio traducido
                stderr=subprocess.STDOUT)
    video_traslated = filename + "_traslated." + output_video_ext
    print("Video traducido: ",video_traslated)
    return video_traslated

# VIDEO TO VIDEO SUBTITULADO: Función que coloca subtitulos traducidos al video
def video_to_video_subtitled(video_file, text_traslated, output_video_ext):
    print("Video a subtitular:!!!!!!!!!!!!!!!!!!!!!",video_file)
    subtitles = text_traslated.split()
    filename, ext = os.path.splitext(video_file)                            # Se extrae el nombre del archivo y su extensión   
    subtitles_file = open(f"{filename+'_subtitles'}.srt","w+")
    subtitles_content  = ('''1
00:00:00,000 --> 00:00:00,500
'''+subtitles[0]+
'''
2
00:00:00,501 --> 00:00:01,000
'''+subtitles[1]+
'''
3
00:00:01,001 --> 00:00:01,500
'''+subtitles[2]+
'''
4
00:00:01,501 --> 00:00:02,000
'''+subtitles[3]+
'''
''')
    subtitles_file.write(subtitles_content)
    subtitles_file.close()
    subtitles_file = filename + "_subtitles.srt"
    subprocess.call(["ffmpeg", "-y", "-copyts", "-i", video_file, "-vf", subtitles_file, f"{filename+'_subtitled'}.{output_video_ext}"],   
                stdout=subprocess.DEVNULL,                                  # Se concatena el video sin audio con el audio traducido
                stderr=subprocess.STDOUT)
    video_subtitled = filename + "_subtitled." + output_video_ext
    print("Video subtitulado: ",video_subtitled)
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
    #delete_cache()
    if video_file_webcam:
        print("PROCESANDO GRABACIÓN VIDEO DE LA WEBCAM")
        print("Traduciendo el video grabado: " + video_file_webcam + " al idioma " + lang_input)
        text_transcribed = convert_video_to_text_app(lang_input,video_file_webcam)
        text_translated = convert_text_to_text_app(lang_input, text_transcribed)
        audio_traslated = text_to_audio(text_transcribed, lang_input)
        video_subtitled = convert_video_to_video_subtitled_app(video_file_webcam, text_translated)
        video_traslated = convert_video_to_video_app(video_file_webcam, audio_traslated)
        print("FIN PROCESO GRABACIÓN VIDEO DE LA WEBCAM")
        return text_transcribed, text_translated, audio_traslated, video_subtitled, video_traslated
    if audio_file_microphone:
        print("PROCESANDO GRABACIÓN AUDIO DEL MICRÓFONO")
        print("Traduciendo el audio grabado " + audio_file_microphone + " al idioma " + lang_input)
        text_transcribed, audio_traslated = convert_audio_to_audio_app(lang_input,audio_file_microphone)
        text_translated = convert_text_to_text_app(lang_input, text_transcribed)
        video_subtitled = None
        video_traslated = None
        print("FIN PROCESO GRABACIÓN AUDIO DEL MICRÓFONO")
        return text_transcribed, text_translated, audio_traslated, video_subtitled, video_traslated
    if video_file_upload:
        print("PROCESANDO ARCHIVO DE VIDEO")
        print("Traduciendo el video ingresado " + video_file_upload + " al idioma " + lang_input)
        text_transcribed = convert_video_to_text_app(lang_input,video_file_upload)
        text_translated = convert_text_to_text_app(lang_input, text_transcribed)
        audio_traslated = text_to_audio(text_transcribed, lang_input)
        video_subtitled = convert_video_to_video_subtitled_app(video_file_upload, text_translated)
        video_traslated = convert_video_to_video_app(video_file_upload, audio_traslated)
        print("FIN PROCESO ARCHIVO DE VIDEO")
        return text_transcribed, text_translated, audio_traslated, video_subtitled, video_traslated
    if audio_file_upload:
        print("PROCESANDO ARCHIVO DE AUDIO")
        print("Traduciendo el audio ingresado " + audio_file_upload + " al idioma " + lang_input)
        text_transcribed, audio_traslated = convert_audio_to_audio_app(lang_input,audio_file_upload)
        text_translated = convert_text_to_text_app(lang_input, text_transcribed)
        video_subtitled = None
        video_traslated = None
        print("FIN PROCESO ARCHIVO DE AUDIO")
        return text_transcribed, text_translated, audio_traslated, video_subtitled, video_traslated
    else:
        print("PROCESANDO TEXTO INGRESADO")
        text_translated = convert_text_to_text_app(lang_input, text_input)
        audio_traslated = text_to_audio(text_input, lang_input)
        video_subtitled = None
        video_traslated = None
        print("FIN PROCESO TEXTO INGRESADO")
        return text_input, text_translated, audio_traslated, video_subtitled, video_traslated

# *************************** SERVICIOS ***************************
# t2t: Traducir el texto a texto en el idioma deseado
def convert_text_to_text_app(lang_input, text_to_translate):
    if text_to_translate:
        print("Traduciendo text " + text_to_translate + " al idioma " + lang_input)
        text_translated = text_to_text(text_to_translate, lang_input)
        return text_translated 

# a2t: Transcribir el audio a texto
def convert_audio_to_text_app(lang_input, audio_file):
    if audio_file:
        print("Convirtiendo audio " + audio_file + " al idioma " + lang_input)
        text_translated = audio_to_text(audio_file)
        return text_translated   

# a2a: Transcribir el audio a texto y de texto al audio traducido
def convert_audio_to_audio_app(lang_input, audio_file):
    if audio_file:
        print("Traduciendo audio " + audio_file + " al idioma deseado...")
        text_translated = audio_to_text(audio_file)
        audio_traslated = text_to_audio(text_translated, lang_input)
        return text_translated, audio_traslated 

# v2t: Convertir video a audio usando 'ffmpeg' con módulo 'subprocess'
def convert_video_to_text_app(lang_input,video_file, output_audio_ext="wav"):
    print("Procesando video " + video_file + " para convertirlo a texto...")
    audio_video = video_to_audio(video_file, output_audio_ext)
    text_translated = convert_audio_to_text_app(lang_input,audio_video)
    return text_translated

# v2v: Convertir video a video
def convert_video_to_video_app(video_file, audio_file_traslated, output_video_ext="webm"):
    print("Procesando video " + video_file + " para traducirlo...")
    video_traslated = video_to_video(video_file, audio_file_traslated, output_video_ext)
    return video_traslated

# v2vs: Convertir video a video subtitulado
def convert_video_to_video_subtitled_app(video_file, text_translated, output_video_ext="webm"):
    print("Procesando video " + video_file + " para subtitularlo...")
    video_subtitled = video_to_video_subtitled(video_file, text_translated, output_video_ext)
    return video_subtitled

# *************************** INTERFAZ ***************************
# Entradas y salidas en la interfaz Gradio
lang_input = gr.inputs.Dropdown(choices=[lang["lang"] for lang in langs], label="Selecciona el idioma al cual deseas traducir:")
video_input_file = gr.Video(label= "Noticias Caracol", value="D:/Noticias/noticias_caracol_tv.mp4", type="mp4")
#video_input_file = gr.Video(label= "Noticias Caracol", source="upload", type="mp4")
video_input_webcam = gr.Video(label= "Noticias Caracol en vivo", type="mp4", source="webcam", include_audio=1, optional=1)
audio_input_file = gr.Audio(label="Caracol Radio", source="upload", type="filepath")
audio_input_microphone = gr.Audio(label="Caracol Radio en vivo", source="microphone", type="filepath")
text_input = gr.inputs.Textbox(label="Noticia a traducir:")
output_text_transcribed = gr.outputs.Textbox(label="Transcripción")
output_text_traslated = gr.outputs.Textbox(label="Traducción")
output_audio = gr.outputs.Audio(label="Audio traducido", type='filepath')
output_video_subtitled = gr.outputs.Video(label="Noticia subtitulada", type="webm")
output_video_traslated = gr.outputs.Video(label="Noticia traducida", type="webm")

# Crea la interfaz Gradio para multimedia_to_multimedia_app
interface = gr.Interface(
    fn=multimedia_to_multimedia_app,
    inputs=[lang_input, video_input_file, audio_input_file, video_input_webcam, audio_input_microphone, text_input],
    outputs=[output_text_transcribed, output_text_traslated, output_audio, output_video_subtitled, output_video_traslated],
    title="TRADUCTOR MULTILENGUA DE NOTICIAS | AYTÉ - GRUPO PRISA",
    description="Ingresa la noticia que deseas traducir:",
    #theme = gr.themes.Soft()
    #theme=gr.themes.Default(primary_hue="blue", secondary_hue="orange")
)
interface.launch()              # Lanza la interfaz
#interface.launch(share=True, auth=("admin", "123"), server_name=("127.0.0.1"), server_port=(1111), favicon_path=())
