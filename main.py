import csv
import os
from common import read_commit_json
from common import read_issue_csv
from common import read_text_file
from common import read_sample_csv
from common import write_commit_json
from common import write_text_file
from common import write_sample_csv
from parse_git_log import parse_git_log
from retrieve_issues import retrieve_issues
from create_samples import create_samples


DIR = 'dataset'

PROJECTS = [
    'abdera',
    'activemq',
    'airflow',
    'arrow',
    'calcite',
    'flink',
    'geode',
    'hadoop',
    'hbase',
    'hudi',
    'jena',
    'kafka',
    'math',
    'maven',
    'rat'
]


def get_project_identifiers(issue_cache):
    project_ids = set()
    for key in issue_cache:
        if issue_cache[key] is None:
            continue
        project_ids.add(key.lower().split('-')[0])
    return project_ids



def to_git_log_filename(name):
    return '%s/%s_log.txt' % (DIR, name)


def to_commit_filename(name):
    return '%s/%s_commits.json' % (DIR, name)


def to_issue_filename(name):
    return '%s/%s_issues.csv' % (DIR, name)


def to_sample_filename(name):
    return '%s/%s_samples.csv' % (DIR, name)


def write_info_csv(filename):
    fn = os.path.join(DIR, filename)
    with open(fn, 'w', newline='', encoding='UTF-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Project', 'Date', 'Total Commits', 'Labeled Commits', 
                         '% Labeled', '% All Labeled Commits'])

        # Read data files
        all_commits = [read_commit_json(to_commit_filename(p)) for p in PROJECTS]
        all_samples = [read_sample_csv(to_sample_filename(p)) for p in PROJECTS]
        total_samples = sum(len(s) for s in all_samples)

        # Write to file
        for name, commits, samples in zip(PROJECTS, all_commits, all_samples):
            n_commits = len(commits)
            n_samples = len(samples)

            # Write row to csv
            writer.writerow([
                name,
                commits[0].date,
                n_commits,
                n_samples,
                '{:.2%}'.format(n_samples / n_commits),
                '{:.2%}'.format(n_samples / total_samples),
            ])


if __name__ == '__main__':
    for name in PROJECTS:
        # Get filenames for stored data
        git_log = to_git_log_filename(name)
        commits_json = to_commit_filename(name)
        issues_csv = to_issue_filename(name)
        samples_csv = to_sample_filename(name)

        # Parse git log into 'commits'
        if os.path.exists(commits_json):
            print('Loading %s from disk...' % (commits_json))
            commits = read_commit_json(commits_json)
        else:
            print('Parsing git log of %s...' % name)
            commits = parse_git_log(read_text_file(git_log))
            write_commit_json(commits, commits_json)

        # Lookup issues
        print('Looking up issues for %s...' % name)
        retrieve_issues(commits, issues_csv)

        # Create final samples file
        print('Creating final samples file for %s...' % name)
        issue_cache = read_issue_csv(issues_csv)
        samples = create_samples(commits, issue_cache)
        write_sample_csv(samples, samples_csv)

    # Write info file
    print('Creating summary file...')
    write_info_csv('_summary.csv')
