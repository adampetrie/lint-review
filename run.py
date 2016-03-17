import argparse
import lintreview
import lintreview.github as github
import lintreview.tasks as tasks
import logging
import pkg_resources
import sys

from flask import url_for
from lintreview.web import app
from lintreview.github import get_repository
from lintreview.github import get_lintrc
from flask import Flask, request, Response
from lintreview.config import load_config


config = load_config()
app = Flask("lintreview")
app.config.update(config)

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.setLevel('DEBUG')
version = pkg_resources.get_distribution('lintreview').version


def main():
    parser = argparse.ArgumentParser(description='Scan the code for issues and report as comments in GitHub')
    parser.add_argument('--pull-request', dest="pull_request", help="The PR to scan", type=int)
## Disabled for now
#    parser.add_argument('--commit', help="The commit to scan", type=str)
    parser.add_argument('--user', help="The GitHub User who owns the repo",
            type=str, default=app.config['GITHUB_USER'])
    parser.add_argument('--repo', help="The GitHub Repo name", type=str)
    runtime_config = parser.parse_args()

    gh = get_repository(app.config, runtime_config.user, runtime_config.repo)
    try:
        lintrc = get_lintrc(gh)
        log.debug("lintrc file contents '%s'", lintrc)
    except Exception as e:
        log.warn("Cannot download .lintrc file for '%s', "
                 "skipping lint checks.", base_repo_url)
        log.warn(e)
        return 2

    if (runtime_config.pull_request > 0):
        tasks.process_pull_request(runtime_config.user, runtime_config.repo, runtime_config.pull_request, lintrc)
## Disabled for now
#    if (isinstance(runtime_config.commit, basestring) and runtime_config.len() > 0):
#        tasks.process_commit(runtime_config.user, runtime_config.repo, runtime_config.commit, lintrc)

if __name__ == '__main__':
    main()

