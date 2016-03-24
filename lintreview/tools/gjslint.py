import logging
import os
import re
from lintreview.tools import Tool
from lintreview.tools import run_command
from lintreview.utils import in_path
from lintreview.utils import npm_exists

log = logging.getLogger(__name__)


class Gjslint(Tool):

    name = 'gjslint'

    def check_dependencies(self):
        """
        See if gjslint is on the system path.
        """
        return in_path('gjslint') or npm_exists('gjslint')

    def match_file(self, filename):
        base = os.path.basename(filename)
        name, ext = os.path.splitext(base)
        return ext == '.js'

    def process_files(self, files):
        """
        Run code checks with gjslint.
        Only a single process is made for all files
        to save resources.
        """
        log.debug('Processing %s files with %s', files, self.name)
        command = self.create_command(files)
        output = run_command(
            command,
            split=True,
            ignore_error=True)

        if not output:
            log.debug('No pep8 errors found.')
            return False

        """
        Lint Errors are reports as follows:
        ----- FILE  :  /private/tmp/workspace/repo/repo_name/pr_number/path/to/file.js -----
        Line 546, E:0007: Should have 2 blank lines between top-level blocks.
        Line 550, E:0210: Missing docs for parameter: "parameters"
        Line 550, E:0210: Missing docs for parameter: "url"
        Found 9 errors, including 1 new error, in 3 files (0 files OK).
        """
        filename = ''
        for line in output:
            if 'FILE' in line:
                filename = self._parse_filename(line)
            elif re.match(r'Found .* errors', line):
                break;
            else:
                line_number, error = self._parse_line(line)
                self.problems.add(filename, line_number, error)

    def _parse_filename(self, line):
        return line.split()[3]

    def _parse_line(self, line):
        """
        Split this: 'Line 546, E:0007: Should have 2 blank lines between top-level blocks' by spaces
        line = '546,' without the comma
        message = Everything after 'E:0007:' converted to a string
        """
        parts = line.split()
        line = int(parts[1][0:-1])
        message = ' '.join(parts[3:len(parts)])
        return (line, message)

    def create_command(self, files):
        cmd = 'gjslint'
        if npm_exists('gjslint'):
            cmd = os.path.join(os.getcwd(), 'node_modules', '.bin', 'gjslint')
        command = [cmd, '--strict']
        command += files
        return command
