import getpass
from collections import namedtuple
from lxml import objectify
from project import Project
from importer import Importer
from labelcolourselector import LabelColourSelector


def read_xml_sourcefile(file_name):
    all_text = open(file_name).read()
    return objectify.fromstring(all_text)


# input('Path to JIRA XML query file: ')
file_name = 'C:\\Users\\dougl\\Desktop\\SearchRequest.xml'
all_xml = read_xml_sourcefile(file_name)

jira_proj = input('JIRA project name to use: ')
jira_done_id = input('JIRA Done statusCategory ID: ')
us = input('GitHub account name: ')
repo = input('GitHub project name: ')
user = input('GitHub username: ')
pw = getpass.getpass('GitHub password: ')

Options = namedtuple("Options", "user passwd account repo")
opts = Options(user=user, passwd=pw, account=us, repo=repo)

project = Project(jira_proj, jira_done_id)

for item in all_xml.channel.item:
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
importer.import_labels(colourSelector)
importer.import_issues()
importer.post_process_comments()
