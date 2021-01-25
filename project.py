from collections import defaultdict
from html.entities import name2codepoint
from dateutil.parser import parse
import re


class Project:

    def __init__(self, name, doneStatusCategoryId):
        self.name = name
        self.doneStatusCategoryId = doneStatusCategoryId
        self._project = {'Milestones': defaultdict(int), 'Components': defaultdict(
            int), 'Labels': defaultdict(int), 'Types': defaultdict(int), 'Issues': []}

    def get_milestones(self):
        return self._project['Milestones']

    def get_components(self):
        return self._project['Components']

    def get_issues(self):
        return self._project['Issues']

    def get_types(self):
        return self._project['Types']

    def get_all_labels(self):
        merge = self._project['Components'].copy()
        merge.update(self._project['Labels'])
        merge.update(self._project['Types'])
        return merge

    def add_item(self, item):
        itemProject = self._projectFor(item)
        if itemProject != self.name:
            print('Skipping item ' + item.key.text + ' for project ' +
                  itemProject + ' current project: ' + self.name)
            return

        self._append_item_to_project(item)

        self._add_milestone(item)

        self._add_labels(item)

        self._add_comments(item)

        self._add_relationships(item)

    def prettify(self):
        def hist(h):
            for key in h.keys():
                print(('%30s (%5d): ' + h[key] * '#') % (key, h[key]))
            print

        print(self.name + ':\n')
        print('-------------------------------------------------------')
        print('  Milestones:')
        hist(self._project['Milestones'])
        print('-------------------------------------------------------')
        print('  Types:')
        hist(self._project['Types'])
        print('-------------------------------------------------------')
        print('  Components:')
        hist(self._project['Components'])
        print('-------------------------------------------------------')
        print('  Labels:')
        hist(self._project['Labels'])
        print('-------------------------------------------------------')
        print
        print('Total Issues to Import: %d' % len(self._project['Issues']))

    def _projectFor(self, item):
        try:
            result = item.project.get('key')
        except AttributeError:
            result = item.key.text.split('-')[0]
        return result

    def _append_item_to_project(self, item):
        # todo assignee
        closed = str(item.statusCategory.get('id')) == self.doneStatusCategoryId
        closed_at = ''
        if closed:
            try:
                closed_at = self._convert_to_iso(item.resolved.text)
            except AttributeError:
                pass

        self._project['Issues'].append({'title': item.title.text[item.title.text.index("]") + 2:len(item.title.text)],
                                        'key': item.key.text,
                                        'body': self._htmlentitydecode(item.description.text) + '\n<i>' + item.title.text[0:item.title.text.index("]") + 1] + ' created by ' + item.reporter.get('username') + '</i>',
                                        'created_at': self._convert_to_iso(item.created.text),
                                        'closed_at': closed_at,
                                        'updated_at': self._convert_to_iso(item.updated.text),
                                        'closed': closed,
                                        'labels': [],
                                        'comments': [],
                                        'duplicates': [],
                                        'is-duplicated-by': [],
                                        'is-related-to': [],
                                        'depends-on': [],
                                        'blocks': []
                                        })
        if not self._project['Issues'][-1]['closed_at']:
            del self._project['Issues'][-1]['closed_at']

    def _convert_to_iso(self, timestamp):
        dt = parse(timestamp)
        return dt.isoformat()

    def _add_milestone(self, item):
        try:
            self._project['Milestones'][item.fixVersion.text] += 1
            # this prop will be deleted later:
            self._project['Issues'][-1]['milestone_name'] = item.fixVersion.text
        except AttributeError:
            pass

    def _add_labels(self, item):
        try:
            self._project['Components'][item.component.text] += 1
            self._project['Issues'][-1]['labels'].append(item.component.text)
        except AttributeError:
            pass

        try:
            for label in item.labels.label:
                self._project['Labels'][label.text] += 1
                self._project['Issues'][-1]['labels'].append(label.text)
        except AttributeError:
            pass

        try:
            self._project['Types'][item.type.text] += 1
            self._project['Issues'][-1]['labels'].append(item.type.text)
        except AttributeError:
            pass

    def _add_comments(self, item):
        try:
            for comment in item.comments.comment:
                self._project['Issues'][-1]['comments'].append(
                    {"created_at": self._convert_to_iso(comment.get('created')),
                     "body": self._htmlentitydecode(comment.text) + '\n<i>by ' + comment.get('author') + '</i>'
                     })
        except AttributeError:
            pass

    def _add_relationships(self, item):
        try:
            for issuelinktype in item.issuelinks.issuelinktype:
                for outwardlink in issuelinktype.outwardlinks:
                    for issuelink in outwardlink.issuelink:
                        for issuekey in issuelink.issuekey:
                            self._project['Issues'][-1][outwardlink.get(
                                "description").replace(' ', '-')].append(issuekey.text)
        except AttributeError:
            pass
        except KeyError:
            print('KeyError at ' + item.key.text)
        try:
            for issuelinktype in item.issuelinks.issuelinktype:
                for inwardlink in issuelinktype.inwardlinks:
                    for issuelink in inwardlink.issuelink:
                        for issuekey in issuelink.issuekey:
                            self._project['Issues'][-1][inwardlink.get(
                                "description").replace(' ', '-')].append(issuekey.text)
        except AttributeError:
            pass
        except KeyError:
            print('KeyError at ' + item.key.text)

    def _htmlentitydecode(self, s):
        if s is None:
            return ''
        s = s.replace(' ' * 8, '')
        return re.sub('&(%s);' % '|'.join(name2codepoint),
                      lambda m: chr(name2codepoint[m.group(1)]), s)
