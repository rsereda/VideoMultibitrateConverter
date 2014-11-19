Video Multibitrate Converter  

Script can conver video file to set of multimitarte streams in different format.

Script make output in :
mp4 file with several audio and video stream
hls with set of different streams
hls with AES-128 encofing
Thunb of video

Usage ./VideoMultibitrateConverter -i <filename> -s <streamname>

<filename> - video file with audio that can be play
<streamname> - name of folder that will store all output
====================


install requrement

for script work you need ffmpeg . Best if you will have latest compiled version

for ubuntu https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu
for CentOS https://trac.ffmpeg.org/wiki/CompilationGuide/Centos
for mac    https://trac.ffmpeg.org/wiki/CompilationGuide/MacOSX
for windows simple get and install latest build 
http://ffmpeg.zeranoe.com/builds/



Configuration

in config.json you need set several parameters

path for output folder
path to ffmpeg
path to ffprobe
path for log file

set bulean valuest True or False for next option

    "hls": true
    "aes128": true
    "mp4": true

Than set encoding config sets.



config in JSON format





