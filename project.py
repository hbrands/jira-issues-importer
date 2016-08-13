#!/usr/bin/env python

from collections import defaultdict
from htmlentitydefs import name2codepoint
import re

class Project:

  def __init__(self, name):
    self.name = name
    self.__project = {'Milestones': defaultdict(int), 'Components': defaultdict(int), 'Labels': defaultdict(int), 'Issues': []}

  def getMilestones(self):
    return self.__project['Milestones']

  def getComponents(self):
    return self.__project['Components']

  def getIssues(self):
    return self.__project['Issues']

  def addItem(self, item):
    itemProject = self.__projectFor(item)
    if itemProject != self.name:
      print('Skipping item ' + item.key.text + ' for project ' + itemProject + ' current project: ' + self.name)
      return
  
    self.appendItemToProject(item)

    # github doesn't want you to assign to any name,
    # must be a github user
    #if item.assignee.get('username') != '-1':
    #  project['Issues'][-1]['assignee'] = item.assignee.get('username')
    self.addMilestone(item)

    self.addLabels(item)

    self.addComments(item)
    self.addRelationships(item)


  def mergeLabelsAndComponents(self):
    self.__project['Components'].update(self.__project['Labels'])
  

  def __projectFor(self, item):
    try:
      result = item.project.get('key')
    except AttributeError:
      result = item.key.text.split('-')[0]
    return result


  def appendItemToProject(self, item):
    try:
      resolved_at = ', resolved ' + item.resolved.text + ''
    except AttributeError:
      resolved_at = ''

    self.__project['Issues'].append({"title": item.title.text[item.title.text.index("]") + 2:len(item.title.text)],
      'key': item.key.text,
      "body": self.htmlentitydecode(item.description.text) + '\n<i>' + item.title.text[0:item.title.text.index("]")+1] + ' created by ' + item.reporter.get('username') + ' at ' + item.created.text + '' + resolved_at + '</i>',
      "labels": [],
      'open': str(item.status.get('id')) not in ('5','6'),
      'comments': [],
      'duplicates': [],
      'is-duplicated-by': [],
      'is-related-to': [],
      'depends-on': [],
      'blocks': []
    })

  def addMilestone(self, item):
    try:
      self.__project['Milestones'][item.fixVersion.text] += 1
      # this prop will be deleted later:
      self.__project['Issues'][-1]['milestone_name'] = item.fixVersion.text 
    except AttributeError:
      pass
  
  def addLabels(self, item):
    try:
      self.__project['Components'][item.component.text] += 1
      self.__project['Issues'][-1]['labels'].append(item.component.text)
    except AttributeError:
      pass
    try:
      for label in item.labels.label:
        self.__project['Labels'][label.text] += 1
        self.__project['Issues'][-1]['labels'].append(label.text)
    except AttributeError:
      pass

  def addComments(self, item):
    try:
      for comment in item.comments.comment:
        self.__project['Issues'][-1]['comments'].append(self.htmlentitydecode(comment.text) +
            '\n<i>' +
            comment.get('author') + ' ' +
            comment.get('created') + '</i>')
    except AttributeError:
      pass

  def addRelationships(self, item):
    try:
      for issuelinktype in item.issuelinks.issuelinktype:
        for outwardlink in issuelinktype.outwardlinks:
          for issuelink in outwardlink.issuelink:
            for issuekey in issuelink.issuekey:
              self.__project['Issues'][-1][outwardlink.get("description").replace(' ', '-')].append(issuekey.text)
    except AttributeError:
      pass
    except KeyError:
          print 'KeyError at ' + item.key.text
    try:
      for issuelinktype in item.issuelinks.issuelinktype:
        for inwardlink in issuelinktype.inwardlinks:
          for issuelink in inwardlink.issuelink:
            for issuekey in issuelink.issuekey:
              self.__project['Issues'][-1][inwardlink.get("description").replace(' ', '-')].append(issuekey.text)
    except AttributeError:
      pass

  def prettify(self):
    def hist(h):
      for key in h.iterkeys():
        print ('%30s(%5d): ' + h[key]*'#') % (key, h[key])
      print

    print self.name + ':\n  Milestones:'
    hist(self.__project['Milestones'])
    print '  Components:'
    hist(self.__project['Components'])
    print '  Labels:'
    hist(self.__project['Labels'])
    print

  def htmlentitydecode(self, s):
    if s is None: return ''
    s = s.replace(' '*8, '')
    return re.sub('&(%s);' % '|'.join(name2codepoint), 
        lambda m: unichr(name2codepoint[m.group(1)]), s)
    
