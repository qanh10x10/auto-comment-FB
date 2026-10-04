"""Offline only: readable source gate, fake credentials, denied external actions."""
import ast
import io
import sys
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

ROOT = Path(__file__).resolve().parent


def source_tree(name):
    tree = ast.parse((ROOT / name).read_text(), filename=name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            assert node.id not in {'exec', 'eval', 'marshal', '__import__', 'b64decode', 'decompress'}, 'Encoded source is never executed'
        if isinstance(node, ast.Constant):
            assert not isinstance(node.value, bytes), 'Binary payload is never executed'
    return tree


def fake_requests():
    return SimpleNamespace(
        get=Mock(side_effect=AssertionError('Unexpected GET')),
        post=Mock(side_effect=AssertionError('Unexpected POST')),
        exceptions=SimpleNamespace(ConnectionError=ConnectionError),
    )


def load_main(requests=None, missing=False):
    tree = source_tree('main.py')
    last = tree.body.pop()
    assert isinstance(last, ast.Expr) and isinstance(last.value, ast.Call)
    assert isinstance(last.value.func, ast.Name) and last.value.func.id == 'menu'
    env = {'input': Mock(), 'print': Mock(), 'open': Mock()}
    modules = {'bs4': None if missing else SimpleNamespace(), 'requests': requests or fake_requests()}
    with patch.dict(sys.modules, modules), patch('sys.stdout', io.StringIO()):
        exec(compile(tree, 'main.py', 'exec'), env)
    for name in ('clear', 'linex', 'loadinglisen', 'jalan', 'menu'):
        env[name] = Mock()
    # Keep the real menu for explicit dispatch testing without calling startup.
    menu_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'menu')
    exec(compile(ast.Module(body=[menu_node], type_ignores=[]), 'main.py', 'exec'), env)
    return env


class OfflineChecks(unittest.TestCase):
    def setUp(self):
        self.guards = ExitStack()
        self.addCleanup(self.guards.close)
        for target in ('os.system', 'subprocess.Popen', 'socket.create_connection', 'socket.socket.connect'):
            self.guards.enter_context(patch(target, side_effect=AssertionError('External action denied')))
        self.guards.enter_context(patch('time.sleep'))

    def test_readable_and_no_unintended_actions(self):
        for name in ('index.py', 'main.py'):
            source_tree(name)
            text = (ROOT / name).read_text()
            for forbidden in ('pip install', 'pip uninstall', 'sms.py', 'gua pake script lu bang', '100089033379675_161391613505284'):
                self.assertNotIn(forbidden, text)

    def test_index_does_not_open_browser_unprompted(self):
        env = {'input': Mock(return_value='invalid'), 'print': Mock()}
        with patch('os.system', return_value=0) as system:
            exec(compile(source_tree('index.py'), 'index.py', 'exec'), env)
        self.assertEqual(system.call_args_list, [call('clear')])

    def test_index_keeps_chosen_link(self):
        env = {'input': Mock(return_value='2'), 'print': Mock()}
        with patch('os.system', return_value=0) as system:
            exec(compile(source_tree('index.py'), 'index.py', 'exec'), env)
        self.assertEqual(system.call_args_list, [call('clear'), call('xdg-open https://github.com/ANONYMOUS-U7P4L ')])

    def test_missing_dependency_exits_without_auto_install(self):
        with self.assertRaises(SystemExit) as error:
            load_main(missing=True)
        self.assertEqual(error.exception.code, 1)
        self.assertNotIn('INSTALLING MISSING', (ROOT / 'main.py').read_text())

    def test_optional_executor_keeps_original_non_module_error_handling(self):
        import builtins
        original_import = builtins.__import__

        def import_failure(name, *args, **kwargs):
            if name == 'concurrent.futures':
                raise RuntimeError('optional executor unavailable')
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=import_failure):
            env = load_main()
        self.assertTrue(callable(env['login']))

    def test_main_menu_starts_login_only_when_chosen(self):
        env = load_main()
        env['input'].return_value = '1'
        env['login'] = Mock()
        env['menu']()
        env['login'].assert_called_once_with()

    def test_admin_keeps_all_chosen_links(self):
        for option, url in [('1', 'https://www.facebook.com/U7P4L.XR'), ('2', 'https://facebook.com/groups/anonymouscyberxd/'), ('3', 'https://t.me/TheU7p4lArmyX'), ('4', 'https://github.com/U7P4L-IN')]:
            with self.subTest(option=option):
                env = load_main()
                env['menu'] = Mock()
                env['input'].return_value = option
                with patch('os.system', return_value=0) as system:
                    env['admin']()
                system.assert_called_once_with('xdg-open ' + url)

    def test_login_never_posts_and_preserves_credentials(self):
        requests = fake_requests()
        requests.get.side_effect = None
        requests.get.return_value = SimpleNamespace(text='EAAG123dummy')
        env = load_main(requests)
        env['input'].return_value = 'dummy-cookie'
        env['open'].side_effect = lambda name, mode: files[name]
        files = {'cookie.txt': Mock(), 'token.txt': Mock()}
        env['comment'] = Mock()
        env['login']()
        requests.post.assert_not_called()
        self.assertEqual(requests.get.call_args.args, ('https://business.facebook.com/business_locations',))
        self.assertEqual(requests.get.call_args.kwargs['headers']['cookie'], 'dummy-cookie')
        files['cookie.txt'].write.assert_called_once_with('dummy-cookie')
        files['token.txt'].write.assert_called_once_with('EAAG123dummy')
        env['comment'].assert_called_once_with()

    def test_invalid_cookie_exits_without_post_or_file_write(self):
        requests = fake_requests()
        requests.get.side_effect = None
        requests.get.return_value = SimpleNamespace(text='no-token')
        env = load_main(requests)
        env['input'].return_value = 'dummy-cookie'
        with self.assertRaisesRegex(SystemExit, 'COOKIES HAVE EXPIRED'):
            env['login']()
        requests.post.assert_not_called()
        env['open'].assert_not_called()

    def test_login_connection_error_exits_without_post(self):
        requests = fake_requests()
        requests.get.side_effect = ConnectionError
        env = load_main(requests)
        with self.assertRaises(SystemExit):
            env['login']()
        requests.post.assert_not_called()
        env['open'].assert_not_called()

    def comment_env(self, response='{"id":"dummy-result"}', limit='2'):
        requests = fake_requests()
        requests.post.side_effect = None
        requests.post.return_value = SimpleNamespace(text=response)
        env = load_main(requests)
        env['menu'] = Mock()
        env['input'].side_effect = ['1001', 'hello', limit, '']
        env['open'].side_effect = lambda name, mode: io.StringIO('dummy-cookie' if name == 'cookie.txt' else 'EAAGdummy')
        return env, requests

    def test_chosen_comment_target_message_limit_and_cookies(self):
        env, requests = self.comment_env()
        env['comment']()
        expected = call('https://graph.facebook.com/1001/comments/?message=hello&access_token=EAAGdummy', cookies={'cookie': 'dummy-cookie'})
        self.assertEqual(requests.post.call_args_list, [expected, expected])
        env['menu'].assert_called_once_with()

    def test_rejected_comment_stops_loop(self):
        env, requests = self.comment_env(response='{"error":"denied"}')
        with self.assertRaises(SystemExit):
            env['comment']()
        self.assertEqual(requests.post.call_count, 1)
        env['menu'].assert_not_called()

    def test_comment_connection_error_stops(self):
        env, requests = self.comment_env()
        requests.post.side_effect = ConnectionError
        with self.assertRaises(SystemExit):
            env['comment']()
        self.assertEqual(requests.post.call_count, 1)

    def test_zero_limit_does_not_post(self):
        env, requests = self.comment_env(limit='0')
        env['comment']()
        requests.post.assert_not_called()

    def test_invalid_limit_keeps_original_value_error_without_post(self):
        env, requests = self.comment_env(limit='not-a-number')
        with self.assertRaises(ValueError):
            env['comment']()
        requests.post.assert_not_called()


if __name__ == '__main__':
    unittest.main()
