import pytest
import string
import csv
import random
from golem.gui import gui_utils


DOCSTRINGS = [
    {
        'actual': """some description

        Parameters:
        param1 : value
        """,
        'expected': {
            'description': 'some description',
            'parameters': [{'name': 'param1', 'type': 'value'}]
        }
    },
    {
        'actual': """some description with
        multiline

        Parameters:
        param1 : value
        """,
        'expected': {
            'description': 'some description with multiline',
            'parameters': [{'name': 'param1', 'type': 'value'}]
        }
    },
    {
        'actual': """some description with
        
        blank lines

        Parameters:
        param1 : value
        """,
        'expected': {
            'description': 'some description with blank lines',
            'parameters': [{'name': 'param1', 'type': 'value'}]
        }
    },
    {
        'actual': """multiple parameters

        Parameters:
        param1 : value
        param2 (with desc and spaces etc) : element
        param3 : value
        param4 : element
        """,
        'expected': {
            'description': 'multiple parameters',
            'parameters': [{'name': 'param1', 'type': 'value'},
                           {'name': 'param2 (with desc and spaces etc)', 'type': 'element'},
                           {'name': 'param3', 'type': 'value'},
                           {'name': 'param4', 'type': 'element'}]
        }
    },
    {
        'actual': """
        Parameters:
        no description : value
        """,
        'expected': {
            'description': '',
            'parameters': [{'name': 'no description', 'type': 'value'}]
        }
    },
    {
        'actual': """no parameters
        
        """,
        'expected': {
            'description': 'no parameters',
            'parameters': []
        }
    }
]


class TestGolemActionParser:

    @pytest.mark.parametrize('actual,expected',
                             [(x['actual'], x['expected']) for x in DOCSTRINGS])
    def test__parse_docstring(self, actual, expected):
        expected = gui_utils.Golem_action_parser()._parse_docstring(actual)
        assert expected == expected
