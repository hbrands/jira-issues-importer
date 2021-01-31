# JIRA issues importer

*Python 3.x* scripts for importing JIRA issues in XML format into an existing Github project without existing issues.  For Python 2.x, see https://github.com/hbrands/jira-issues-importer.

# Features

* Import
  * JIRA milestones as Github milestones
  * JIRA labels as Github labels
  * JIRA components as Github labels
  * JIRA issues as Github issues where
    * Issue ids are mapped one by one, e.g. PROJECT-1 becomes GH-1 and PROJECT-4711 becomes GH-4711
    * Both issue label and component assignments are mapped to Github labels
    * Issue relationships like "depends on", "blocks" or "duplicates" are mapped to special Github comments
    * Issue timestamps such as creation, close or update date are considered
    * Issue states (open or closed) are considered
    * Issue comments are mapped to Github comments
      * JIRA issue references in normal and relationship comments are replaced by references to the Github issue id    
  * Multiple files to help overcome the export limit of 1000 (export multiple files by using the JIRA key column as a range)    
* Configure colour scheme for labelling on import

# Caveats
 * This project does not try to map JIRA users to Github users
   * The Github user which performs the import will appear as issue creator, the original JIRA issue reporter is noted in the first comment
   * The Github user which performs the import will also appear as comment creator, as the Github API doesn't support that (yet),
     the original JIRA commentator is noted in the comment text

# Assumptions and prerequisites

* Use these scripts at your own risk, no warranties for a correct and successful migration are given
* It's recommended to test your issue migration first with a test project on Github
* Input to the import script is the XML export file of your JIRA project, see below
* Works with JIRA Cloud, as of March 2019
* Your target Github project should already exist with the issue tracker enabled
* There should be no existing issues and pull requests - else the issue id mapping will be incorrect

# Getting started

* Clone this repository
* Run `pip install -r requirements.txt`
* Export the desired JIRA issues of your project (see section below)
* Edit the `labelcolourselector.py` if you want to change the logic of how the colours are set on labels
* Copy `config.sample.init` as `config.ini`
* Fill out your config values in config.ini.  Note that this file is Git ignored.
* Start the Github import by executing 'python main.py'
* The import process will then
  * Read the JIRA XML export file and create an in-memory project representation of the xml file contents
  * Import the milestones with the regular [Github Milestone API](https://developer.github.com/v3/issues/milestones/)
  * Import the labels with the regular [Github Label API](https://developer.github.com/v3/issues/labels/)
  * Import the issues with comments with the [Github Import API](https://gist.github.com/jonmagic/5282384165e0f86ef105)
    * References to issues in the comments are replaced with placeholders in this step
    * The used import API will not run into abuse rate limits in contrast to the normal [Github Issues API](https://developer.github.com/v3/issues/)
  * Post-process all comments to replace the issue reference placeholders with the real Github issue ids using the [Github Comment API](https://developer.github.com/v3/issues/comments/)

# Export JIRA issues

1. Navigate to Issue search page for project. Issues --> Search for Issues

1. Select project you are interested in

1. Specify Query criteria, Sort as needed, if you have more than 1000 items use something like eg. `issuekey < PRO-1000 AND issuekey > PRO-2000` to select a range and export each set into separate XML files

1. From results page, click on Export icon at the top right of page

1. Select XML output and save file
