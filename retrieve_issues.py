import argparse
import os
import time
import csv
from urllib.request import urlopen
from common import read_commit_json, read_issue_csv, write_issue_csv
from common import get_apache_issue_id


BUG_STR = 'Bug - A problem which impairs'
NOT_FOUND_STR = 'You must log in to access this page'
BASE_URL = 'https://issues.apache.org/jira/browse/'


def request_is_bug(key):
    line_end = '\t\t' if len(key) < 10 else '\t'
    print('Looking up %s...' % (key), end=line_end)
    res = urlopen(BASE_URL + key).read().decode('UTF-8')
    if res.find(NOT_FOUND_STR) != -1:
        print('None')
        return None
    bug = res.find(BUG_STR) != -1
    print(bug)
    return bug


def retrieve_issues(commits, issues_csv):
    issue_cache = {}
    if not os.path.exists(issues_csv):
        write_issue_csv(issue_cache, issues_csv)
    issue_cache = read_issue_csv(issues_csv)
    for commit in commits:
        # Look in commit message for an Apache Issue ID
        issue_id = get_apache_issue_id(commit.msg)

        # Skip Nones (no regex match)
        if issue_id is None:
            continue

        # Skip if we already cached this issue
        if issue_id in issue_cache:
            continue

        # Look it up and cache it
        issue_cache[issue_id] = request_is_bug(issue_id)
        write_issue_csv(issue_cache, issues_csv)


if __name__ == '__main__':
    ag = argparse.ArgumentParser(description='Lookup issue IDs in commits csv')
    ag.add_argument('commits_json', type=str, help='a commits json')
    ag.add_argument('issues_csv', type=str, help='a new or existing issues csv')
    args = ag.parse_args()
    commits = read_commit_json(args.commits_json)
    retrieve_issues(commits, args.issues_csv)
