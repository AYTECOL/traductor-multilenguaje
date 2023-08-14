from pydub import AudioSegment, silence

myaudio = AudioSegment.from_wav("test_audios/audio.wav")
dBFS=myaudio.dBFS

silence = silence.detect_silence(
    myaudio, 
    min_silence_len=1000, 
    silence_thresh=dBFS-16
    )

silence = [((start/1000),(stop/1000)) for start,stop in silence] #convert to sec

print(silence)

#TODO: Integrate with audio middleware demo
#TODO: For each slice, do the ASR (speech_recognition). Each call 
# is independant and can continue to Translation and TTS, however, 
# they are only applied to multimedia outputs once all are ready