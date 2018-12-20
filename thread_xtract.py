import pickle, os, subprocess, re, threading, requests, base64, sys, time
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
moodlesession = "22fbq760m6q5vunsd8hp52rre0"
f = open('all-data', 'rb')
data = pickle.load(f)
f.close()
'''


'''
class myThread (threading.Thread):
   def __init__(self, threadID, name, isubj, subj, subjlink, tix):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.isubj = isubj
      self.subj = subj
      self.subjlink = subjlink
      self.tix = tix
      # self.counter = counter
   def run(self):
      print ("Starting " + self.name)
      # print_time(self.name, self.counter, 5)
      func(self.isubj, self.subj, self.subjlink, self.tix)
      print ("Exiting " + self.name)

class fetchThread (threading.Thread):
   def __init__(self, threadID, name, audio, master_json_url, substitute, base_url, resp, content, path):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.audio = audio
      self.master_json_url = master_json_url
      self.substitute = substitute
      self.base_url = base_url
      self.resp = resp
      self.content = content
      self.path = path
      # self.counter = counter
   def run(self):
      print ("Starting " + self.name)
      # print_time(self.name, self.counter, 5)
      if self.audio == False:
        runThreadVideo(self.master_json_url, self.substitute, self.base_url, self.resp, self.content, self.path)
      else:
        runThreadAudio(self.master_json_url, self.substitute, self.base_url, self.resp, self.content, self.path)
      print ("Exiting " + self.name)

def xtract_url(s, i):
	i, j = i, i
	while s[i-1]!='"':
		i-=1
	while s[j+1]!='"':
		j+=1
	return i, j

def ex(t):
	return str(subprocess.Popen(f'{t}', shell=True, stdout=subprocess.PIPE).stdout.read())
ts = [0, 5, 39, 45, 55, 61, 65, 71, 82, 83, 98, 121, 128, 147, 167, 173, 182, 190, 199, 219]

def runThreadVideo(master_json_url, substitute, base_url, resp, content, path):
    heights = [(i, d['height']) for (i, d) in enumerate(content['video'])]
    idx, _ = max(heights, key=lambda h: h[1])
    video = content['video'][idx]
    video_base_url = base_url + 'video/' + video['base_url']
    print('base url:', video_base_url)

    filename = f"{path.split('/')[3]}.mp4"
    video_filename = filename
    print('saving to %s' % filename)

    # video_file = open(path + '.mp4', 'wb')

    init_segment = base64.b64decode(video['init_segment'])
    # video_file.write(init_segment)
    chk = 0
    resps = []
    for segment in tqdm(video['segments']):
        segment_url = video_base_url + segment['url']
        headers = requests.utils.default_headers()
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        resp = requests.get(segment_url, stream=True, headers = headers)
        if resp.status_code != 200:
            print('not 200!')
            # print(resp)
            # print(segment_url)
            chk = 1
            print(substitute)
            return
        resps.append(resp)
        # for chunk in resp:
        #     video_file.write(chunk)
    video_file = open(path + '.mp4', 'wb')
    video_file.write(init_segment)
    print('=============================================================***')
    ti = len(resps)
    for i, resp in tqdm(enumerate(resps)):
        # time.sleep(1)
        for j, chunk in enumerate(resp):
            print(f'Writing: {i}/{ti} : {j}')
            x = None
            while x is None:
                try:
                    x = video_file.write(chunk)
                except:
                    pass
            print('Done Writing video file')
    # video_file.write(resps)
    print('Flushing: video file')
    video_file.flush()
    print('Closing: video file')
    video_file.close()
    print('Returing: video file')
def runThreadAudio(master_json_url, substitute, base_url, resp, content, path):
    audio = content['audio'][0]
    audio_base_url = base_url + audio['base_url'][3:]
    print('base url:', audio_base_url)

    filename = f"{path.split('/')[3]}.mp4"
    audio_filename = filename
    print('saving to %s' % filename)

    # audio_file = open(path + '.mp3', 'wb')

    init_segment = base64.b64decode(audio['init_segment'])
    # audio_file.write(init_segment)
    chk = 0
    resps = []
    for segment in tqdm(audio['segments']):
        segment_url = audio_base_url + segment['url']
        resp = requests.get(segment_url, stream=True)
        if resp.status_code != 200:
            print('not 200!')
            # print(resp)
            # print(segment_url)
            chk = 1
            print(substitute)
            return
        resps.append(resp)
        # for chunk in resp:
        #     audio_file.write(chunk)
    audio_file = open(path + '.mp3', 'wb')
    audio_file.write(init_segment)
    for resp in resps:
    	for chunk in resp:
    		# print('Writing:')
    		audio_file.write(chunk)
    print('Flushing: audio file')
    audio_file.flush()
    print('Closing: audio file')
    audio_file.close()
    print('Returning: audio file')


def func(isubj, subj, subjlink, topicindex):
	d = {}
	subjtopics = topics[isubj]
	for isubjtopics, (topic, topiclink) in enumerate(subjtopics):
		vids = videos[topicindex]
		for vidlink, vidtitle in vids:
			if vidtitle == 'News forum' or 'resource' in vidlink:
				continue
			
			# string += f'{subj}                 {topic}                  {vidtitle}\n'
			print(f'{subj}                 {topic}                  {vidtitle}')
			req_url = f"curl '{vidlink}' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.9,hi;q=0.8' -H 'Cookie: _ga=GA1.2.151426872.1521890632; _gid=GA1.2.1586262255.1544728045; MoodleSession={moodlesession}' --compressed"
			data = ex(req_url)[2:-1]
			iframe = bs(data, 'html.parser').find('iframe')['src'].split('/')
			if iframe[2] == 'www.youtube.com':
				continue
			iframe = iframe[4]
			# print(iframe, '==========================')
			vid_req = f"curl 'https://player.vimeo.com/video/{iframe}' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Referer: {vidlink}' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,hi;q=0.8' -H 'Cookie: __utma=256147786.1601619963.1500907724.1507815667.1509430014.5; vuid=pl1529248567.2043095762; player='volume=0.8999999999999999'; _gcl_au=1.1.1189656578.1544869498; _ga=GA1.2.1426972584.1544869499; _gid=GA1.2.901729755.1544869499; __qca=P0-1758620115-1544869500465' --compressed"
			vid_data = ex(vid_req)[2:-1]
			# print(vid_data)
			indxs = [m.start() for m in re.finditer('master.json', vid_data)]
			print(len(indxs))
			i1, i2 = xtract_url(vid_data, indxs[0])
			j1, j2 = xtract_url(vid_data, indxs[1])
			print(vid_data[i1: i2 + 1])
			path = f'./{subj}/{topic}/{vidtitle}'
			value = (vid_data[i1: i2 + 1], vid_data[j1: j2 + 1])
			master_json_url, substitute = value
			if os.path.exists(path + '.mp4'):
				continue
			temp = '.'
			for i in path.split('/')[1:-1]:
			    temp += '/' + i
			    if not os.path.exists(temp):
			        os.mkdir(temp)
			base_url = master_json_url[:master_json_url.rfind('/', 0, -26) - 5]

			resp = requests.get(master_json_url)
			# print(resp.status_code)
			if resp.status_code != 200:
			    # print(master_json_url)
			    # print(substitute)
			    print(data[(master_json_url, substitute)])
			    continue
			content = resp.json()



			vt = fetchThread(0, f"Thread-{0}", False, master_json_url, substitute, base_url, resp, content, path)
			at = fetchThread(1, f"Thread-{1}", True, master_json_url, substitute, base_url, resp, content, path)
			vt.start()
			at.start()
			vt.join()
			at.join()
			# d[value] = path
			print()
			print()



		topicindex+=1
	# print(d)
	# f = open(f'./pathlink-{isubj}', 'wb')
	# pickle.dump(d, f)
	# f.close()

'''
dict_keys(['subjects', 'topics', 'videos'])
'''
# string = ''
subjs, topics, videos = data['subjects'], data['topics'], data['videos']
topicindex=0
threads = []
import sys
query = sys.argv[1]
for isubj, (subj, subjlink) in enumerate(subjs):
	if isubj != int(query):
		continue
	print('Downloading data')
	threads.append(myThread(isubj, f"Thread-{isubj}", isubj, subj, subjlink, ts[isubj]) )
	# break
ss = [i.start() for i in threads]
jj = [i.join() for i in threads]
# f=open('all-data.txt', 'w')
# f.write(string)
# f.close()



# req_url = f"curl '{url}' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.9,hi;q=0.8' -H 'Cookie: _ga=GA1.2.151426872.1521890632; _gid=GA1.2.1586262255.1544728045; MoodleSession=nv4e8peepekg414erl1b0272h7' --compressed"

# data = ex(req_url)[2:-1]
# iframe = bs(data, 'html.parser').find('iframe')['src'].split('/')[4]
# # print(iframe)


# vid_req = f"curl 'https://player.vimeo.com/video/{iframe}' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Referer: {url}' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,hi;q=0.8' -H 'Cookie: __utma=256147786.1601619963.1500907724.1507815667.1509430014.5; vuid=pl1529248567.2043095762; player='volume=0.8999999999999999'; _gcl_au=1.1.1189656578.1544869498; _ga=GA1.2.1426972584.1544869499; _gid=GA1.2.901729755.1544869499; __qca=P0-1758620115-1544869500465' --compressed"
# vid_data = ex(vid_req)[2:-1]
# f=open('temp.html', 'w')
# f.write(vid_data)
# f.close()

# # print(vid_data)

# indxs = [m.start() for m in re.finditer('master.json', vid_data)]
# print(indxs)


# i1, i2 = xtract_url(vid_data, indxs[0])
# j1, j2 = xtract_url(vid_data, indxs[1])
# print(vid_data[i1: i2 + 1])
# print(vid_data[j1: j2 + 1])