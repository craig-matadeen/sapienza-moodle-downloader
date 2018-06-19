# sapienza-moodle-downloader

A script to download your moodle course resources from sapienza's moodle for courses that you are currently enrolled in.

The moodler.py script downloads all the files posted in the course page of all the courses you are enrolled to.

Set the following in the file config.conf before running the script:

	url [String] : This is the login page for Sapienza, it is not necessary to change this.
	username [String] : Moodle Username
	password [String] : Moodle Password
	save_location [String] : The path to the directory where the files are to be stored.

The script finds only courses in your course list. So make sure that you check https://elearning2.uniroma1.it/my fo a list of your courses.

REQUIREMENTS:

	Python 3
	urllib
	requests
	time
	re
	os
	BeautifulSoup
	tqdm
	configparser


Special thanks to:

	Vinay Chandra	- https://github.com/vinaychandra/Moodle-Downloader
	Daniel Vogt		- https://github.com/C0D3D3V/Moodle-Crawler

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
