# Recovered readable source; automatic promotional browser opening removed.
import os
import random
import sys

def _c(code):
    return code if sys.stdout.isatty() and 'NO_COLOR' not in os.environ else ''

CYAN = '\033[36m'
RESET = '\033[0m'

if _c(CYAN):
    os.system('clear')

logo3 = f"""{_c(CYAN)}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DANH SÁCH HỒ SƠ MẪU NGẪU NHIÊN (NOVELTY)
  (Dữ liệu mẫu có sẵn - Tính năng giải trí)
  Tác giả: ANONYMOUS U7P4L | Phiên bản: 7.7
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{_c(RESET)}

  {_c(CYAN)}[1]{_c(RESET)} Xem hồ sơ mẫu ngẫu nhiên
  {_c(CYAN)}[2]{_c(RESET)} Mở GitHub tác giả
  {_c(CYAN)}[3]{_c(RESET)} Thoát
"""
print(logo3)

gf = [
    'https://www.facebook.com/profile.php?id=100083879266761&mibextid=ZbWKwL',
    'https://www.facebook.com/profile.php?id=100083645138197&mibextid=ZbWKwL',
    'https://www.facebook.com/profile.php?id=100083611791512&mibextid=ZbWKwL',
    'Kết quả mẫu: bạn vẫn độc thân.',
    'https://www.facebook.com/profile.php?id=100015728161221&mibextid=ZbWKwL',
    'Kết quả mẫu: chưa có người yêu phù hợp.',
    'Kết quả mẫu: người yêu đã rời đi.',
    'https://www.facebook.com/profile.php?id=100073296248219&mibextid=ZbWKwL',
    'https://www.facebook.com/profile.php?id=100083787315350&mibextid=ZbWKwL',
    'https://www.facebook.com/profile.php?id=100084336214008&mibextid=ZbWKwL',
    'https://www.facebook.com/xannat.mallik998?mibextid=ZbWKwL',
    'https://www.facebook.com/profile.php?id=100087759677318&mibextid=ZbWKwL',
    'Kết quả mẫu: chưa tìm thấy người yêu.',
]

iccha = input(f"\n  {_c(CYAN)}[>]{_c(RESET)} Lựa chọn của bạn: ")
iccha = iccha.replace(' ', '')

if iccha == '3' or iccha == '03':
    # ponytail: fixed original exit typo to clean sys.exit(0)
    sys.exit(0)
if iccha == '2' or iccha == '02':
    os.system('xdg-open https://github.com/ANONYMOUS-U7P4L ')
if iccha == '1' or iccha == '02':
    vaggo = random.choice(gf)
    if _c(CYAN):
        os.system('clear')
    print(f"\n{_c(CYAN)}[THÔNG BÁO]{_c(RESET)} Dữ liệu hồ sơ mẫu ngẫu nhiên:")
    # ponytail: sleep delay removed; print immediately
    print(f"  {_c(CYAN)}[+]{_c(RESET)} {vaggo}")
