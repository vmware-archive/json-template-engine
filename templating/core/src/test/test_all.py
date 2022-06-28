import os
import subprocess
import unittest

# LIB_TOP is the parent directory of the git repo clone.
LIB_TOP = os.getenv("LIB_TOP")
core = f'{LIB_TOP}/json-template-engine/templating/core'
tag_contrib = f'{LIB_TOP}/json-template-engine/templating/tag_contributions'
java_libs = f'{LIB_TOP}/libs'

os.putenv('PYTHONPATH', f'{core}/build/python/dist/jsonteng.whl:{tag_contrib}/build/python/dist/jsonteng_contribs.whl:'
                        f'{os.getenv("PYTHONPATH","")}')
jars = f'{core}/build/libs/jsonteng.jar:{tag_contrib}/build/libs/jsonteng-contribs.jar:' \
       f'{java_libs}/jackson-databind-2.9.7.jar:{java_libs}/jython-2.7.1b3.jar:{java_libs}/commons-cli-1.3.1.jar:' \
       f'{java_libs}/jackson-annotations-2.9.0.jar:{java_libs}/jackson-core-2.9.7.jar'


def _run_test(lang_type, input_params):
    if lang_type == 'python':
        p = subprocess.run(['python3', '-m', 'jsonteng.template_engine'] + input_params,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif lang_type == 'java':
        p = subprocess.run(['java', '-cp', jars, 'com.vmware.jsonteng.Cli'] + input_params,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif lang_type == 'c++':
        p = subprocess.run([f'{core}/build/c++/jsonteng'] + input_params,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif lang_type == 'go':
        p = subprocess.run([f'{core}/build/go/jsonteng_go_linux_x64'] + input_params,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        return ""
    output = p.stdout.decode('utf8')
    return output


class TestJsonteng(unittest.TestCase):
    """
    Unit tests for the template engine.
    """
    lang_types = ['python', 'java', 'c++', 'go']

    def test_resolve_dict(self):
        """
        Test resolving templates.
        """
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"x": 1}', '{"y": "\\\\abc\\\\defx$\\$${x}\\\\"}'])
            self.assertEqual('"{\\"y\\": \\"\\\\abc\\\\defx$$1\\\\\\"}"\n', output, f'test_resolve_dict - {lang}')

    def test_resolve_list_value(self):
        """
        Test resolving templates with list values.
        """
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"x": [1, 2]}', '{"y": "${x[1]}"}'])
            self.assertEqual('{"y":2}\n', output, f'test_resolve_list_value - {lang}')

    def test_misformed_param(self):
        """
        Test resolving templates with missing }.
        """
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"x": [1, 2]}', '{"y": "${x[1]"}'])
            self.assertEqual('Mis-formed parameterized string "${x[1]".\n', output, f'test_misformed_param - {lang}')

    def test_missing_param(self):
        """
        Test resolving templates with missing binding param.
        """
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"x": [1, 2]}', '{"y": "${x1}"}'])
            self.assertEqual('Unable to resolve parameter "x1".\n', output, f'test_missing_param - {lang}')

    def test_resolve_empty_param(self):
        """
        Test resolving templates with empty param reference.
        """
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"x": [1, 2]}', '{"y": "${}"}'])
            self.assertEqual('Unable to resolve parameter "".\n', output, f'test_resolve_empty_param - {lang}')

    def test_resolve_too_many_param(self):
        """
        Test resolving templates with too many param layers.
        """
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"x": [1, 2]}', '{"y": "${x.x1}"}'])
            self.assertEqual('Unable to resolve parameter "x.x1".\n', output, f'test_resolve_too_many_param - {lang}')

    def test_resolve_bool_value(self):
        """
        Test resolving templates with boolean value.
        """
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"x": true}', '{"y": "${x}"}'])
            self.assertEqual('{"y":true}\n', output, f'test_resolve_bool_value - {lang}')

    def test_cli(self):
        """
        Test resolving templates using CLI.
        """
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-v", "-s", "-d", "-r", "-b", '{"x": 1}', '{"y": "${x}"}'])
            self.assertIn('Resolved JSON in', output, f'test_cli - {lang}')

    def test_duplicate_param(self):
        """
        Test resolving templates with duplicated params.
        """
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-v", "-r", "-b", '{"x": 1};{"x": 2}', '{"y": "${x}"}'])
            self.assertIn('duplicate', output, f'test_duplicate_param - {lang}')

    def test_key_rule(self):
        """
        Test resolving templates where a key is a rule.
        """
        template = '{"#one-of":[["1==2","false"],["2==2", {"a":"lower"}]]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"list":[{"z":"100"},{"z":"200"}]}', template])
            self.assertEqual('{"a":"lower"}\n', output, f'test_key_rule - {lang}')

    def test_key_rule_invalid(self):
        """
        Test resolving templates with invalid rule format.
        """
        template = '{"#one-of":"lower"}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"list":[{"z":"100"}, {"z":"200"}]}', template])
            self.assertEqual('Value must be a list if name is a tag: "#one-of". Found "lower".\n',
                             output, f'test_key_rule_invalid - {lang}')

    def test_key_rule_invalid_result(self):
        """
        Test resolving templates with a key rule that does not return a dict.
        """
        template = '{"#one-of":[["1==2","false"],["2==2", "lower"]]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"list":[{"z":"100"},{"z":"20"}]}', template])
            self.assertEqual('Invalid tag result format for JSON object name tag: "#one-of"'
                             ' [["1==2","false"],["2==2","lower"]] => "lower".\n',
                             output, f'test_key_rule_invalid_result - {lang}')

    def test_unknown_rule(self):
        """
        Test resolving templates with a unknown rule.
        """
        template = '{"x":["#xxyyzz","${list}","{\\"y\\":\\"${z}\\"}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"list":[{"z":"100"}, {"z":"200"}]}', template])
            self.assertEqual('Unknown tag "xxyyzz".\n', output, f'test_unknown_rule - {lang}')

    def test_foreach(self):
        """
        Test resolving templates with for-each rule.
        """
        template = '{"x":["#for-each","${list}","{\\"y\\":\\"${z}\\"}\"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"list":[{"z":"100"},{"z":"200"}]}', template])
            self.assertEqual('{"x":[{"y":"100"},{"y":"200"}]}\n', output, f'test_foreach - {lang}')

    def test_oneof(self):
        """
        Test resolving templates with one-of rule.
        """
        template = '{"x": ["#one-of",["1 == 2","false"], ["2==2","true"]]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"list":[{"z":"100"},{"z":"200"}]}', template])
            self.assertEqual('{"x":"true"}\n', output, f'test_oneof - {lang}')

    def test_oneof_default(self):
        """
        Test resolving templates with one-of rule having a default value.
        """
        template = '{"x": ["#one-of",["1 == 2","false"], "default"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"list":[{"z":"100"},{"z":"200"}]}', template])
            self.assertEqual('{"x":"default"}\n', output, f'test_oneof_default - {lang}')

    def test_oneof_invalid_type(self):
        """
        Test resolving templates with one-of rule with invalid default (list).
        """
        template = '{"x": ["#one-of",["1 == 2","false"], ["invalid default"]]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"list":[{"z":"100"},{"z":"20"}]}', template])
            self.assertEqual('Tag "one-of" contains an invalid parameter. ["invalid default"].\n',
                             output, f'test_oneof_invalid_type - {lang}')

    def test_tobool_true(self):
        """
        Test resolving templates with to-bool rule.
        """
        template = '{"x": ["#to-bool", "${z}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"z":"True"}', template])
            self.assertEqual('{"x":true}\n',
                             output, f'test_tobool_true - {lang}')

    def test_tobool_false(self):
        """
        Test resolving templates with to-bool rule.
        """
        template = '{"x": ["#to-bool", "${z}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"z":"False"}', template])
            self.assertEqual('{"x":false}\n',
                             output, f'test_tobool_false - {lang}')

    def test_tobool_invalid_str(self):
        """
        Test resolving templates with to-bool rule.
        """
        template = '{"x": ["#to-bool", "${z}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"z":"Not a bool"}', template])
            self.assertEqual('Tag "to-bool" invalid string "Not a bool"\n',
                             output, f'test_tobool_invalid_str - {lang}')

    def test_tofloat(self):
        """
        Test resolving templates with to-float rule.
        """
        template = '{"x": ["#to-float", "${z}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"z":"3.14"}', template])
            self.assertEqual('{"x":3.14}\n',
                             output, f'test_tofloat - {lang}')

    def test_tofloat_invalid_str(self):
        """
        Test resolving templates with to-float rule.
        """
        template = '{"x": ["#to-float", "${z}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"z":"abc"}', template])
            self.assertEqual('Tag "to-float" invalid string "abc"\n',
                             output, f'test_tofloat_invalid_str - {lang}')

    def test_toint(self):
        """
        Test resolving templates with to-int rule.
        """
        template = '{"x": ["#to-int", "${z}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"z":"100"}', template])
            self.assertEqual('{"x":100}\n',
                             output, f'test_toint - {lang}')

    def test_toint_invalid_str(self):
        """
        Test resolving templates with to-int rule.
        """
        template = '{"x": ["#to-int", "${z}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"z":"abc"}', template])
            self.assertEqual('Tag "to-int" invalid string "abc"\n',
                             output, f'test_toint_invalid_str - {lang}')

    def test_tonull(self):
        """
        Test resolving templates with to-int rule.
        """
        template = '{"x": ["#to-null", "${z}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"z":"Null"}', template])
            self.assertEqual('{"x":null}\n',
                             output, f'test_tonull - {lang}')

    def test_tonull_invalid_str(self):
        """
        Test resolving templates with to-int rule.
        """
        template = '{"x": ["#to-null", "${z}"]}'
        for lang in TestJsonteng.lang_types:
            output = _run_test(lang, ["-r", "-b", '{"z":"xyz"}', template])
            self.assertEqual('Tag "to-null" invalid string "xyz"\n',
                             output, f'test_tonull_invalid_str - {lang}')
