import os
import csv
import string
import random
import pytest

from golem.cli import messages
from golem.gui import user
from golem.core import utils


class TestGolemHelp:

    run_commands = [
        ('golem', messages.USAGE_MSG),
        ('golem -h', messages.USAGE_MSG),
        ('golem --help', messages.USAGE_MSG),
        ('golem -h run', messages.RUN_USAGE_MSG),
        ('golem -h gui', messages.GUI_USAGE_MSG),
        ('golem -h createproject', messages.CREATEPROJECT_USAGE_MSG),
        ('golem -h createtest', messages.CREATETEST_USAGE_MSG),
        ('golem -h createsuite', messages.CREATESUITE_USAGE_MSG),
        ('golem -h createuser', messages.CREATEUSER_USAGE_MSG),
        ('golem run -h', messages.RUN_USAGE_MSG),
        ('golem gui -h', messages.GUI_USAGE_MSG),
    ]

    @pytest.mark.slow
    @pytest.mark.parametrize('command,expected', run_commands)
    def test_golem_command_output(self, command, expected, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        result = test_utils.run_command(command)
        assert result == expected


class TestGolemRun:

    @pytest.mark.slow
    def test_golem_run_test(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        test = 'test2'
        command = 'golem createtest {} {}'.format(project, test)
        test_utils.run_command(command)
        command = 'golem run {} {}'.format(project, test)
        result = test_utils.run_command(command)
        assert 'INFO Test execution started: {}'.format(test) in result
        assert 'INFO Browser: chrome' in result
        assert 'INFO Test Result: SUCCESS' in result

    @pytest.mark.slow
    def test_golem_run_suite_with_no_tests(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        suite = 'suite2'
        command = 'golem createsuite {} {}'.format(project, suite)
        test_utils.run_command(command)
        command = 'golem run {} {}'.format(project, suite)
        result = test_utils.run_command(command)
        assert 'No tests were found for suite suite2' in result

    @pytest.mark.slow
    def test_golem_run_no_args(self, project_session, test_utils):
        path = project_session.testdir
        os.chdir(path)
        result = test_utils.run_command('golem run')
        expected = messages.RUN_USAGE_MSG
        expected += '\nProjects:'
        for proj in utils.get_projects(path):
            expected += '\n  {}'.format(proj)
        assert result == expected

    @pytest.mark.slow
    def test_golem_run_test_b_flag(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        test = 'test2'
        command = 'golem createtest {} {}'.format(project, test)
        test_utils.run_command(command)
        command = 'golem run {} {} -b firefox'.format(project, test)
        result = test_utils.run_command(command)
        assert 'INFO Test execution started: {}'.format(test) in result
        assert 'INFO Browser: firefox' in result
        assert 'INFO Test Result: SUCCESS' in result

    @pytest.mark.slow
    def test_golem_run_not_match_test_or_suite(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        test = 'test001_does_not_exist'
        command = 'golem run {} {}'.format(project, test)
        result = test_utils.run_command(command)
        expected = ('golem run: error: the value {} does not match '
                    'an existing test, suite or directory'.format(test))
        assert result == expected

    @pytest.mark.slow
    def test_golem_run_project_does_not_exist(self, testdir_session, test_utils):
        project = 'project_does_not_exist_4564546'
        os.chdir(testdir_session.path)
        test = 'test002_does_not_exist'
        command = 'golem run {} {}'.format(project, test)
        result = test_utils.run_command(command)
        expected = ('golem run: error: the project {0} does not exist'.format(project))
        assert result == expected

    @pytest.fixture(scope="class")
    def _project_with_suite(self, project_class, test_utils):
        """A fixture of a project with class scope with one suite with
        one test
        """
        suite_name = 'suite1'
        test_utils.create_test(project_class.testdir, project_class.name,
                               parents=[], name='test1')
        test_utils.create_suite(project_class.testdir, project_class.name,
                                parents=[], name=suite_name, content=None,
                                tests=['test1'])
        project_class.suite_name = suite_name
        return project_class

    @pytest.mark.slow
    def test_generate_reports(self, _project_with_suite, test_utils):
        """Assert that the reports are generated by default in the
        report directory and with name: 'report'
        """
        project = _project_with_suite.name
        timestamp = '0.1.2.3.001'
        cmd = ('golem run {} {} -r html html-no-images junit --timestamp {}'
               .format(project, _project_with_suite.suite_name, timestamp))
        test_utils.run_command(cmd)
        reportdir = os.path.join(_project_with_suite.testdir, 'projects', project,
                                 'reports', _project_with_suite.suite_name, timestamp)
        assert os.path.isfile(os.path.join(reportdir, 'report.html'))
        assert os.path.isfile(os.path.join(reportdir, 'report-no-images.html'))
        assert os.path.isfile(os.path.join(reportdir, 'report.xml'))
        # report.json is generated by default
        assert os.path.isfile(os.path.join(reportdir, 'report.json'))

    @pytest.mark.slow
    def test_generate_reports_with_report_folder(self, _project_with_suite, test_utils):
        """Assert that the reports are generated in the report-folder"""
        project = _project_with_suite.name
        timestamp = '0.1.2.3.002'
        reportdir = os.path.join(_project_with_suite.testdir, 'report-folder')
        cmd = ('golem run {} {} -r html html-no-images junit json --report-folder {} '
               '--timestamp {}'.format(project, _project_with_suite.suite_name,reportdir, timestamp))
        test_utils.run_command(cmd)
        assert os.path.isfile(os.path.join(reportdir, 'report.html'))
        assert os.path.isfile(os.path.join(reportdir, 'report-no-images.html'))
        assert os.path.isfile(os.path.join(reportdir, 'report.xml'))
        assert os.path.isfile(os.path.join(reportdir, 'report.json'))

    @pytest.mark.slow
    def test_generate_reports_with_report_folder_report_name(self, _project_with_suite,
                                                             test_utils):
        """Assert that the reports are generated in the report-folder with report-name"""
        project = _project_with_suite.name
        timestamp = '0.1.2.3.003'
        reportdir = os.path.join(_project_with_suite.testdir, 'projects', project,
                                 'reports', _project_with_suite.suite_name, timestamp)
        report_name = 'foo'
        cmd = ('golem run {} {} -r html html-no-images junit json --report-name {} '
               '--timestamp {}'.format(project, _project_with_suite.suite_name, report_name, timestamp))
        test_utils.run_command(cmd)
        assert os.path.isfile(os.path.join(reportdir, 'foo.html'))
        assert os.path.isfile(os.path.join(reportdir, 'foo-no-images.html'))
        assert os.path.isfile(os.path.join(reportdir, 'foo.xml'))
        assert os.path.isfile(os.path.join(reportdir, 'foo.json'))

    @pytest.mark.slow
    def test_generate_reports_with_report_folder_report_name(self, _project_with_suite,
                                                             test_utils):
        """Assert that the reports are generated in the report-folder with report-name"""
        project = _project_with_suite.name
        timestamp = '0.1.2.3.004'
        reportdir = os.path.join(_project_with_suite.testdir, 'report-folder')
        report_name = 'foo'
        cmd = ('golem run {} {} -r html html-no-images junit json --report-folder {} '
               '--report-name {} --timestamp {}'
               .format(project, _project_with_suite.suite_name, reportdir, report_name, timestamp))
        test_utils.run_command(cmd)
        assert os.path.isfile(os.path.join(reportdir, 'foo.html'))
        assert os.path.isfile(os.path.join(reportdir, 'foo-no-images.html'))
        assert os.path.isfile(os.path.join(reportdir, 'foo.xml'))
        assert os.path.isfile(os.path.join(reportdir, 'foo.json'))


class TestGolemCreateProject:

    @pytest.mark.slow
    def test_golem_createproject(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        project = 'testproject1'
        cmd = 'golem createproject {}'.format(project)
        result = test_utils.run_command(cmd)
        assert result == 'Project {} created'.format(project)
        projects = utils.get_projects(testdir_session.path)
        assert project in projects

    @pytest.mark.slow
    def test_golem_createproject_no_args(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        result = test_utils.run_command('golem createproject')
        expected = ('usage: golem createproject [-h] project\n'
                    'golem createproject: error: the following '
                    'arguments are required: project')
        assert result == expected

    @pytest.mark.slow
    def test_golem_createproject_project_exists(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        cmd = 'golem createproject {}'.format(project)
        result = test_utils.run_command(cmd)
        expected = ('golem createproject: error: a project with name \'{}\' already exists'
                    .format(project))
        assert result == expected


class TestGolemCreateSuite:

    @pytest.mark.slow
    def test_golem_createsuite(self, project_session, test_utils):
        project = project_session.name
        os.chdir(project_session.testdir)
        suite = 'suite1'
        command = 'golem createsuite {} {}'.format(project, suite)
        result = test_utils.run_command(command)
        msg = 'Suite {} created for project {}'.format(suite, project)
        assert result == msg
        spath = os.path.join(project_session.path, 'suites', suite+'.py')
        assert os.path.isfile(spath)

    @pytest.mark.slow
    def test_golem_createsuite_no_args(self, project_session, test_utils):
        path = project_session.testdir
        os.chdir(path)
        result = test_utils.run_command('golem createsuite')
        expected = ('usage: golem createsuite [-h] project suite\n'
                    'golem createsuite: error: the following arguments '
                    'are required: project, suite')
        assert result == expected

    @pytest.mark.slow
    def test_golem_createsuite_project_does_not_exist(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        project = 'project_does_not_exist'
        suite = 'suite_test_00002'
        cmd = 'golem createsuite {} {}'.format(project, suite)
        result = test_utils.run_command(cmd)
        expected = ('golem createsuite: error: a project with name {} '
                    'does not exist'.format(project))
        assert result == expected

    @pytest.mark.slow
    def test_golem_createsuite_already_exists(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        suite = 'suite_test_00003'
        command = 'golem createsuite {} {}'.format(project, suite)
        test_utils.run_command(command)
        result = test_utils.run_command(command)
        expected = ('golem createsuite: error: a suite '
                    'with that name already exists')
        assert result == expected


class TestGolemCreateTest:

    @pytest.mark.slow
    def test_golem_createtest(self, project_session, test_utils):
        project = project_session.name
        os.chdir(project_session.testdir)
        test = 'test1'
        command = 'golem createtest {} {}'.format(project, test)
        result = test_utils.run_command(command)
        msg = 'Test {} created for project {}'.format(test, project)
        assert result == msg
        tpath = os.path.join(project_session.path, 'tests', test+'.py')
        assert os.path.isfile(tpath)

    @pytest.mark.slow
    def test_golem_createtest_no_args(self, project_session, test_utils):
        path = project_session.testdir
        os.chdir(path)
        result = test_utils.run_command('golem createtest')
        expected = ('usage: golem createtest [-h] project test\n'
                    'golem createtest: error: the following arguments '
                    'are required: project, test')
        assert result == expected

    @pytest.mark.slow
    def test_golem_createtest_project_not_exist(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        project = 'project_not_exist'
        test = 'test_0004'
        cmd = 'golem createtest {} {}'.format(project, test)
        result = test_utils.run_command(cmd)
        expected = ('golem createtest: error: a project with name {} '
                    'does not exist'.format(project))
        assert result == expected

    @pytest.mark.slow
    def test_golem_createtest_already_exists(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        test = 'test_0005'
        cmd = 'golem createtest {} {}'.format(project, test)
        test_utils.run_command(cmd)
        result = test_utils.run_command(cmd)
        expected = ('golem createtest: error: a test with that name already exists')
        assert result == expected


class TestGolemCreateUser:

    @pytest.mark.slow
    def test_golem_createuser(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        username = 'user1'
        password = '123456'
        command = 'golem createuser {} {}'.format(username, password)
        result = test_utils.run_command(command)
        msg = 'User {} was created successfully'.format(username)
        assert result == msg
        assert user.get_user_data(username=username)
