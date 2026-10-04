# Recovered readable source; automatic installs, promotion and hidden POST removed.
import json
import os
import re
import sys

try:
    import bs4
    import requests
except ModuleNotFoundError:
    print('\n[LỖI] THIẾU THƯ VIỆN: Vui lòng cài đặt requests và beautifulsoup4 trước khi chạy.')
    sys.exit(1)

def _c(code):
    return code if sys.stdout.isatty() and 'NO_COLOR' not in os.environ else ''

CYAN = '\033[36m'
RESET = '\033[0m'

logo = f"""{_c(CYAN)}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FB AUTO COMMENT - TỰ ĐỘNG BÌNH LUẬN FB
  Phiên bản: 1.0.3 | Tác giả: U7P4L-IN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{_c(RESET)}"""

def clear():
    if _c(CYAN):
        os.system('clear')
    print(logo)

try:
    from concurrent.futures import ThreadPoolExecutor as tred
except ModuleNotFoundError:
    print('\n[LỖI] THIẾU THƯ VIỆN: Vui lòng sử dụng Python 3 có sẵn concurrent.futures.')
    sys.exit(1)
except:
    pass  # Preserve the original optional-import fallback.

def linex():
    print(f"{_c(CYAN)}──────────────────────────────────────────{_c(RESET)}")

def menu():
    clear()
    linex()
    print(f" {_c(CYAN)}[01/A]{_c(RESET)} Bắt đầu tự động bình luận")
    print(f" {_c(CYAN)}[00/X]{_c(RESET)} Thoát chương trình")
    linex()
    option = input(f" {_c(CYAN)}[>]{_c(RESET)} Lựa chọn: ")
    if option in ('1', '01', 'A', 'a'):
        login()
        return None
    if option in ('0', '00', 'x', 'X'):
        print(f" {_c(CYAN)}[THOÁT]{_c(RESET)} Đã thoát chương trình.")
        print(f" {_c(CYAN)}[CẢM ƠN]{_c(RESET)} Cảm ơn bạn đã sử dụng công cụ!")
        exit(0)
    print(f" {_c(CYAN)}[LỖI]{_c(RESET)} Tùy chọn không hợp lệ trong menu...")
    menu()
    return None

def login():
    clear()
    linex()
    cookie = input(f" {_c(CYAN)}[>]{_c(RESET)} Nhập Cookie Facebook: ")
    try:
        cari = requests.get('https://business.facebook.com/business_locations', headers={'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; MI 8 Build/OPM1.171019.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.86 Mobile Safari/537.36', 'cookie': cookie})
        token = re.search(r'(EAAG\w+)', cari.text).group(1)
        if 'EAAG' in str(token):
            open('cookie.txt', 'w').write(cookie)
            open('token.txt', 'w').write(token)
            print(f"\n {_c(CYAN)}[THÔNG TIN]{_c(RESET)} Đăng nhập thành công.")
            linex()
            comment()
    except AttributeError:
        exit(f"\n {_c(CYAN)}[LỖI]{_c(RESET)} Cookie đã hết hạn hoặc không hợp lệ!")
        linex()
    except requests.exceptions.ConnectionError:
        print(f"\n {_c(CYAN)}[LỖI]{_c(RESET)} Không có kết nối mạng...")
        exit()

def comment():
    cookie = open('cookie.txt', 'r').read()
    token = open('token.txt', 'r').read()
    clear()
    linex()
    try:
        id = input(f" {_c(CYAN)}[>]{_c(RESET)} Nhập ID bài viết: ")
        comment = input(f" {_c(CYAN)}[>]{_c(RESET)} Nhập nội dung bình luận: ")
        limit = int(input(f" {_c(CYAN)}[>]{_c(RESET)} Nhập số lượng bình luận: "))
        linex()
        for x in range(limit):
            posting = requests.post('https://graph.facebook.com/' + str(id) + '/comments/?message=' + str(comment) + '&access_token=' + str(token), cookies={'cookie': cookie})
            cek = json.loads(posting.text)
            if 'id' in cek:
                print(f" {_c(CYAN)}[THÀNH CÔNG]{_c(RESET)} ID: {cek['id']} (Lần {x + 1}/{limit})")
            else:
                print(f" {_c(CYAN)}[THẤT BẠI]{_c(RESET)} Không thể gửi bình luận!")
                exit()
        print(f" {_c(CYAN)}[HOÀN TẤT]{_c(RESET)} Đã hoàn thành gửi bình luận.")
        print(f" {_c(CYAN)}[THÔNG TIN]{_c(RESET)} Nhấn Enter để quay lại menu chính...")
        input(f" {_c(CYAN)}──────────────────────────────────────────{_c(RESET)}")
        menu()
    except requests.exceptions.ConnectionError:
        print(f"\n {_c(CYAN)}[LỖI]{_c(RESET)} Không có kết nối mạng...")
        exit()

menu()
