import os
import logging
from lintreview.tools import Tool
from lintreview.tools import run_command
from lintreview.utils import in_path
from lintreview.utils import bundle_exists

log = logging.getLogger(__name__)


class Reek(Tool):

    name = 'reek'

    def check_dependencies(self):
        """
        See if reek is on the PATH
        """
        return in_path('reek') or bundle_exists('reek')

    def match_file(self, filename):
        base = os.path.basename(filename)
        name, ext = os.path.splitext(base)
        return ext == '.rb'

    def process_files(self, files):
        """
        Run code smell checks with reek
        """
        log.debug('Processing %s files with %s', files, self.name)
        command = ['reek']
        if bundle_exists('reek'):
            command = ['bundle', 'exec', 'reek']
        command += ['--single-line','--no-color']
        command += files
        output = run_command(
            command,
            split=True,
            ignore_error=True,
            include_errors=False
        )

        if not output:
            log.debug('No reek errors found.')
            return False

        for line in output:
            """
            Reek -s outputs warnings with leading spaces
            """
            if isinstance(line, basestring) and line.startswith(' '):
                filename, line, error = self._parse_line(line)
                self.problems.add(filename, line, error)

    def _parse_line(self, line):
        """
        `reek --single-line` lines look like this:
          filename:lineno: error
        """
        parts = line.strip().split(':', 2)
        message = parts[2].strip()
        filename = os.path.abspath(parts[0])
        return (filename, int(parts[1]), message)
