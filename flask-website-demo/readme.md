how to run:

`pip install flask, requests, yt-dlp`

sign into youtube in your browser.

NOTE: I have `scripts/download_songs.py` set to use firefox. If you use another browser change `    "cookiesfrombrowser": ["firefox"]` in the config to the browser of your choice

install ffmpeg from https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z

extract to ffmpeg folder (overwrite any present files)

make sure `ffmpeg/bin/` exists

run app.py

might not run on macos, sorry (you probably need to change the filepaths in the python files)

I tried to use generic paths when possible, but i might have missed some. ffmpeg was pretty weird to set up and I wont be surprised if something goes wrong on anything that isnt windows, where i wrote this code on.

Note for Ross: You had cosine metrics in the annoy model scripts, but i couldnt get them to run. Based of my 5 seconds of research it seems like Angular is a cosine function so i used that instead.