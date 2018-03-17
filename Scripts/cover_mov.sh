#!/bin/bash
ffmpeg -i 0208-pm1.mov -vcodec libx264 -acodec libmp3lame -preset fast -crf 35 -y -vf "scale=1280:-1" -r 10 -ab 96k 0208-pm1.mp4

for f in `ls *.mov`;
do
    echo "Processing '$f'"
    ffmpeg -i $f -vcodec libx264 -acodec aac -preset fast -crf 32 -y -r 6 -ab 64k ./mp4/${f%%.mov}.mp4
    echo "Done"
done
