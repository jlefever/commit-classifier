import argparse
from common import Sample, read_commit_json, read_issue_csv
from common import write_sample_csv
from common import get_apache_issue_id


def create_samples(commits, issue_cache):
    samples = []
    for c in commits:
        # Skip merge commits
        if c.merge is not None:
            continue

        # Look in commit message for an Apache Issue ID
        issue_id = get_apache_issue_id(c.msg)

        # Skip if there is no Issue ID
        if issue_id is None:
            continue

        # Skip if we do not have this issue cached
        # (This only happens if we do not yet have all issues)
        if issue_id not in issue_cache:
            continue
        is_bug = issue_cache[issue_id]

        # Skip Nones
        if is_bug is None:
            continue

        sample = Sample(hash=c.hash, msg=c.msg, n_files=len(c.files),
                        loc_added=c.loc_added(), loc_removed=c.loc_removed(),
                        issue_id=issue_id, is_bug=is_bug)
        samples.append(sample)
    return samples


if __name__ == '__main__':
    ag = argparse.ArgumentParser(description='Compile commits csv and issues csv')
    ag.add_argument('commit_json', type=str, help='a commits json')
    ag.add_argument('issue_csv', type=str, help='an issues csv')
    ag.add_argument('sample_csv', type=str, help='an output samples csv')
    args = ag.parse_args()
    commits = read_commit_json(args.commit_json)
    issue_cache = read_issue_csv(args.issue_csv)
    samples = create_samples(commits, issue_cache)
    write_sample_csv(samples, args.sample_csv)
