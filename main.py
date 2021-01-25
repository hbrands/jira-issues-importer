import getpass
import configparser
import os.path
from os import path
from collections import namedtuple
from lxml import objectify
from project import Project
from importer import Importer
from labelcolourselector import LabelColourSelector

def read_xml_sourcefile(file_names):
    files = list()
    for file_name in file_names.split(';'):
        all_text = open(file_name).read()
        files.append(objectify.fromstring(all_text))

    return files


config = configparser.ConfigParser()
if not path.exists('config.ini'):
    print('ERROR: No config.ini found in this directory')
    exit()

config.read('config.ini')

jira_project = config['Settings']['jira_project']
jira_done_id = config['Settings']['jira_done_id']
user_or_org = config['Settings']['user_or_org']
repo_name = config['Settings']['repo_name']
username = config['Settings']['username']
password = config['Settings']['password']
start_from_issue = config['Settings']['start_from_issue']
start_from_issue = 0 if (start_from_issue=='') else start_from_issue

file_names = config['Settings']['file_names']
all_xml_files = read_xml_sourcefile(file_names)

Options = namedtuple("Options", "user passwd account repo")
opts = Options(user=username, passwd=password, account=user_or_org, repo=repo_name)

project = Project(jira_project, jira_done_id)

for f in all_xml_files:
    for item in f.channel.item:
        project.add_item(item)

project.prettify()

input('Press any key to begin...')

'''
Steps:
  1. Create any milestones
  2. Create any labels
  3. Create each issue with comments, linking them to milestones and labels
  4: Post-process all comments to replace issue id placeholders with the real ones
'''
importer = Importer(opts, project)
colourSelector = LabelColourSelector(project)

importer.import_milestones()

if int(start_from_issue) == 0:
    importer.import_labels(colourSelector)

importer.import_issues(int(start_from_issue))
importer.post_process_comments()
