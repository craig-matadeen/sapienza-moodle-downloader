"""
    Copyright 2018 Craig Steform Matadeen

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import urllib.parse
import requests
import time
import re
import os
import os.path as op
from bs4 import BeautifulSoup
from tqdm import tqdm
from configparser import ConfigParser

config = ConfigParser()
config.read('config.conf') # read config file;

loginurl = config.get('login_url', 'url') # get login url from config file;
username = config.get('credentials', 'username') # get username from config file;
password = config.get('credentials', 'password') # get password from config file;
save_location = config.get('directory', 'save_location') # get download files save location from config file;

payload = {'username': username, 'password': password}

def is_resource(url):
    """
    :param url: url to check;
    :return: return boolean;

    This function checks if a url is a downloadable resource. This is defined by the list of resources;
    """
    if url:
            resources = ['mod/resource', 'mod/assign', 'pluginfile']

            for resource in resources:
                if resource in url:
                    return True

def download_file(session, url, chunksize_bytes=1024, download_path='', file_number=''):
    """
    :param session: reusable session variable;
    :param url: resource url;
    :param chunksize_bytes: downloadable chunck size;
    :param download_path: path to save the download file;
    :param file_number: this is the number of the file with regards to the current section being downloaded; numbers may not be
                        contiguous as this number is just a way to keep the files sorted by their order on the course page;
    :return: file saved path;

    This function downloads a link resource if the passed in url is not an html page;
    If the page is an html page it will return all resource links from the page;
    """

    response = session.get(url, stream=True)

    if response.headers['Content-Type'].split(';')[0] == 'text/html': # check if page is html or resource;
        # if page is html get all resource links from the page;
        contents = response.content

        soup = BeautifulSoup(contents, 'lxml')
        region_main = soup.select_one('#region-main')

        links = []
        if region_main:
            links = [{'link_number': file_number, 'link': link.get('href')} for link in region_main.find_all('a') if is_resource(link.get('href'))]
        return {'status': False, "value": links} # return all resource links found on the page;
    else:
        # if page is resource page then download resource;
        os.makedirs(op.normpath(download_path), exist_ok=True) # create download directory;
        response_url = urllib.parse.unquote(response.url) # decode resource url;
        filename = clean_string(response_url.split('/')[-1].split('?')[0]) # get filename and extension from url;
        name, ext = op.splitext(filename) # separate file name and extension from filename;
        if not ext: # set non-extension files to text;
            ext = '.txt'
        filename = file_number + ' - ' + name + ext # generate download file name;
        file_path = op.normpath(op.join(download_path, filename)) # generate file save path;
        if op.exists(file_path): # check if the file is already downloaded;
            return {'status': True, "value": "file already downloaded at: {0}".format(file_path)}
        else:
            with open(file_path, 'wb') as file:
                if 'Content-Length' in response.headers: # get size of file;
                    filesize = int(response.headers['Content-Length'])
                else:
                    filesize = 0 # for files with no content length in header set value to 0;
                progress_bar = tqdm(unit="B", total=filesize, unit_scale=True) # create progress bar for file download;
                for chunk in response.iter_content(chunk_size=chunksize_bytes): # save each chunk of the file;
                    if chunk: # filter out keep-alive new chunks;
                        progress_bar.update(len(chunk)) # update progress bar;
                        file.write(chunk)
    return {'status': True, "value": file_path}

def clean_string(string):
    """
    :param string: this is the string to be cleaned;
    :return: cleaned string;

    This function removed unwanted characters from a string and formats it;
    """
    return re.sub('[^0-9A-Za-z\.&]+', '_', string.lower())

with requests.Session() as session: # create session;
    post = session.post(url=loginurl, data=payload) # open session to login page with credentials;
    contents = post.content # get session data;

    if b'My courses' not in contents: # if 'My courses' is not on the page then login failed;
        raise ValueError("Cannot Log In")
    else:
        print("Logged In")

        soup = BeautifulSoup(contents, 'lxml') # parse session data;

        courses = {}
        for course in soup.select(".course_title"): # get all courses from the courses page;
            courses[clean_string(course.find('a').get("title"))] = {'link': course.find('a').get("href")}

        for course in courses: # get resource links from each individual course page;
            response = session.get(courses[course]['link'])
            contents = response.content

            soup = BeautifulSoup(contents, 'lxml')
            course_main = soup.select_one('#region-main') # get main region of page;

            topics = course_main.select('.content') # get all sections in main region;

            sections = {}
            section_number = 0
            for topic in topics:
                sectionname = topic.select_one('.sectionname')
                if sectionname: # get all links in each section;
                    links = [link.get('href') for link in topic.find_all('a') if is_resource(link.get('href'))]
                    if links:
                        numbered_links = [{'link_number': str(link_number) , 'link': link} for link_number, link in enumerate(links)]
                        sections[str(section_number) + ' - ' + clean_string(sectionname.text)] = numbered_links
                        section_number += 1
            courses[course]['sections'] = sections # add all course sections to courses;
            time.sleep(2)  # throttle requests, sleep for 2 seconds between requests;

        downloaded_links = set()
        for course in courses: # download all files for each set of course's links;
            for section in courses[course]['sections']:
                section_path = op.join(save_location, course, section)
                print('downloading section: {0}'.format(section))
                download_links = courses[course]['sections'][section]
                for numbered_link in download_links:
                    if numbered_link['link'] not in downloaded_links:
                        # download resource at link;
                        downloaded = download_file(session=session, url=numbered_link['link'], download_path=section_path, file_number=numbered_link['link_number'])
                        if downloaded['status']: # check if file was downloaded;
                            print(downloaded['value'])
                        else:
                            download_links += downloaded['value'] # add new links to list of links since page is an html page;
                        downloaded_links.add(numbered_link['link'])
                        time.sleep(2) # throttle requests, sleep for 2 seconds between requests;