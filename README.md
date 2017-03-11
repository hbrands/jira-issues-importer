# JIRA issues importer

Python 2.x scripts for importing JIRA issues in XML format into an existing Github project without existing issues

# Background

Due to the java.net close-down in April 2017 there is a need to move projects from the java.net forge to Github.
Part of the transition is the migration of java.net JIRA issues to the Github issue tracker.
Googling for solutions for this issue migration I came across these "dirty" migration scripts from the following GISTs:

* https://gist.github.com/Jach/1537770
* https://gist.github.com/mkurz/20293e306b1c6fefff7c

I took these as a starting point for this project. I restructured the code and added some more features.

# Features

* Import JIRA milestones as Github milestones
* Import JIRA labels as Github labels
* Import JIRA components as Github labels
* Import JIRA issues as Github issues where
  * issue ids are mapped one by one, e.g. PROJECT-1 becomes GH-1 and PROJECT-4711 becomes GH-4711
  * both issue label and component assignments are mapped to Github labels
  * issue relationships like "depends on", "blocks" or "duplicates" are mapped to special Github comments
  * issue timestamps such as creation, close or update date are considered
  * issue states (open or closed) are considered
  * issue comments are mapped to Github comments
    * JIRA issue references in normal and relationship comments are replaced by references to the Github issue id  
 
# Caveats 
 * this project does not try to map JIRA users to Github users
   * the Github user which performs the import will appear as issue creator, the original JIRA issue reporter is noted in the first comment 
   * the Github user which performs the import will also appear as comment creator, as the Github API doesn't support that (yet),
     the original JIRA commentator is noted in the comment text

# Assumptions and prerequisites

* the migration scripts are written in Python 2.x. In particular, they were tested with Python 2.7 on Windows
* python modules used are getpass, collections, lxml, htmlentitydefs, dateutil.parser, re, requests, random, time
* use these scripts at your own risk, no warranties for a correct and successful migration are given
* it's recommended to test your issue migration first with a test project on Github
* input to the import script is the XML export file of your JIRA project, see below
* the import/export was tested with the current java.net JIRA (v6.2.3), other versions might produce different XML export content
* your target Github project should already exist with the issue tracker enabled, but without any existing issues

# Getting started

* ensure you have installed the proper Python environment with the needed modules
* clone this repository or copy the three Python files main.py, project.py and importer.py to your system
* export the desired JIRA issues of your project (see section below) 
* to start the Github import, execute 'python main.py'
* on startup it will ask for
  * the JIRA XML export file name
  * the JIRA project name
  * the Github account name (user or organization)
  * the target Github repository name
  * the Github user and password for authentication
* the import process will then
  * read the JIRA XML export file and create an in-memory project representation of the xml file contents
  * import the milestones with the regular [Github Milestone API](https://developer.github.com/v3/issues/milestones/)
  * import the labels with the regular [Github Label API](https://developer.github.com/v3/issues/labels/)
  * import the issues with comments with the [Github Import API](https://gist.github.com/jonmagic/5282384165e0f86ef105)
    * references to issues in the comments are replaced with placeholders in this step
    * the used import API will not run into abuse rate limits in contrast to the normal [Github Issues API](https://developer.github.com/v3/issues/)
  * post-process all comments to replace the issue reference placeholders with the real Github issue ids using the [Github Comment API](https://developer.github.com/v3/issues/comments/)

# Export JIRA issues

1. Navigate to Issue search page for project. Issues --> Search for Issues

1. Select project you are interested in

1. Specify Query criteria, Sort as needed

1. From results page, click on Export icon at the top right of page

1. Select XML output and save file
