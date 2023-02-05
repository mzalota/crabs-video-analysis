import urllib2

#filedata = urllib2.urlopen('https://sonar.ocean.ru/seafhttp/files/ebc4f335/u002D7c60/u002D4eef/u002Da1bb/u002D04a638cd3d42/V20200901_214516_001.srt')


class Runner:
	def run(self):
		files= list()

		
		#2020.09.16_6922
		files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_194953_20200916_195355.avi&dl=1")
		#files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_195355_20200916_195753.avi&dl=1")
		
		              
		#files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_195355_20200916_200151.avi&dl=1")
		files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_195355_20200916_200549.avi&dl=1")
		files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_195355_20200916_200947.avi&dl=1")
		files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_195355_20200916_201345.avi&dl=1")
		files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_195355_20200916_201743.avi&dl=1")
		files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_195355_20200916_202143.avi&dl=1")
		files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_195355_20200916_202543.avi&dl=1")
		files.append("https://sonar.ocean.ru/d/fbc1009733144a16bb66/files/?p=%2F2020.09.16%20%D0%A1%D1%82%206922%2FR_20200916_195355_20200916_202941.avi&dl=1")
		
		for file in files:
			self.download_file(file)
		
	def filename_from_url(self, url):
		position = url.find('R_2020')		
		end_part_of_url = url[position:]
		position_end = end_part_of_url.find('&')
		filename = end_part_of_url[0:position_end]
		return filename
		
	def download_file(self, url):
		
		print("URL: " + url)

		filename = self.filename_from_url(url)

		print("filename: " + filename)

		# New lines begin here
		http_logger = urllib2.HTTPHandler(debuglevel = 1)
		opener = urllib2.build_opener(http_logger) # put your other handlers here too!
		urllib2.install_opener(opener)
		# End of new lines
		
		filedata = urllib2.urlopen(url)
		print("Content Length")
		print(filedata.headers.get("Content-Length"))

		CHUNK = 1024 * 1024
		with open(filename, 'wb') as f:
			while True:
				chunk = filedata.read(CHUNK)
				if not chunk:
					break
				f.write(chunk)

		print("downloaded file: " + filename)

	def read_file_as_whole(self):
		datatowrite = filedata.read()
		with open(filename, 'wb') as f:
			f.write(datatowrite)
		
runner = Runner()
runner.run()
			
print("done3")
