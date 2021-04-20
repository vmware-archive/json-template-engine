import unittest

from jsonteng import template_engine
from jsonteng.exception import TemplateEngineException


def _run_test(input_params):
    with open("/tmp/t1.txt", "w") as fp:
        template_engine.main(input_params, file=fp)
    with open("/tmp/t1.txt", "r") as fp:
        json_str = fp.read()
    return json_str


class TestJsonteng(unittest.TestCase):
    """
    Unit tests for the template engine.
    """

    def test_resolve_dict(self):
        """
        Test resolving templates.
        """
        json_str = _run_test(["-r", "-b", '{"x": 1}', '{"y": "abc\\\\defx$\\$${x}"}'])
        self.assertEqual('"{\\"y\\": \\"abc\\\\defx$$1\\"}"\n', json_str, 'test_resolve_dict')

    def test_resolve_list_value(self):
        """
        Test resolving templates with list values.
        """
        json_str = _run_test(["-r", "-b", '{"x": [1, 2]}', '{"y": "${x[1]}"}'])
        self.assertEqual('{"y": 2}\n', json_str, 'test_resolve_list_value')

    def test_misformed_param(self):
        """
        Test resolving templates with missing }.
        """
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  '{"x": [1, 2]}', '{"y": "${x[1]"}'])

    def test_missing_param(self):
        """
        Test resolving templates with missing binding param.
        """
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  '{"x": [1, 2]}', '{"y": "${x1}"}'])

    def test_resolve_empty_param(self):
        """
        Test resolving templates with empty param reference.
        """
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  '{"x": [1, 2]}', '{"y": "${}"}'])

    def test_resolve_too_many_param(self):
        """
        Test resolving templates with too many param layers.
        """
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  '{"x": [1, 2]}', '{"y": "${x.x1}"}'])

    def test_resolve_bool_value(self):
        """
        Test resolving templates with boolean value.
        """
        json_str = _run_test(["-r", "-b", '{"x": true}', '{"y": "${x}"}'])
        self.assertEqual('{"y": true}\n', json_str, 'test_resolve_bool_value')

    def test_cli(self):
        """
        Test resolving templates using CLI.
        """
        json_str = _run_test(["-v", "-s", "-d", "-r", "-b", '{"x": 1}', '{"y": "${x}"}'])
        self.assertEqual(154, len(json_str), 'test_cli')

    def test_duplicate_param(self):
        """
        Test resolving templates with duplicated params.
        """
        json_str = _run_test(["-v", "-r", "-b", '{"x": 1};{"x": 2}', '{"y": "${x}"}'])
        self.assertNotEqual(-1, json_str.find("duplicate"), 'test_duplicate_param')

    def test_key_rule(self):
        """
        Test resolving templates where a key is a rule.
        """
        template = '{"#one-of":[["1==2","false"],["2==2", {"a":"lower"}]]}'
        json_str = _run_test(["-r", "-b", '{"list":[{"z":"100"},{"z":"200"}]}', template])
        self.assertEqual('{"a": "lower"}\n', json_str, 'test_key_rule')

    def test_key_rule_invalid(self):
        """
        Test resolving templates with invalid rule format.
        """
        template = '{"#one-of":"lower"}'
        with self.assertRaises(TemplateEngineException):
            template_engine.main(
                ["-r", "-b", '{"list":[{"z":"100"}, {"z":"200"}]}', template])

    def test_key_rule_invalid_result(self):
        """
        Test resolving templates with a key rule that does not return a dict.
        """
        template = '{"#one-of":[["1==2","false"],["2==2", "lower"]]}'
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  '{"list":[{"z":"100"},{"z":"20"}]}',
                                  template])

    def test_unknown_rule(self):
        """
        Test resolving templates with a unknown rule.
        """
        template = \
            '{"x":["#xxyyzz","${list}","{\\"y\\":\\"${z}\\"}"]}'
        with self.assertRaises(TemplateEngineException):
            template_engine.main(
                ["-r", "-b", '{"list":[{"z":"100"}, {"z":"200"}]}',
                    template])

    def test_foreach(self):
        """
        Test resolving templates with for-each rule.
        """
        template = '{"x":["#for-each","${list}","{\\"y\\":\\"${z}\\"}\"]}'
        json_str = _run_test(["-r", "-b", '{"list":[{"z":"100"},{"z":"200"}]}', template])
        self.assertEqual('{"x": [{"y": "100"}, {"y": "200"}]}\n', json_str, 'test_foreach')

    def test_oneof(self):
        """
        Test resolving templates with one-of rule.
        """
        template = '{"x": ["#one-of",["1 == 2","false"], ["2==2","true"]]}'
        json_str = _run_test(["-r", "-b", '{"list":[{"z":"100"},{"z":"200"}]}', template])
        self.assertEqual('{"x": "true"}\n', json_str, 'test_oneof')

    def test_oneof_default(self):
        """
        Test resolving templates with one-of rule having a default value.
        """
        template = '{"x": ["#one-of",["1 == 2","false"], "default"]}'
        json_str = _run_test(["-r", "-b", '{"list":[{"z":"100"},{"z":"200"}]}', template])
        self.assertEqual('{"x": "default"}\n', json_str, 'test_oneof_default')

    def test_oneof_invalid_type(self):
        """
        Test resolving templates with one-of rule with invalid default (list).
        """
        template = '{"x": ["#one-of",["1 == 2","false"], ["default"]]}'
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  '{"list":[{"z":"100"},{"z":"20"}]}',
                                  template])
