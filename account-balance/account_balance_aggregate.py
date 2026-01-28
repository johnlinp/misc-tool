#!/usr/bin/env python3

import os
import sys
import re
import argparse
import logging
import csv

class AccountBalanceAggregate:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description='Aggregate the account balanace information.')

        parser.add_argument('--input-file-path', '-i', action='append', help='Input account balance file, can specify multiple times')
        parser.add_argument('--output-file-path', '-o', help='Output account balance file')
        parser.add_argument('--verbose', '-v', action='store_true', help='When you want to debug')

        return parser.parse_args()

    @staticmethod
    def run(args):
        AccountBalanceAggregate._check_args(args)

        balance_summary = {}
        for input_file_path in args.input_file_path:
            input_balance_summary = AccountBalanceAggregate._read_balance_summary(input_file_path)
            AccountBalanceAggregate._add_balance_summary(balance_summary, input_balance_summary)

        AccountBalanceAggregate._write_balance_summary(balance_summary, args.output_file_path)

    @staticmethod
    def _read_balance_summary(input_file_path):
        with open(input_file_path) as f:
            reader = csv.reader(f)
            rows = list(reader)
            rows.pop(0)
            return rows

    @staticmethod
    def _write_balance_summary(balance_summary, output_file_path):
        with open(output_file_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'balance'])
            for entry in sorted(balance_summary.items()):
                writer.writerow([entry[0], entry[1]])

    @staticmethod
    def _add_balance_summary(balance_summary, input_balance_summary):
        for entry in input_balance_summary:
            date = AccountBalanceAggregate._to_month(entry[0])
            balance = entry[1]

            if date not in balance_summary:
                balance_summary[date] = '0.00'

            balance_summary[date] = AccountBalanceAggregate._add_money(balance_summary[date], balance)

    @staticmethod
    def _to_month(full_date):
        match = re.match(r'^(\d+)/(\d+)/\d+$', full_date)
        if not match:
            raise Error(f'unexpected date format: {full_date}')
        year = match.group(1)
        month = match.group(2)
        return f'{year}/{month}'

    @staticmethod
    def _check_money_format(money):
        match = re.match(r'^\d+\.\d\d$', money)
        if not match:
            raise Error(f'unexpected money format: {money}')

    @staticmethod
    def _add_money(money1, money2):
        AccountBalanceAggregate._check_money_format(money1)
        AccountBalanceAggregate._check_money_format(money2)

        no_dot_money1 = re.sub(r'\.', '', money1)
        no_dot_money2 = re.sub(r'\.', '', money2)

        no_dot_money_sum = str(int(no_dot_money1) + int(no_dot_money2))
        return f'{no_dot_money_sum[:-2]}.{no_dot_money_sum[-2:]}'

    @staticmethod
    def _check_args(args):
        if not args.input_file_path:
            raise Error('please specify --input-file-path')
        if not args.output_file_path:
            raise Error('please specify --output-file-path')

    @staticmethod
    def _config_logging(verbose):
        log_level = logging.DEBUG if verbose else logging.INFO
        log_format = '%(levelname)s: %(message)s'
        logging.basicConfig(level=log_level, format=log_format)


class Error(Exception):
    pass


def main():
    args = AccountBalanceAggregate.parse_args()
    AccountBalanceAggregate.run(args)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Error as e:
        logging.error(e)
        sys.exit(1)
