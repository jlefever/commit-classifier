import argparse
from typing import List
import os
import csv
import re
from common import Commit, FileLine, write_commit_json, read_text_file


class FileLineParser:
    def __init__(self, text, row):
        self.text = text
        self.row = row
        self.curr_index = 0
    
    def parse(self):
        additions = self.parse_number()
        self.skip_whitespace()
        deletions = self.parse_number()
        self.skip_whitespace()
        filename = self.parse_to_end()
        return FileLine(filename, additions, deletions)

    def parse_number(self):
        digits = ''
        while self.is_digit():
            digits += self.advance()
        if digits == '-':
            return 0
        try:
            return int(digits)
        except ValueError:
            self.error('Expected an integer.')

    def parse_to_end(self):
        text = ''
        while self.peak() != '\0':
            text += self.advance()
        return text

    def skip_whitespace(self):
        while self.peak() in ' \t':
            self.advance()

    def is_digit(self):
        char = self.peak()
        return char != '\0' and char in '-0123456789'

    def is_at_end(self):
        return self.curr_index >= len(self.text)

    def peak(self):
        if self.is_at_end(): return '\0'
        return self.text[self.curr_index]

    def advance(self):
        if self.is_at_end(): return '\0'
        self.curr_index += 1
        return self.text[self.curr_index - 1]

    def error(self, error_message: str):
        row, col = self.row, self.curr_index
        print('Error: Row {}: Col: {}: {}'.format(row, col, error_message))
        quit()


class GitLogParser:
    def __init__(self, text) -> None:
        self.lines: List[str] = text.splitlines()
        self.curr_line: int = 0

    def parse(self):
        commits = []
        while not self.is_at_end():
            commits.append(self.parse_commit())
        return commits

    def parse_commit(self):
        hash = self.parse_field('commit ')
        merge = self.parse_field('Merge: ', optional=True)
        author = self.parse_field('Author: ')
        date = self.parse_field('Date:   ')
        self.parse_empty_line()
        msg = self.parse_msg()
        files = self.parse_files()
        return Commit(hash, merge, author, date, msg, files)

    def parse_field(self, name, optional=False):
        line = self.peak()
        if line.startswith(name):
            self.advance()
            return line[len(name):]
        if not optional:
            self.error('Expected "{}"'.format(name))
        return None

    def parse_empty_line(self):
        text = self.advance()
        if text != '':
            self.error('Expected empty line.')

    def parse_msg(self):
        items = []
        while self.peak() != '':
            items.append(self.parse_field('    '))
        self.parse_empty_line()
        return '\n'.join(items)

    def parse_files(self):
        files = []
        if not self.starts_with_digit():
            return files
        while self.starts_with_digit():
            file_parser = FileLineParser(self.peak(), self.curr_line)
            files.append(file_parser.parse())
            self.advance()
        self.parse_empty_line()
        return files

    def starts_with_digit(self):
        text = self.peak()
        return len(text) > 0 and text[0] in '-0123456789'

    def is_at_end(self):
        return self.curr_line >= len(self.lines)

    def peak(self):
        if self.is_at_end(): return ''
        return self.lines[self.curr_line]

    def advance(self):
        if self.is_at_end(): return ''
        self.curr_line += 1
        return self.lines[self.curr_line - 1]

    def error(self, error_message: str) -> None:
        print('Error: Row {}: {}'.format(self.curr_line, error_message))
        quit()


def parse_git_log(text):
    return GitLogParser(text).parse()


if __name__ == '__main__':
    ag = argparse.ArgumentParser(description='Extract features from a git log.')
    ag.add_argument('git_log', type=str, help='a git log file')
    ag.add_argument('commit_json', type=str, help='output commits json')
    args = ag.parse_args()
    commits = parse_git_log(read_text_file(args.git_log))
    write_commit_json(commits, args.commit_json)
