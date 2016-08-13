#!/usr/bin/env python
import getpass
from collections import namedtuple
from lxml import objectify
import project
import importer

'''
>>> p = re.compile('(GLAZEDLISTS-)(\d+)')
>>> p.sub(r'#\2', 'This is GLAZEDLISTS-2 and GLAZEDLISTS-567.')
'This is #2 and #567.'
'''
def readXmlSourceFile(file_name):
  all_text = open(file_name).read()
  return objectify.fromstring(all_text)

file_name = raw_input('Path to JIRA XML query file: ')
all_xml = readXmlSourceFile(file_name);

#jiraProj = raw_input('JIRA project name to use: ')
#us = raw_input('GitHub account name: ')
#repo = raw_input('GitHub project name: ')
#user = raw_input('GitHub username: ')
#pw = getpass.getpass('GitHub password: ')

jiraProj = 'GLAZEDLISTS'
us = 'hbrands'
repo = 'jira-import-test'
user = 'hbrands'
pw = 'hb_buHtiG6'

Options = namedtuple("Options", "user passwd account repo")
opts = Options(user = user, passwd = pw, account = us, repo=repo)

project = project.Project(jiraProj)

for item in all_xml.channel.item:
  project.addItem(item)

print
print 'Components will be combined with labels as github labels...'
project.mergeLabelsAndComponents()
project.prettify()

'''
Steps:
  1. Create any milestones
  2. Create any labels
  3. Create each issue, linking them to milestones and labels
  3.1: Update status for new issue if closed
  4: Create all the comments for each issue
'''
importer = importer.Importer(opts, project)

importer.importMilestones()
importer.importLabels()
importer.importIssues()
importer.importRelationships()

