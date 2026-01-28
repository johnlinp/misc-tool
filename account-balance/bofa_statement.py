#!/usr/bin/env python3

import sys
import os
import re
import argparse
import logging
import csv
import pdfplumber


class BofaStatement:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description='Extract the account balance summary from statements')

        parser.add_argument('--input-directory-path', '-i', help='The input directory of statements')
        parser.add_argument('--output-file-path', '-o', help='The output file of account balance summary')
        parser.add_argument('--verbose', '-v', action='store_true', help='When you want to debug')

        return parser.parse_args()

    @staticmethod
    def run(args):
        BofaStatement._config_logging(args.verbose)

        BofaStatement._check_args(args)

        balance_summary = []
        for statement_file_path in BofaStatement._list_file_paths(args.input_directory_path):
            logging.info(f'processing statement file "{statement_file_path}"...')
            text = BofaStatement._retrieve_text(statement_file_path)
            date = BofaStatement._extract_date(text)
            balance = BofaStatement._extract_balance(text)
            balance_summary.append([date, balance])

        BofaStatement._write_balance_summary(balance_summary, args.output_file_path)

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
            match = re.search(r'^for .* to (.*) Account number: .*$', line)
            if not match:
                continue
            return BofaStatement._normalize_date(match.group(1))
        raise Error('date not found')

    @staticmethod
    def _normalize_date(human_date):
        match = re.match(r'^(\w+) (\d+), (\d+)$', human_date)
        if not match:
            raise Error(f'unexpected date format: {human_date}')
        month = BofaStatement._normalize_month(match.group(1))
        day = BofaStatement._normalize_day(match.group(2))
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
    def _extract_balance(text):
        lines = re.split('\n', text)
        for line in lines:
            match = re.search(r'^Ending balance on .* \$(.*)$', line)
            if not match:
                continue
            return BofaStatement._normalize_money(match.group(1))
        raise Error('balance not found')

    @staticmethod
    def _normalize_money(human_money):
        no_comma_money = re.sub(',', '', human_money)
        match = re.match(r'^\d+\.\d\d$', no_comma_money)
        if not match:
            raise Error(f'unexpected money format: {human_money}')
        return no_comma_money

    @staticmethod
    def _get_account_type_mark(account_type):
        mapping = {
            'checking': 'CHECKING SUMMARY',
            'savings': 'SAVINGS SUMMARY',
        }
        return mapping[account_type]

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

    @staticmethod
    def _config_logging(verbose):
        log_level = logging.DEBUG if verbose else logging.INFO
        log_format = '%(levelname)s: %(message)s'
        logging.basicConfig(level=log_level, format=log_format)


class Error(Exception):
    pass


def main():
    args = BofaStatement.parse_args()
    BofaStatement.run(args)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Error as e:
        logging.error(e)
        sys.exit(1)
