#!/usr/bin/env python3

import subprocess                                   # Librerias de video 
import os

subtitles = "C\\\\:\\Users\\camil\\Desktop\\itcon\\traductor-multilenguaje\\noticias_caracol_small_subtitles.srt" # Sería filename + "_subtitles.srt"
subtitles_path = 'subtitles=' + subtitles.split(":")[0] + ":" + subtitles.split("\\\\:")[1].replace("\\","/") + ''
print(subtitles_path)
subprocess.call(["ffmpeg", "-y", "-copyts", "-i", "C:/Users/camil/Desktop/itcon/traductor-multilenguaje/noticias_caracol_tv.mp4", "-vf", subtitles_path, f"{'C:/Users/camil/Desktop/itcon/traductor-multilenguaje/output'+'_subtitled'}.{'mp4'}"],   
                stdout=subprocess.DEVNULL,                                  # Se concatena el video sin audio con el audio traducido
                stderr=subprocess.STDOUT)