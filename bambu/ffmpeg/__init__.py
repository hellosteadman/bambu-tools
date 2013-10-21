from tempfile import mkstemp
from django.conf import settings
from pymediainfo import MediaInfo
import os, subprocess, logging, mimetypes, time

ASPECT_RATIO = getattr(settings, 'FFMPEG_ASPECT_RATIO', '16:9')
WIDTH = getattr(settings, 'FFMPEG_WIDTH', 640)

if ASPECT_RATIO == '16:9':
	ASPECT_RATIO_SLASH = '16/9'
elif ASPECT_RATIO == '4:3':
	ASPECT_RATIO_SLASH = '4/3'
else:
	raise Exception('Unrecognised aspect ratio %s' % ASPECT_RATIO)

x, y = map(float, ASPECT_RATIO.split(':'))
HEIGHT = str(int(float(WIDTH) / x * y))
WIDTH = str(WIDTH)

VIDEO_ENCODING_COMMAND = 'ffmpeg -i %s -s ' + WIDTH + 'x' + HEIGHT + ' -vf "%sscale=iw*sar:ih , pad=max(iw\,ih*(' + ASPECT_RATIO_SLASH + ')):ow/(' + ASPECT_RATIO_SLASH + '):(ow-iw)/2:(oh-ih)/2" -aspect ' + ASPECT_RATIO + ' -r 30000/1001 -b:v 200k -bt 240k -vcodec libx264 -vpre ipod' + WIDTH + ' -acodec libfaac -ac 2 -ar 48000 -ab 192k -y %s'
AUDIO_ENCODING_COMMAND = 'ffmpeg -i %s %s -acodec libfaac -ac 2 -ar 48000 -ab 192k -y %s'
THUMBNAIL_ENCODING_COMMAND = 'ffmpeg -i %s -vf "%sscale=iw*sar:ih , pad=max(iw\,ih*(' + ASPECT_RATIO_SLASH + ')):ow/(' + ASPECT_RATIO_SLASH + '):(ow-iw)/2:(oh-ih)/2" -aspect ' + ASPECT_RATIO + ' -f image2 -vframes 1 -y %s'

def _run_command(command, extension, source):
	handles = []
	logger = logging.getLogger('bambu.ffmpeg')
	logging.info('Started encode')
	transpose = ''
	
	try:
		info = MediaInfo.parse(source)
		video_tracks = [t for t in info.tracks if t.track_type == 'Video']
		
		for video in video_tracks:
			if video.rotation == '90.000':
				transpose = 'transpose=1,'
			elif video.rotation == '180.000':
				transpose = 'vflip,'
			elif video.rotation == '270.000':
				transpose = 'transpose=2,'
	except OSError:
		logger.warn('Mediainfo library not installed')
	
	d = {}
	
	try:
		handle, dest = mkstemp(
			extension,
			dir = settings.TEMP_DIR
		)
		
		os.close(handle)
		output = subprocess.Popen(
			command % (source, transpose, dest),
			shell = True,
			stdout = subprocess.PIPE
		).stdout.read()
		
		if os.stat(dest).st_size > 0:
			f = open(dest, 'r')
			handles.append(f)
			success = True
		else:
			success = False
		
		d = {
			'command': command % (source, transpose, dest),
			'source': source,
			'dest': dest,
			'extension': extension,
			'output': output
		}
		
		for f in handles:
			f.close()
	except Exception, ex:
		logger.error('Error encoding: %s' % unicode(ex))
		success = False
	
	if success:
		return dest
	else:
		if os.path.exists(dest):
			os.remove(dest)
		
		if any(d):
			logger.error('Conversion failed',
				extra = {
					'data': d
				}
			)
		
		return None

def convert_video(source):
	return _run_command(VIDEO_ENCODING_COMMAND, '.mp4', source)

def convert_audio(source):
	return _run_command(AUDIO_ENCODING_COMMAND, '.aac', source)

def create_thumbnail(source):
	return _run_command(THUMBNAIL_ENCODING_COMMAND, '.jpg', source)