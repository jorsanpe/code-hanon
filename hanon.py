#!/usr/bin/env python3
import argparse
import sys
from code_hanon import analyzer
from code_hanon import languages
from code_hanon import practice
from code_hanon import statistics_presenter


def print_help():
    help_text = 'Usage: code-hanon <command> [args]'
    help_text += '\n\nAvailable commands:'
    help_text += f'\n\t{"analyze":<20} Analyze a codebase and extract generator expressions'
    help_text += f'\n\t{"practice":<20} Practice coding using generator expressions'
    help_text += f'\n\t{"stats":<20} Show your performance statistics'
    print(help_text)


def analyze(argv):
    options = argparse.ArgumentParser(description='analyze frequency of code expressions by line')
    options.add_argument('-l', '--language', action='store', choices=languages.supported.keys())
    options.add_argument(
        '-o', '--output',
        default="exercises",
        action='store',
        help="output directory where to leave the analysis result files (exercises.txt, words.txt and names.txt)"
    )
    options.add_argument('directories', nargs=argparse.REMAINDER)

    args = options.parse_args(argv)

    analyzer.analyze(args.language, args.directories, args.output)


def start_practice(argv):
    options = argparse.ArgumentParser(description='practice coding based on generator expressions')
    options.add_argument(
        '-i', '--input-directory',
        default="exercises",
        action='store',
        help="input directory from which to read the generator files (exercises.txt, words.txt and names.txt)"
    )
    options.add_argument(
        '-c', '--count',
        default=25,
        action='store',
        type=int,
        help="how many string challenges to generate for the exercise (default 25)"
    )

    args = options.parse_args(argv)

    practice.start(args.input_directory, int(args.count))


def show_stats(argv):
    options = argparse.ArgumentParser(description='show your current performance statistics')
    options.add_argument(
        '-s', '--sort-by',
        default="latency",
        choices=['latency', 'error_rate'],
        action='store',
        help="input directory from which to read the generator files (exercises.txt, words.txt and names.txt)"
    )

    args = options.parse_args(argv)

    statistics_presenter.present(args.sort_by)


COMMANDS = {
    "help": print_help,
    "analyze": analyze,
    "practice": start_practice,
    "stats": show_stats
}


def main():
    top_level_parser = argument_parser()
    args = top_level_parser.parse_args(sys.argv[1:])

    if not args.command:
        print_help()
        sys.exit(0)

    command_to_execute = args.command[0]
    command_arguments = args.command[1:]
    COMMANDS[command_to_execute](command_arguments)


def argument_parser():
    top_level_parser = argparse.ArgumentParser(description='hanon: ')
    top_level_parser.add_argument('command',
                                  choices=list(COMMANDS.keys()) + ['help'],
                                  nargs=argparse.REMAINDER)
    return top_level_parser


if __name__ == '__main__':
    main()
