#!/usr/bin/env python
#  upload to AWS S3 and clean up

# author Roman Sereda
# sereda.roman@gmail.com
#

#script run
#./VideoMultibitrateConverter.py <filename> <streamname>

import json
import os.path
import logging
import subprocess
import sys
import getopt

#get config
config_file = 'config.json'
json_data=open(config_file)
config = json.load(json_data)
json_data.close()

#Settings loggin
logging.basicConfig(filename=config['log'],level=logging.DEBUG)



# Get File Streams Data
def GetStreamInfo (ffprobe,filename):
	"""Get info about stream and return disc with data false if not a media file """
	if os.path.isfile(filename):
		command = [ ffprobe, "-v","quiet","-print_format","json","-show_format","-show_streams",  filename]
		process = subprocess.Popen(command, stdout=subprocess.PIPE)
		out, err = process.communicate()
		video_stat = json.loads(out)
		if not len (video_stat) is 0 :
			if 'streams' in video_stat:
				logging.debug('isVideo ' + 'tested ' + filename )
				if len (video_stat['streams']) >= 1:
					logging.debug('isVideo ' + 'tested the is Video file' + filename )
					return video_stat
				else :
					logging.debug('Only audio or video in '  + filename )
		else :
			logging.debug('The is not a video '  + filename )
	else:
		logging.debug(' No such file or directory '  + filename )
	return False


def EncodeMultibitrateStream (config,inFile):
	"""Create set of streams with different bitrate from input video file"""
	StreamInfo = GetStreamInfo (config['ffprobe'],inFile)
	if StreamInfo:
		print StreamInfo
		streamVideoID = []
		streamAudioID = []
		streamlist = [[],[]]
		#video multibitrate transcode
		#get first file stream in conteiner 
		for stream in StreamInfo ['streams']:
			if stream ['codec_type'] == 'video':
				streamVideoID = streamVideoID + [stream ['index']]
			if stream ['codec_type'] == 'audio':
				streamAudioID = streamAudioID + [stream ['index']]
		print streamVideoID , streamAudioID
		# get stream trancode config and prepare comanf for ffmpeg
		if not os.path.exists(config["out"] ):
			try :
				os.makedirs(config["out"])
			except :
				print "cant create " + config["out"] + "Access fobident"
				logging.debug("cant create " + config["out"] + "Access fobident")
				return False
		if not os.path.exists(config["out"]+"/mp4" ):
			try :
				os.makedirs(config["out"]+"/mp4")
				outfolder = config["out"]+"/mp4"
			except :
				print "cant create " + config["out"]/mp4 + "Access fobident"
				logging.debug("cant create " + config["out"]/mp4 + "Access fobident")
				return False
		else :
			outfolder = config["out"]+"/mp4"
		#Video stream processing
		for streamconf in config["video_streams"]:
			command =  [config["ffmpeg"] ,"-i",inFile , "-map", "0:"+str(streamVideoID[0]), "-s", streamconf["screen_size"],  "-aspect", streamconf["aspect"] , "-vcodec" , streamconf["codec"], "-b:v" ,streamconf["bitrate"] , "-profile:v" , streamconf["profile"], "-r", streamconf["framerate"],"-level", streamconf["level"],"-f", "mp4",  outfolder + "/video" + streamconf["bitrate"] + ".mp4" ]
			print command
			logging.debug(command)
			process = subprocess.Popen(command, stdout=subprocess.PIPE)
			out, err = process.communicate()
			StreamInfoTest = GetStreamInfo (config['ffprobe'],outfolder + "/video" + streamconf["bitrate"] + ".mp4")
			if StreamInfoTest :
				logging.debug("Video processing of " + streamconf["bitrate"] + "is OK!!!!")
				print "Video processing of " + streamconf["bitrate"] + "is OK!!!!"
				streamlist[0].append (outfolder + "/video" + streamconf["bitrate"] + ".mp4" )
			else :
				logging.debug("Video processing of " + streamconf["bitrate"] + "Fail!!!!")
				print "Video processing of " + streamconf["bitrate"] + "Fail!!!!"
		#Audio streams processing
		streamid = 0
		for streamconf in config["audio_streams"]:
			command =  [config["ffmpeg"] ,"-i" , inFile , "-map", "0:"+str(streamAudioID[0]),   "-acodec" , streamconf["codec"], "-b:a" ,streamconf["bitrate"] , "-ar", streamconf["sampling_rate"], "-ac", str (streamconf["ac"]) ,"-f", "mp4", str(outfolder) + "/audio" + streamconf["bitrate"] + ".mp4" ]
			print command
			logging.debug(command)
			process = subprocess.Popen(command, stdout=subprocess.PIPE)
			out, err = process.communicate()
			StreamInfoTest = GetStreamInfo (config['ffprobe'],outfolder + "/audio" + streamconf["bitrate"] + ".mp4")
			if StreamInfoTest :
				logging.debug("Audio processing of " + streamconf["bitrate"] + "is OK!!!!")
				print "Audio processing of " + streamconf["bitrate"] + "is OK!!!!"
				streamlist[1].append( outfolder + "/audio" + streamconf["bitrate"] + ".mp4" )
			else :
				logging.debug("Audioo processing of " + streamconf["bitrate"] + "Fail!!!!")
				print "Audio processing of " + streamconf["bitrate"] + "Fail!!!!"
		return streamlist
	else :
		return False





def ConvertMP4 (config,streamlist):
	print config
	"""ffmpeg -i $out_folder/mp4/audio64k.mp4 \
	-i $out_folder/mp4/audio96k.mp4 \
	-i $out_folder/mp4/audio128k.mp4 \
	-i $out_folder/mp4/video0200.mp4 \
	-i $out_folder/mp4/video0600.mp4 \
	-i $out_folder/mp4/video1200.mp4 \
	-i $out_folder/mp4/video3500.mp4 \
	-i $out_folder/mp4/video5000.mp4 \
	-i $out_folder/mp4/video6500.mp4 \
	-i $out_folder/mp4/video8500.mp4 \
	-map 0:0 -acodec copy  -map 1:0 -acodec copy -map 2:0 -acodec copy \
	-map 3:0 -c:v copy -map 4:0 -c:v copy -map 5:0 -c:v copy \
	-map 6:0 -c:v copy -map 7:0 -c:v copy -map 8:0 -c:v copy  \
	-map 9:0 -c:v copy   \
	-f mp4 -y $out_folder/mp4/multibitrate.mp4"""
	i=0
	command =  [config["ffmpeg"] ]
	for audio in streamlist[1]:
		command.append ("-i")
		command.append (audio)
	for video in streamlist[0]:
		command.append ("-i")
		command.append (video)
	for audio in streamlist[1]:
		command.append ("-map")
		command.append (str(i)+":0")
		command.append ("-acodec")
		command.append ("copy")
		i=i+1
	for video in streamlist[0]:
		command.append ("-map")
		command.append (str(i)+":0")
		command.append ("-vcodec")
		command.append ("copy")
		i=i+1
	command = command + ["-f", "mp4", "-y", config['out'] + "/mp4/multibitrate.mp4"]
	print command
	logging.debug(command)
	process = subprocess.Popen(command, stdout=subprocess.PIPE)
	out, err = process.communicate()
	StreamInfoTest = GetStreamInfo (config['ffprobe'],config['out'] + "/mp4/multibitrate.mp4")
	if StreamInfoTest :
		logging.debug("Multibitrate processing of "  + "is OK!!!!")
		print "Multibitrete processing of "  + "is OK!!!!"
		return config['out'] + "/mp4/multibitrate.mp4"
	else :
		return False




# Conver to multibitrate HLS stream
def ConvertHLS (config,streamlist):
	print config

def ConvertThumb (onfig,inFile):
	print config

def main (config,argv):
	inFile = ''
	StreamName = ''
	try:
		opts, args = getopt.getopt(argv,"hi:s:",["ifile=","stream="])
	except getopt.GetoptError:
		print 'test.py -i <inputfile> -s <streamname>'
		sys.exit(2)
	if (len(opts) < 2) :
		print 'test.py -i <inputfile> -s <streamname>'
		sys.exit()
	for opt, arg in opts:
		print opt, arg
		if opt == '-h':
			print 'test.py -i <inputfile> -s <streamname>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inFile = arg
		elif opt in ("-s", "--stream"):
			StreamName = arg
	print 'Input file is "', inFile
	print 'Stream name is "', StreamName
	config['out'] = config['out'] +"/"+ str(StreamName)
	streamlist = EncodeMultibitrateStream (config,inFile)
	if streamlist :
		print streamlist
		mp4 = ConvertMP4 (config,streamlist)
		print "multibitrate MP$" , mp4



if __name__ == "__main__":
	main (config,sys.argv[1:])
