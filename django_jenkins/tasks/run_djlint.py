# -*- coding: utf-8 -*-
# pylint: disable=W0201
import os
import sys
from optparse import make_option
from django.conf import settings
from django_jenkins.tasks import BaseTask, get_apps_under_test

from pylint.reporters.text import ParseableTextReporter

from django_lint.script import djlint


class Task(BaseTask):
    option_list = [make_option("--djlint-rcfile",
                               dest="djlint_rcfile",
                               help="django pylint configuration file"),
                   make_option("--djlint-errors-only",
                               dest="djlint_errors_only",
                               action="store_true", default=False,
                               help="django lint output errors only mode")]

    def __init__(self, test_labels, options):
        super(Task, self).__init__(test_labels, options)

        self.test_all = options['test_all']
        self.config_path = options['djlint_rcfile'] or \
                           Task.default_config_path()
        self.errors_only = options['djlint_errors_only']

        if options.get('djlint_file_output', True):
            output_dir = options['output_dir']
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.output = open(os.path.join(output_dir, 'djlint.report'), 'w')
        else:
            self.output = sys.stdout

    def teardown_test_environment(self, **kwargs):
        rc_file = self.config_path
        targets = get_apps_under_test(self.test_labels, self.test_all)

        djlint(rc_file, targets, errors_only=self.errors_only,
               reporter=ParseableTextReporter(output=self.output), exit=False)

        return True

    @staticmethod
    def default_config_path():
        rcfile = getattr(settings, 'PYLINT_RCFILE', 'pylint.rc')
        if os.path.exists(rcfile):
            return rcfile

        # use build-in
        root_dir = os.path.normpath(os.path.dirname(__file__))
        return os.path.join(root_dir, 'pylint.rc')
