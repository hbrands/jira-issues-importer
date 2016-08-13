from collections import namedtuple
import project
import human_curl as hurl
import json
import random
import time
import re
import project

DEFAULT_TIME_OUT = 60.0

class Importer:

  def __init__(self, options, project):
    self.options = options
    self.project = project
    self.github_url = 'https://api.github.com/repos/' + self.options.account + '/' + self.options.repo
    
  def importMilestones(self):
    print 'Making milestones...', self.github_url + '/milestones'
    print
    for mkey in self.project.getMilestones().iterkeys():
        data = {'title': mkey}
        r = hurl.post(self.github_url + '/milestones', json.dumps(data),
            auth=(self.options.user, self.options.passwd), timeout=DEFAULT_TIME_OUT)
        # overwrite histogram data with the actual milestone id now
        if r.status_code == 201:
          content = json.loads(r.content)
          self.project.getMilestones()[mkey] = content['number']
          print mkey
        else:
          if r.status_code == 422: # already exists
            ms = json.loads(hurl.get(self.github_url + '/milestones?state=open').content)
            ms += json.loads(hurl.get(self.github_url + '/milestones?state=closed').content)
            f = False
            for m in ms:
              if m['title'] == mkey:
                self.project.getMilestones()[mkey] = m['number']
                print mkey, 'found'
                f = True
                break
            if not f:
              exit('Could not find milestone: ' + mkey)
          else:
            print 'Failure!', r.status_code, r.content, r.headers
    
  
  def importLabels(self):
    for lkey in self.project.getComponents().iterkeys():
      data = {'name': lkey, 'color': '%.6x' % random.randint(0, 0xffffff)}
      r = hurl.post(self.github_url + '/labels', json.dumps(data),
                  auth=(self.options.user, self.options.passwd), timeout=DEFAULT_TIME_OUT)
      if r.status_code == 201:
        print lkey
      else:
        print 'Failure!', r.status_code, r.content, r.headers


  def addcomment(self, number, comment):
    time.sleep(3)
    r3 = hurl.post(self.github_url + '/issues/' + number + '/comments',
    json.dumps({'body': comment}), auth=(self.options.user, self.options.passwd),
                   headers={'Accept': 'application/vnd.github.beta.html+json'}, timeout=DEFAULT_TIME_OUT)
    if r3.status_code == 201:
      print 'Added comment',
    else:
      print 'Failed to add comment!', r3.status_code, r3.content, r3.headers


  def importIssues(self):
    for issue in self.project.getIssues():
        time.sleep(2)
        if 'milestone_name' in issue:
          issue['milestone'] = self.project.getMilestones()[ issue['milestone_name'] ]
          del issue['milestone_name']
        op = issue['open']
        del issue['open']
        comments = issue['comments']
        del issue['comments']

        print issue['key']
        r = hurl.post(self.github_url + '/issues', json.dumps(issue), auth=(self.options.user, self.options.passwd),
            headers={'Accept': 'application/vnd.github.beta.html+json'}, timeout=DEFAULT_TIME_OUT)

        if r.status_code == 201:
          content = json.loads(r.content)
          print 'Created issue:', issue['title']
          if op == False:
            # this is supposed to be hurl.method.patch() but it fails
            r2 = hurl.post(self.github_url + '/issues/' + str(content['number']),
                json.dumps({'state': 'closed'}), auth=(self.options.user, self.options.passwd), timeout=DEFAULT_TIME_OUT)
            if r2.status_code == 200:
              print 'Closed issue'
            else:
              print 'Failed to close issue!', r2.status_code, r2.content, r2.headers

          issue['githubid'] = str(content['number'])
          print 'githubid: ' + issue['githubid']

          for comment in comments:
            self.addcomment(str(content['number']), comment)

          print
        else:
          print "FFFFFFFFFFFFFFFuuuuuuuuuuuu, couldn't make issue:", issue
          print '*'*10
          print r.status_code, r.content, r.headers
        print

  def importRelationships(self):
    for issue in self.project.getIssues():
        duplicates = issue['duplicates']
        is_duplicated_by = issue['is-duplicated-by']
        relates_to = issue['is-related-to']
        depends_on = issue['depends-on']
        blocks = issue['blocks']

        for duplicate_item in duplicates:
          self.addcomment(issue['githubid'], "Duplicates: " + self.resolve_github_id(duplicate_item))

        for is_duplicated_by_item in is_duplicated_by:
          self.addcomment(issue['githubid'], "Is duplicated by: " + self.resolve_github_id(is_duplicated_by_item))

        for relates_to_item in relates_to:
          self.addcomment(issue['githubid'], "Is related to: " + self.resolve_github_id(relates_to_item))

        for depends_on_item in depends_on:
          self.addcomment(issue['githubid'], "Depends on: " + self.resolve_github_id(depends_on_item))

        for blocks_item in blocks:
          self.addcomment(issue['githubid'], "Blocks: " + self.resolve_github_id(blocks_item))

  def resolve_github_id(self, jiraid):
    print "Resolve " + jiraid + "\n"
    githubid = ''
    for issue in self.project.getIssues():
      if issue['key'] == jiraid:
        githubid = issue['githubid']
        break
    if githubid == '':
      print "Can not resolve " + jiraid + "\n"
    else:
      return "#" + githubid
