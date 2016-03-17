import os
import logging
from lintreview.tools import Tool
from lintreview.tools import run_command
from lintreview.utils import in_path
from lintreview.utils import bundle_exists

log = logging.getLogger(__name__)


class Brakeman(Tool):

    name = 'brakeman'

    def check_dependencies(self):
        """
        See if brakeman is on the PATH
        """
        return in_path('brakeman') or bundle_exists('brakeman')

    def match_file(self, filename):
        base = os.path.basename(filename)
        name, ext = os.path.splitext(base)
        return ext == '.rb'

    def process_files(self, files):
        """
        Run code checks with brakeman
        """
        log.debug('Processing %s files with %s', files, self.name)
        command = ['brakeman']
        if bundle_exists('brakeman'):
            command = ['bundle', 'exec', 'brakeman']
        command += ['--format', 'tabs']
        command += files
        output = run_command(
            command,
            split=True,
            ignore_error=True,
            include_errors=False
        )

        if not output:
            log.debug('No brakeman errors found.')
            return False

        for line in output:
            filename, line, error = self._parse_line(line)
            self.problems.add(filename, line, error)

    def _parse_line(self, line):
        """
        `brakeman --format tabs` lines look like this:
        filename\tlineno\tclass\terror
        """
        parts = line.split('\t', 3)
        message = 'Brakeman: ' + parts[2] + parts[3]
        return (parts[0], int(parts[1]), message)
