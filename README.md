# Commit Classifier

Can we use NLP to classify commits as bug-fixing or non-bug-fixing?

## Data Collection

Below are the command line scripts used to collect the data. We rely on [Apache projects](https://issues.apache.org/jira/secure/BrowseProjects.jspa) for our data.

- `parse_git_log.py` - Parse a git log into a CSV of commits.

- `retrieve_issues.py` - Given a CSV of commmits, lookup the issue IDs matching the regex. Record if that issue is a bug, not a bug, or not an issue at all. Write this into a CSV of issues.

- `create_samples.py` - Compile CSV of commits and CSV of issues into a single file for easier use.

## Experiement

`notebook.ipynb` includes an experiement using a bag-of-words model with naive bayes.
