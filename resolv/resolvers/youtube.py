import re, urllib, urllib2
import resolv

def resolve(url):
	try:
		contents = urllib2.urlopen(url).read()
	except:
		raise resolv.ResolverError("Could not retrieve the specified URL.")
	
	map_start = "url_encoded_fmt_stream_map="
	map_end = "\\u0026amp;"
	
	try:
		pos_start = contents.index(map_start) + len(map_start) + 6
		snippet = contents[pos_start:]
	except ValueError:
		raise resolv.ResolverError("The starting position for the YouTube player configuration could not be found. Is the URL really a valid video page?")
	
	try:
		pos_end = snippet.index(map_end)
		stream_map = snippet[:pos_end]
	except ValueError:
		raise resolv.ResolverError("The ending position for the YouTube player configuration could not be found.")
	
	try:
		stream_map = urllib.unquote(stream_map)
		streams = stream_map.split(',url=')
	except:
		raise resolv.ResolverError("The YouTube player configuration is corrupted.")
	
	stream_pool = []
	
	for stream in streams:
		fields = stream.split('&')
		
		if len(fields) < 5:
			raise resolv.ResolverError("The amount of fields in the YouTube player configuration is incorrect.")
		
		video_url = urllib.unquote(fields[0])
		quality = fields[1].split("=")[1]
		fallback_host = fields[2].split("=")[1]
		mimetype = urllib.unquote(fields[3].split("=")[1])
		itag = fields[4].split("=", 2)[1]
		
		if mimetype.startswith("video/mp4"):
			video_format = "mp4"
		elif mimetype.startswith("video/x-flv"):
			video_format = "flv"
		elif mimetype.startswith("video/3gpp"):
			video_format = "3gp"
		elif mimetype.startswith("video/webm"):
			video_format = "webm"
		else:
			video_format = "unknown"
		
		if quality == "small":
			video_quality = "240p"
			video_priority = 5
		elif quality == "medium":
			video_quality = "360p"
			video_priority = 4
		elif quality == "large":
			video_quality = "480p"
			video_priority = 3
		elif quality == "hd720":
			video_quality = "720p"
			video_priority = 2
		elif quality == "hd1080":
			video_quality = "1080p"
			video_priority = 1
		else:
			video_quality = "unknown"
		
		stream_dict = {
			'url'		: video_url,
			'quality'	: video_quality,
			'priority'	: video_priority,
			'format'	: video_format
		}
		
		stream_pool.append(stream_dict)
	
	try:
		video_title = unescape(re.search('<meta property="og:title" content="([^"]*)">', contents).group(1))
	except:
		raise resolv.ResolverError("Could not find the video title.")
	
	return { 'title': video_title, 'videos': stream_pool }
