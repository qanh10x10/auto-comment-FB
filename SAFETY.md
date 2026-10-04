# develop — readable source and targeted cleanup

Both entrypoints were recovered from Python 3.11 bytecode as readable Python before removing automatic actions. Original revision: `5eef7eee49967ea1570e7fc90db0d061bc3fbfad`.

Removed only:
- Unprompted promotional browser opening at index startup and main-menu entry.
- The fixed Facebook comment POST performed inside login, before the operator selects a target.
- Runtime package installation/uninstallation and the missing `sms.py` launcher. Missing dependencies now produce a message and exit.

Kept: existing terminal UI, explicit menu links, login/token extraction, and user-selected comment target/message/limit. Recovery is not the original author's source text: index recovery compiled to identical bytecode; main was reconstructed and its constants, control flow and exception handling reviewed against disassembly. Some f-string formatting appears as string concatenation.

## Offline checks

```sh
python3.11 -m unittest discover -s . -v
```

Tests reject encoded wrappers before execution, deny process/socket side effects, and use dummy credentials and fake HTTP responses. No real Facebook login/comment was used for functional verification; live API compatibility is not certified.

## Remaining original limitations

`cookie.txt` and `token.txt` still store credentials in plaintext (excluded from Git). Original menu typos/option routing and legacy request construction are preserved, not repaired by this narrowly scoped change. Do not treat this cleanup as a comprehensive security hardening or a guarantee the Facebook API still accepts this flow.

## Audit exception

During the coder's initial RED test, an incorrectly mocked import boundary executed the original `index.py` wrapper. It can clear the terminal and invoke the promotional browser opener. No account cookie/token was supplied, and the original `main.py` payload was not executed by that test. The final test harness refuses wrappers before loading source and denies external actions.
