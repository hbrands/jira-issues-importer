# JIRA issues importer

Python 3.x scripts for importing JIRA issues in XML format into an existing Github project without existing issues

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
* Configure colour scheme for labelling on import
* Import multiple files to help overcome the export limit of 1000 (export multiple files by by using the JIRA key column as a range)
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

* use these scripts at your own risk, no warranties for a correct and successful migration are given
* it's recommended to test your issue migration first with a test project on Github
* input to the import script is the XML export file of your JIRA project, see below
* works with JIRA Cloud, as of March 2019
* your target Github project should already exist with the issue tracker enabled
* there should be no existing issues and pull requests - else the issue id mapping will be incorrect

# Getting started

* clone this repository
* run `pip install -r requirements.txt`
* export the desired JIRA issues of your project (see section below)
* to start the Github import, execute 'python main.py'
* edit the `labelcolourselector.py` if you want to change the logic of how the colours are set on labels
* on startup it will ask for
  * the JIRA XML export file name (use a semi-colon to enter multiple XML paths)
  * the JIRA project name
  * the `<statusCategoryId>` element's `id` attribute that signifies an issue as Done 
  * the Github account name (user or organization)
  * the target Github repository name
  * the Github user and password for authentication
  * the index at which to start from, enter 0 to begin, if you have a failure, enter the index number the import failed at. Entering a number higher than 0 will stop labels from re-importing and milestones will re-match to existing.
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

1. Specify Query criteria, Sort as needed, if you have more than 1000 items use something like eg. `issuekey < PRO-1000 AND issuekey > PRO-2000` to select a range and export each set into separate XML files

1. From results page, click on Export icon at the top right of page

1. Select XML output and save file
