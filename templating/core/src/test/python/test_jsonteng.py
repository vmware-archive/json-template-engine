import sys
from io import StringIO
import unittest

from jsonteng import template_engine
from jsonteng.exception import TemplateEngineException


class TestJsonteng(unittest.TestCase):
    """
    Unit tests for the template engine.
    """
    def setUp(self):
        """
        Set up each test.
        """
        self.stream = StringIO()
        sys.stdout = self.stream

    def tearDown(self):
        """
        Tear down each test.
        """
        sys.stdout = sys.__stdout__

    def test_resolve_dict(self):
        """
        Test resolving templates.
        """
        template_engine.main(["-r", "-b",
                              "{\"x\": 1}", '{"y": "x$\\$${x}"}'])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str, '"{\\"y\\": \\"x$$1\\"}"')

    def test_resolve_list_value(self):
        """
        Test resolving templates with list values.
        """
        template_engine.main(["-r", "-b",
                              "{\"x\": [1, 2]}", '{"y": "${x[1]}"}'])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str, '{"y": 2}')

    def test_misformed_param(self):
        """
        Test resolving templates with missing }.
        """
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  "{\"x\": [1, 2]}", '{"y": "${x[1]"}'])

    def test_missing_param(self):
        """
        Test resolving templates with missing binding param.
        """
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  "{\"x\": [1, 2]}", '{"y": "${x1}"}'])

    def test_resolve_empty_param(self):
        """
        Test resolving templates with empty param reference.
        """
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  "{\"x\": [1, 2]}", '{"y": "${}"}'])

    def test_resolve_too_many_param(self):
        """
        Test resolving templates with too many param layers.
        """
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  "{\"x\": [1, 2]}", '{"y": "${x.x1}"}'])

    def test_resolve_bool_value(self):
        """
        Test resolving templates with boolean value.
        """
        template_engine.main(["-r", "-b",
                              "{\"x\": true}", '{"y": "${x}"}'])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str, '{"y": true}')

    def test_cli(self):
        """
        Test resolving templates using CLI.
        """
        template_engine.main(["-v", "-s", "-d", "-r", "-b",
                              "{\"x\": 1}", '{"y": "${x}"}'])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(len(json_str), 153, json_str)

    def test_duplicate_param(self):
        """
        Test resolving templates with duplicated params.
        """
        template_engine.main(["-v", "-r", "-b",
                              "{\"x\": 1};{\"x\": 2}", '{"y": "${x}"}'])
        json_str = self.stream.getvalue().strip()
        self.assertNotEqual(json_str.find("duplicate"), -1)

    def test_key_rule(self):
        """
        Test resolving templates where a key is a rule.
        """
        template = \
            "{\"#one-of\":[[\"1==2\",\"false\"],[\"2==2\", {\"a\":\"lower\"}]]}"
        template_engine.main(["-r", "-b",
                              "{\"list\":[{\"z\":\"100\"},{\"z\":\"200\"}]}",
                              template])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str, "{\"a\": \"lower\"}")

    def test_key_rule_invalid(self):
        """
        Test resolving templates with invalid rule format.
        """
        template = \
            "{\"#one-of\":\"lower\"}"
        with self.assertRaises(TemplateEngineException):
            template_engine.main(
                ["-r", "-b", "{\"list\":[{\"z\":\"100\"}, {\"z\":\"200\"}]}",
                    template])

    def test_key_rule_invalid_result(self):
        """
        Test resolving templates with a key rule that does not return a dict.
        """
        template = \
            "{\"#one-of\":[[\"1==2\",\"false\"],[\"2==2\", \"lower\"]]}"
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  "{\"list\":[{\"z\":\"100\"},{\"z\":\"20\"}]}",
                                  template])

    def test_unknwon_rule(self):
        """
        Test resolving templates with a unknown rule.
        """
        template = \
            "{\"x\":[\"#xxyyzz\",\"${list}\",\"{\\\"y\\\":\\\"${z}\\\"}\"]}"
        with self.assertRaises(TemplateEngineException):
            template_engine.main(
                ["-r", "-b", "{\"list\":[{\"z\":\"100\"}, {\"z\":\"200\"}]}",
                    template])

    def test_foreach(self):
        """
        Test resolving templates with for-each rule.
        """
        template = \
            "{\"x\":[\"#for-each\",\"${list}\",\"{\\\"y\\\":\\\"${z}\\\"}\"]}"
        template_engine.main(["-r", "-b",
                              "{\"list\":[{\"z\":\"100\"},{\"z\":\"200\"}]}",
                              template])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str,
                         "{\"x\": [{\"y\": \"100\"}, {\"y\": \"200\"}]}")

    def test_oneof(self):
        """
        Test resolving templates with one-of rule.
        """
        template = \
            "{\"x\": [\"#one-of\",[\"1 == 2\",\"false\"], [\"2==2\",\"true\"]]}"
        template_engine.main(["-r", "-b",
                              "{\"list\":[{\"z\":\"100\"},{\"z\":\"200\"}]}",
                              template])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str, "{\"x\": \"true\"}")

    def test_oneof_default(self):
        """
        Test resolving templates with one-of rule having a default value.
        """
        template = \
            "{\"x\": [\"#one-of\",[\"1 == 2\",\"false\"], \"default\"]}"
        template_engine.main(["-r", "-b",
                              "{\"list\":[{\"z\":\"100\"},{\"z\":\"200\"}]}",
                              template])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str, "{\"x\": \"default\"}")

    def test_oneof_invalid_type(self):
        """
        Test resolving templates with one-of rule with invalid default (list).
        """
        template = \
            "{\"x\": [\"#one-of\",[\"1 == 2\",\"false\"], [\"default\"]]}"
        with self.assertRaises(TemplateEngineException):
            template_engine.main(["-r", "-b",
                                  "{\"list\":[{\"z\":\"100\"},{\"z\":\"20\"}]}",
                                  template])
