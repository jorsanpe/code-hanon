# Copyright (C) Jordi Sánchez 2024
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import termios
import tty
from termcolor import colored
from code_hanon import statistics_repository
from code_hanon.practice_session import PracticeSession


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def start(input_directory, config):
    statistics_repository.prepare()
    session = PracticeSession(input_directory, config)
    count = config['count']

    for challenge, next_challenge in session.challenges():
        if next_challenge:
            text = colored(f"{challenge.string}\n{next_challenge.string}", "light_grey")
            sys.stdout.write(text + "\r\033[1A")
        else:
            text = colored(f"{challenge.string}", "light_grey")
            sys.stdout.write(text + "\r")

        sys.stdout.flush()
        ok_chars = [False] * len(challenge.string)
        pos = 0

        while True:
            char = getch()
            if is_ctrl_c(char):
                session.finish()
                sys.exit(1)
            if is_backspace(char):
                if pos > 0:
                    pos -= 1
                    sys.stdout.write(f"\b{colored(challenge.string[pos], 'light_grey')}\b")
            elif char == challenge.string[pos]:
                sys.stdout.write(colored(char, "green"))
                ok_chars[pos] = True
                pos += 1
                session.valid_input(pos-1)
            else:
                sys.stdout.write(colored(challenge.string[pos], "red"))
                pos += 1
                session.invalid_input(pos-1)
            sys.stdout.flush()

            if pos == len(challenge.string):
                if session.challenge_ok():
                    print(colored(" ✓", "green"))
                else:
                    print(colored(" x", "red"))
                session.challenge_end()
                break
    session.finish()


def is_backspace(char):
    return char == "\x7f"


def is_ctrl_c(char):
    return char == "\x03"
