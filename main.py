from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import whisper
import shutil
import os
import datetime
import subprocess
import io
from moviepy.editor import *
app = FastAPI()



model = whisper.load_model("base")
current_date = datetime.date.today()


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
   with open(f"{file.filename}-{current_date}.mp4", "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)
#    return {"filename": file.filename}
   video = VideoFileClip(f"{file.filename}-{current_date}.mp4")
   video.audio.write_audiofile(f"{file.filename}-{current_date}.mp3")
   result = model.transcribe(f"{file.filename}-{current_date}.mp3",fp16=False)
#    print(type(result["text"]))
   os.remove(f"./{file.filename}-{current_date}.mp4")
   os.remove(f"./{file.filename}-{current_date}.mp3")
   transcript =result["text"]

   # Split the transcript into individual sentences
   sentences = transcript.split('.')

   # Open a file for writing the subtitles
   srt_file = io.open('subtitles.srt', 'w', encoding='utf-8')

   # Write each subtitle to the SRT file
   for i, sentence in enumerate(sentences):
      start_time = i * 10  # Assumes each subtitle is 5 seconds long
      end_time = (i + 1) * 10
      srt_file.write('{}\n{} --> {}\n{}\n\n'.format(
         i+1,
         '{:02d}:{:02d}:{:02d},000'.format(0, 0, start_time),
         '{:02d}:{:02d}:{:02d},000'.format(0, 0, end_time),
         sentence.strip()))

   # Close the SRT file
   srt_file.close()
   # Print a message indicating that the subtitles have been generated
   print('Subtitles generated and saved to subtitles.srt')
   file_path = "./subtitles.srt"
   return FileResponse(file_path)
   