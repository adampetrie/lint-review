import logging
import os
from lintreview.tools import Tool
from lintreview.tools import run_command
from lintreview.utils import in_path
from lintreview.utils import npm_exists

log = logging.getLogger(__name__)


class Sasslint(Tool):

    name = 'sasslint'

    def check_dependencies(self):
        """
        See if SassLint is on the system path.
        """
        return in_path('sass-lint') or npm_exists('sass-lint')

    def match_file(self, filename):
        """
        Check if a file should be linted using SassLint.
        """
        base = os.path.basename(filename)
        name, ext = os.path.splitext(base)
        return ext == '.scss' or ext == '.sass'

    def process_files(self, files):
        """
        Run code checks with SassLint.
        """
        log.debug('Processing %s files with %s', files, self.name)
        cmd = 'sass-lint'
        if npm_exists('sass-lint'):
            cmd = os.path.join(os.getcwd(), 'node_modules', '.bin', 'sass-lint')
        command = [cmd, '--format', 'checkstyle', '--no-exit', '--verbose']
        # Add config file if it's present
        if self.options.get('config'):
            command += ['--config', self.apply_base(self.options['config'])]
        command += files
        output = run_command(
            command,
            ignore_error=True)
        self._process_checkstyle(output)
