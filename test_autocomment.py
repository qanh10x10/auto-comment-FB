"""Offline only: readable source gate, fake credentials, denied external actions."""
import ast
import io
import os
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
    for name in ('clear', 'linex', 'menu'):
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
        self.assertEqual(system.call_args_list, [])

    def test_index_keeps_chosen_link(self):
        env = {'input': Mock(return_value='2'), 'print': Mock()}
        with patch('os.system', return_value=0) as system:
            exec(compile(source_tree('index.py'), 'index.py', 'exec'), env)
        self.assertEqual(system.call_args_list, [call('xdg-open https://github.com/ANONYMOUS-U7P4L ')])

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

    def test_optional_executor_keyboard_interrupt_fallback(self):
        import builtins
        original_import = builtins.__import__

        def interrupt_failure(name, *args, **kwargs):
            if name == 'concurrent.futures':
                raise KeyboardInterrupt
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=interrupt_failure):
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

    def test_admin_menu_vietnamese_labels(self):
        env = load_main()
        env['menu'] = Mock()
        env['input'].return_value = '0'
        printed = []
        env['print'] = Mock(side_effect=lambda *args: printed.append(' '.join(str(a) for a in args)))
        with patch('os.system'):
            env['admin']()
        combined = '\n'.join(printed)
        self.assertIn('Trang Facebook', combined)
        self.assertIn('Quay lại menu chính', combined)

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
        with self.assertRaisesRegex(SystemExit, 'Cookie đã hết hạn'):
            env['login']()
        requests.post.assert_not_called()
        env['open'].assert_not_called()

    def test_main_menu_vietnamese_labels_and_clean_exit(self):
        tree = source_tree('main.py')
        tree.body.pop()  # remove final menu() call
        env = {'input': Mock(return_value='0'), 'print': Mock(), 'open': Mock(), 'exit': Mock(side_effect=SystemExit(0))}
        modules = {'bs4': SimpleNamespace(), 'requests': fake_requests()}
        with patch.dict(sys.modules, modules), patch('sys.stdout', io.StringIO()):
            exec(compile(tree, 'main.py', 'exec'), env)
        printed = []
        env['print'] = Mock(side_effect=lambda *args: printed.append(' '.join(str(a) for a in args)))
        with patch('os.system') as mock_sys:
            with self.assertRaises(SystemExit) as cm:
                env['menu']()
            self.assertEqual(cm.exception.code, 0)
        combined = '\n'.join(printed)
        self.assertIn('Bắt đầu', combined)
        self.assertIn('Báo lỗi', combined)
        self.assertIn('Thoát', combined)
        self.assertNotIn('U7P4L Army', combined)

    def test_no_delays_in_menu_and_loading(self):
        tree = source_tree('main.py')
        tree.body.pop()
        env = {'input': Mock(return_value='0'), 'print': Mock(), 'open': Mock(), 'exit': Mock(side_effect=SystemExit(0))}
        modules = {'bs4': SimpleNamespace(), 'requests': fake_requests()}
        with patch.dict(sys.modules, modules), patch('sys.stdout', io.StringIO()):
            exec(compile(tree, 'main.py', 'exec'), env)
        with patch('time.sleep') as mock_sleep, patch('os.system'):
            with self.assertRaises(SystemExit) as cm:
                env['menu']()
            self.assertEqual(cm.exception.code, 0)
            mock_sleep.assert_not_called()
        self.assertNotIn('time.sleep', (ROOT / 'main.py').read_text())
        self.assertNotIn('loadinglisen', (ROOT / 'main.py').read_text())
        self.assertNotIn('jalan', (ROOT / 'main.py').read_text())

    def test_color_respects_no_color_and_nontty(self):
        tree = source_tree('main.py')
        tree.body.pop()
        env = {'input': Mock(), 'print': Mock(), 'open': Mock()}
        modules = {'bs4': SimpleNamespace(), 'requests': fake_requests()}
        with patch.dict(sys.modules, modules), patch('sys.stdout', io.StringIO()):
            exec(compile(tree, 'main.py', 'exec'), env)
        # In non-TTY or with NO_COLOR, _c should return empty string
        self.assertTrue(callable(env.get('_c')))
        with patch.dict(os.environ, {'NO_COLOR': '1'}), patch('sys.stdout.isatty', return_value=True):
            self.assertEqual(env['_c']('\033[36m'), '')
        with patch.dict(os.environ, {}, clear=True), patch('sys.stdout.isatty', return_value=False):
            self.assertEqual(env['_c']('\033[36m'), '')
        with patch.dict(os.environ, {}, clear=True), patch('sys.stdout.isatty', return_value=True):
            self.assertEqual(env['_c']('\033[36m'), '\033[36m')

    def test_index_truthful_vietnamese_and_clean_exit(self):
        printed = []
        env = {'input': Mock(return_value='3'), 'print': Mock(side_effect=lambda *args: printed.append(' '.join(str(a) for a in args)))}
        with patch('os.system', return_value=0) as system:
            with self.assertRaises(SystemExit) as cm:
                exec(compile(source_tree('index.py'), 'index.py', 'exec'), env)
            self.assertEqual(cm.exception.code, 0)
        # Should not have called os.syatem
        self.assertNotIn('syatem', (ROOT / 'index.py').read_text())
        combined = '\n'.join(printed)
        self.assertIn('DANH SÁCH HỒ SƠ MẪU NGẪU NHIÊN', combined)
        self.assertIn('Thoát', combined)
        self.assertNotIn('Start GF hack', combined)

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
        printed = []
        env['print'] = Mock(side_effect=lambda *args: printed.append(' '.join(str(a) for a in args)))
        env['comment']()
        expected = call('https://graph.facebook.com/1001/comments/?message=hello&access_token=EAAGdummy', cookies={'cookie': 'dummy-cookie'})
        self.assertEqual(requests.post.call_args_list, [expected, expected])
        env['menu'].assert_called_once_with()
        combined = '\n'.join(printed)
        self.assertIn('[THÀNH CÔNG]', combined)
        self.assertIn('[HOÀN TẤT]', combined)

    def test_rejected_comment_stops_loop(self):
        env, requests = self.comment_env(response='{"error":"denied"}')
        printed = []
        env['print'] = Mock(side_effect=lambda *args: printed.append(' '.join(str(a) for a in args)))
        with self.assertRaises(SystemExit):
            env['comment']()
        self.assertEqual(requests.post.call_count, 1)
        env['menu'].assert_not_called()
        combined = '\n'.join(printed)
        self.assertIn('[THẤT BẠI]', combined)

    def test_comment_connection_error_stops(self):
        env, requests = self.comment_env()
        requests.post.side_effect = ConnectionError
        printed = []
        env['print'] = Mock(side_effect=lambda *args: printed.append(' '.join(str(a) for a in args)))
        with self.assertRaises(SystemExit):
            env['comment']()
        self.assertEqual(requests.post.call_count, 1)
        combined = '\n'.join(printed)
        self.assertIn('[LỖI] Không có kết nối mạng', combined)

    def test_rendered_plain_and_tty_output(self):
        # 1. Plain output: non-TTY or TTY with NO_COLOR must produce NO escape sequences and invoke NO external commands
        for script, exit_input in (('main.py', '0'), ('index.py', '3')):
            for is_tty, env_dict in [(False, {}), (True, {'NO_COLOR': '1'})]:
                with self.subTest(script=script, is_tty=is_tty, env=env_dict):
                    out = io.StringIO()
                    out.isatty = lambda t=is_tty: t
                    env = {
                        'input': Mock(return_value=exit_input),
                        'print': lambda *args, **kw: out.write(' '.join(str(a) for a in args) + '\n'),
                        'open': Mock(),
                        'exit': Mock(side_effect=SystemExit(0)),
                    }
                    modules = {'bs4': SimpleNamespace(), 'requests': fake_requests()}
                    with patch.dict(os.environ, env_dict, clear=True), patch.dict(sys.modules, modules), patch('sys.stdout', out), patch('os.system') as mock_sys:
                        tree = source_tree(script)
                        if script == 'main.py':
                            tree.body.pop()  # remove final menu() call
                            exec(compile(tree, script, 'exec'), env)
                            with self.assertRaises(SystemExit):
                                env['menu']()
                        else:
                            with self.assertRaises(SystemExit):
                                exec(compile(tree, script, 'exec'), env)
                        mock_sys.assert_not_called()
                        text = out.getvalue()
                        self.assertNotIn('\x1b', text)
                        self.assertNotIn('\033', text)

        # 2. TTY normal (interactive TTY and NO_COLOR absent): clears once per screen, contains cyan escapes
        for script, exit_input in (('main.py', '0'), ('index.py', '3')):
            with self.subTest(script=script, is_tty=True, normal=True):
                out = io.StringIO()
                out.isatty = lambda: True
                env = {
                    'input': Mock(return_value=exit_input),
                    'print': lambda *args, **kw: out.write(' '.join(str(a) for a in args) + '\n'),
                    'open': Mock(),
                    'exit': Mock(side_effect=SystemExit(0)),
                }
                modules = {'bs4': SimpleNamespace(), 'requests': fake_requests()}
                with patch.dict(os.environ, {}, clear=True), patch.dict(sys.modules, modules), patch('sys.stdout', out), patch('os.system', return_value=0) as mock_sys:
                    tree = source_tree(script)
                    if script == 'main.py':
                        tree.body.pop()
                        exec(compile(tree, script, 'exec'), env)
                        with self.assertRaises(SystemExit):
                            env['menu']()
                    else:
                        with self.assertRaises(SystemExit):
                            exec(compile(tree, script, 'exec'), env)
                    self.assertEqual(mock_sys.call_args_list, [call('clear')])
                    text = out.getvalue()
                    self.assertIn('\033[36m', text)

    def test_index_preserves_random_preset_pool(self):
        env = {'input': Mock(return_value='1'), 'print': Mock()}
        with patch('sys.stdout', io.StringIO()), patch('random.choice', return_value='Kết quả mẫu') as choose:
            exec(compile(source_tree('index.py'), 'index.py', 'exec'), env)
        presets = choose.call_args.args[0]
        self.assertEqual(len(presets), 13)
        self.assertEqual(sum(item.startswith('https://') for item in presets), 9)
        self.assertTrue(all('\x1b' not in item for item in presets))

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
