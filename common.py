import csv
import json
import re
from distutils.util import strtobool

csv.field_size_limit(100000000)

APACHE_ISSUE_REGEX = re.compile(r'^\[?([\dA-Z]+-\d+)\]?')

class Commit:
    def __init__(self, hash, merge, author, date, msg, files):
        self.hash = hash
        self.merge = merge
        self.author = author
        self.date = date
        self.msg = msg
        self.files = files

    def loc_added(self):
        return sum(f.additions for f in self.files)

    def loc_removed(self):
        return sum(f.deletions for f in self.files)


class FileLine:
    def __init__(self, filename, additions, deletions):
        self.filename = filename
        self.additions = additions
        self.deletions = deletions


class Sample:
    def __init__(self, hash, msg, n_files, loc_added, loc_removed, issue_id, is_bug):
        self.hash = hash
        self.msg = msg
        self.n_files = n_files
        self.loc_added = loc_added
        self.loc_removed = loc_removed
        self.issue_id = issue_id
        self.is_bug = is_bug

    def __iter__(self):
        yield self.hash
        yield self.msg
        yield self.n_files
        yield self.loc_added
        yield self.loc_removed
        yield self.issue_id
        yield self.is_bug


def get_apache_issue_id(text):
    match = APACHE_ISSUE_REGEX.match(text)
    if match is None:
        return None
    return match.group(1)


def to_commit_dict(commit):
    return dict([
        ('hash', commit.hash),
        ('merge', commit.merge),
        ('author', commit.author),
        ('date', commit.date),
        ('msg', commit.msg),
        ('files', [f.__dict__ for f in commit.files])
    ])


def from_commit_dict(commit_dict):
    c = commit_dict
    return Commit(
        c['hash'],
        c['merge'],
        c['author'],
        c['date'],
        c['msg'],
        [FileLine(
            f['filename'],
            f['additions'],
            f['deletions'])
            for f in c['files']])


def to_commits_json(commits):
    return json.dumps([to_commit_dict(c) for c in commits], indent=4)


def from_commits_json(text):
    return [from_commit_dict(c) for c in json.loads(text)]


def write_commit_json(commits, filename):
    with open(filename, 'w', encoding='UTF-8') as file:
        file.write(to_commits_json(commits))


def read_commit_json(filename):
    with open(filename, 'r', encoding='UTF-8') as file:
        return from_commits_json(file.read())


def read_issue_csv(filename):
    with open(filename, 'r', newline='', encoding='UTF-8') as csv_file:
        reader = csv.reader(csv_file)
        issue_cache = {}
        for row in reader:
            if len(row) == 2:
                try:
                    v = strtobool(row[1])
                    v = bool(v)
                except ValueError:
                    v = None
                issue_cache[row[0]] = v
        return issue_cache


def write_issue_csv(issue_cache, filename):
    with open(filename, 'w', newline='', encoding='UTF-8') as csv_file:
        writer = csv.writer(csv_file)
        for key in issue_cache:
            writer.writerow([key, issue_cache[key]])


def read_sample_csv(filename):
    with open(filename, 'r', newline='', encoding='UTF-8') as csv_file:
        reader = csv.reader(csv_file)
        return [Sample(*row) for row in reader]


def write_sample_csv(samples, filename):
    with open(filename, 'w', newline='', encoding='UTF-8') as csv_file:
        writer = csv.writer(csv_file)
        for sample in samples:
            writer.writerow(list(sample))


def read_text_file(filename):
    file = open(filename, 'r', encoding='UTF-8')
    text = file.read()
    file.close()
    return text


def write_text_file(filename, text):
    file = open(filename, 'w', encoding='UTF-8')
    text = file.write(text)
    file.close()
