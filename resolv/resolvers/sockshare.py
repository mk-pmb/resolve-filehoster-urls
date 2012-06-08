import re
import resolv

def resolve(url):
	try:
		import mechanize
	except ImportError:
		raise resolv.ResolverError("The Python mechanize module is required to resolve SockShare URLs.")
	
	matches = re.search("https?:\/\/(www\.)?sockshare\.com\/(file|embed)\/([A-Z0-9]+)", url)

	if matches is None:
		raise resolv.ResolverError("The provided URL is not a valid SockShare URL.")
	
	video_id = matches.group(3)
	
	try:
		browser = mechanize.Browser()
		browser.set_handle_robots(False)
		browser.open("http://sockshare.com/embed/%s" % video_id)
	except:
		raise resolv.ResolverError("The SockShare site could not be reached.")
	
	try:
		browser.select_form(nr=0)
		result = browser.submit()
		page = result.read()
	except Exception, e:
		raise resolv.ResolverError("The file was removed, or the URL is incorrect.")
		
	matches = re.search("playlist: '([^']+)'", page)
	
	if matches is None:
		raise resolv.ResolverError("No playlist was found on the given URL; the SockShare server for this file may be in maintenance mode, or the given URL may not be a video file. The SockShare resolver currently only supports video links.")
	
	playlist = matches.group(1)
	
	try:
		browser.open("http://www.sockshare.com%s" % playlist)
	except:
		raise resolv.ResolverError("The playlist file for the given URL could not be loaded.")
	
	matches = re.search("url=\"([^\"]+)\" type=\"video\/x-flv\"", browser.response().read())
	
	if matches is None:
		raise resolv.ResolverError("The playlist file does not contain any video URLs. The SockShare resolver currently only supports video links.")
	
	video_file = matches.group(1)
	
	try:
		video_title = unescape(re.search('<a href="\/file\/[^"]+"[^>]*><strong>([^<]*)<\/strong><\/a>', page).group(1))
	except:
		raise resolv.ResolverError("Could not find the video title.")
	
	stream_dict = {
		'url'		: video_file,
		'quality'	: "unknown",
		'priority'	: 1,
		'format'	: "unknown"
	}
	
	return { 'title': video_title, 'videos': [stream_dict] }
