#!/usr/bin/env python

import time, string, sys, threading, re, urllib, urllib2
import xml.etree.ElementTree as ET
from sys import stdout
from datetime import datetime
from datetime import date

_config = None

dayname = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Unknown']
dayshort = ['Mo', 'Tu', 'We', 'Tr', 'Fr', 'Sa', 'Su', 'Uk']

def Main():
	favorites = Call('User_Favorites', {
		'accountid': _config.find('settings/accounts/account[@name="TheTVDB"]/id').text
	})

	serieslist = {
		'Airing': {},
		'Hiatus': {},
		'Ended': {},
		'Unknown': {}
	}

	dtStart = datetime.today()

	ids = []
	for favorite in favorites.findall('Series'):
		ids.append(favorite.text)
		t = threading.Thread(target=GetSeriesDetails, args = (ids,serieslist,favorite.text))
		t.daemon = True
		t.start()
	
	print 'Fetching series data...'

	while len(ids) != 0:
		print '|' * len(ids)

		time.sleep(1)

	dtEnd = datetime.today()

	print 'Done.\n\n'

	for statusname, status in serieslist.iteritems():
		if len(status) > 0:
			print statusname
			for dayofweek, day in status.iteritems():
				if statusname == 'Airing' and dayofweek != 0 and dayofweek == datetime.now().weekday():
					print

				if statusname == 'Airing':
					day = sorted(day, key=lambda k: k['Name']) 
				else:
					day = sorted(day, key=lambda k: k['Airs'] + k['Name']) 

				for series in day:
					if dayofweek < 7:
						print '\t{0:40}{1:3}{2:10} (S{3:02}E{4:02})'.format(series['Name'], series['Weekday'], series['Airs'], int(series['Season']), int(series['Episode']))
					else:
						print '\t{0:40}'.format(series['Name'])

			print

	print '\nElapsed time: %s\n' % (dtEnd - dtStart)

def GetSeriesDetails(ids, serieslist, id):
	list = None
	found = False

	try:
		series = Call('series/%s/all' % (id))
		for episode in series.findall('Episode'):
			sAirs = episode.find('FirstAired').text
			if sAirs != None:
				airs = datetime.strptime(sAirs, '%Y-%m-%d')
				if airs.date() >= datetime.now().date():
					status = series.find('Series/Status').text
					if status == 'Continuing':
						if (airs - datetime.now()).days < 6:
							list = serieslist['Airing']
							weekday = airs.weekday()
						else:
							list = serieslist['Hiatus']
							weekday = 0
					elif status == 'Ended':
						list = serieslist['Ended']
						weekday = 0
					else:
						continue

					if weekday not in list:
						list[weekday] = []
					
					list[weekday].append({
						'Name': FormatName(series.find('Series/SeriesName').text),
						'Airs': episode.find('FirstAired').text,
						'Weekday': dayshort[airs.weekday()],
						'Season': episode.find('Combined_season').text,
						'Episode': episode.find('Combined_episodenumber').text
					})
					
					found = True
					break

		if found == False:
			if 7 not in serieslist['Unknown']:
				serieslist['Unknown'][7] = []

			serieslist['Unknown'][7].append({
				'Name': FormatName(series.find('Series/SeriesName').text),
				'Airs': '??',
				'Season': '??',
				'Episode': '??'
			})
			
	except Exception as e:
		print e
		ineedtofigureouthowtohaveanempytblock = 1

	ids.remove(id)

def LoadConfig(file):
	global _config
	tree = ET.parse(file)
	_config = tree.getroot()

def Call(endpoint, params = {}):
	params = urllib.urlencode(params)

	override = _config.find('apis/api[@name="TheTVDB"]/endpointoverrides/endpoint[@name="%s"]' % (endpoint))
	if override != None:
		url = '%s/%s?%s' % (
			_config.find('apis/api[@name="TheTVDB"]/url').text,
			override.text,
			params
		)
	else:
		url = '%s/%s/%s/?%s' % (
			_config.find('apis/api[@name="TheTVDB"]/url').text,
			_config.find('apis/api[@name="TheTVDB"]/key').text,
			endpoint,
			params
		)

	stream = urllib2.urlopen(url)
	sResponse = stream.read();
	response = ET.fromstring(sResponse)

	return response

def FormatName(name):
	return re.sub(_config.find('settings/regex/sanitizename').text, '', name).strip()

if len(sys.argv) != 2:
	print '\tUsage: ' + sys.argv[0] + ' config.xml'
else:
	LoadConfig(sys.argv[1])
	Main()
