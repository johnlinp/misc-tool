#!/usr/bin/env python3

import sys
import os
import re
import argparse
import logging
import csv
import pdfplumber


class ChaseStatement:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description='Extract the account balance summary from statements')

        parser.add_argument('--input-directory-path', '-i', help='The input directory of statements')
        parser.add_argument('--output-file-path', '-o', help='The output file of account balance summary')
        parser.add_argument('--account-type', '-t', choices=['checking', 'savings'], help='The account type to look at')
        parser.add_argument('--verbose', '-v', action='store_true', help='When you want to debug')

        return parser.parse_args()

    @staticmethod
    def run(args):
        ChaseStatement._config_logging(args.verbose)

        ChaseStatement._check_args(args)

        balance_summary = []
        for statement_file_path in ChaseStatement._list_file_paths(args.input_directory_path):
            logging.info(f'processing statement file "{statement_file_path}"...')
            text = ChaseStatement._retrieve_text(statement_file_path)
            date = ChaseStatement._extract_date(text)
            balance = ChaseStatement._extract_balance(text, args.account_type)
            balance_summary.append([date, balance])

        ChaseStatement._write_balance_summary(balance_summary, args.output_file_path)

    @staticmethod
    def _list_file_paths(dir_path):
        file_paths = []
        for filename in os.listdir(dir_path):
            file_paths.append(os.path.join(dir_path, filename))
        return file_paths

    @staticmethod
    def _retrieve_text(pdf_file_path):
        with pdfplumber.open(pdf_file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
            return text

    @staticmethod
    def _extract_date(text):
        lines = re.split('\n', text)
        for line in lines:
            match = re.search(r'^.*through(.*)$', line)
            if not match:
                continue
            return ChaseStatement._normalize_date(match.group(1))
        raise Error('date not found')

    @staticmethod
    def _normalize_date(human_date):
        match = re.match(r'^(\w+) (\d+), (\d+)$', human_date)
        if not match:
            raise Error(f'unexpected date format: {human_date}')
        month = ChaseStatement._normalize_month(match.group(1))
        day = ChaseStatement._normalize_day(match.group(2))
        year = match.group(3)
        return f'{year}/{month}/{day}'

    @staticmethod
    def _normalize_month(human_month):
        mapping = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12',
        }
        return mapping[human_month]

    @staticmethod
    def _normalize_day(human_day):
        if len(human_day) == 2:
            return human_day
        if len(human_day) == 1:
            return f'0{human_day}'
        raise Error('unexpected day format: {human_day}')

    @staticmethod
    def _extract_balance(text, account_type):
        lines = re.split('\n', text)
        account_type_mark = ChaseStatement._get_account_type_mark(account_type)
        account_type_mark_found = False
        for line in lines:
            if not account_type_mark_found:
                match = re.search(f'^{account_type_mark}$', line)
                if match:
                    account_type_mark_found = True
            else:
                match = re.search(r'^Ending Balance \$(.*)$', line)
                if not match:
                    continue
                return ChaseStatement._normalize_money(match.group(1))
        raise Error('balance not found')

    @staticmethod
    def _get_account_type_mark(account_type):
        mapping = {
            'checking': 'CHECKING SUMMARY',
            'savings': 'SAVINGS SUMMARY',
        }
        return mapping[account_type]

    @staticmethod
    def _normalize_money(human_money):
        no_comma_money = re.sub(',', '', human_money)
        match = re.match(r'^\d+\.\d\d$', no_comma_money)
        if not match:
            raise Error(f'unexpected money format: {human_money}')
        return no_comma_money

    @staticmethod
    def _write_balance_summary(balance_summary, output_file_path):
        with open(output_file_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'balance'])
            for entry in sorted(balance_summary):
                writer.writerow([entry[0], entry[1]])

    @staticmethod
    def _check_args(args):
        if not args.input_directory_path:
            raise Error('please specify --input-directory-path')
        if not args.output_file_path:
            raise Error('please specify --output-file-path')
        if not args.account_type:
            raise Error('please specify --account-type')

    @staticmethod
    def _config_logging(verbose):
        log_level = logging.DEBUG if verbose else logging.INFO
        log_format = '%(levelname)s: %(message)s'
        logging.basicConfig(level=log_level, format=log_format)


class Error(Exception):
    pass


def main():
    args = ChaseStatement.parse_args()
    ChaseStatement.run(args)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Error as e:
        logging.error(e)
        sys.exit(1)
