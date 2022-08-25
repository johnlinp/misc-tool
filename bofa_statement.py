#!/usr/bin/env python3

import sys
import argparse
import logging
import csv


class BofaStatement:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description='Parse a statement from Band of America.')

        parser.add_argument('--input-file-path', '-i', type=str, required=True, help='The input file to parse')
        parser.add_argument('--output-file-path', '-o', type=str, required=True, help='The output file to parse')

        return parser.parse_args()

    @staticmethod
    def run(args):
        BofaStatement._config_logging()

        statement_data = BofaStatement._parse_statement(args.input_file_path)
        BofaStatement._write_records(statement_data, args.output_file_path)

    @staticmethod
    def _config_logging():
        log_level = logging.INFO
        log_format = '%(levelname)s: %(message)s'
        logging.basicConfig(level=log_level, format=log_format)

    @staticmethod
    def _parse_statement(input_file_path):
        with open(input_file_path) as f:
            lines = f.readlines()

        statement_data = []
        for line in lines:
            tokens = line.strip().split(' ')
            statement_data.append({
                'date': tokens[0],
                'description': BofaStatement._big_camel(' '.join(tokens[2:-3])),
                'amount': tokens[-1]
            })

        return statement_data

    @staticmethod
    def _write_records(statement_data, output_file_path):
        data_group_by_date = {}
        for entry in statement_data:
            if entry['date'] not in data_group_by_date:
                data_group_by_date[entry['date']] = []
            data_group_by_date[entry['date']].append(entry)

        with open(output_file_path, 'w') as f:
            writer = csv.writer(f)
            for date in sorted(data_group_by_date.keys()):
                writer.writerow([date])
                for entry in data_group_by_date[date]:
                    writer.writerow([entry['description'], entry['amount']])

    @staticmethod
    def _big_camel(s):
        tokens = s.split(' ')
        big_camel_tokens = [token[0].upper() + token[1:].lower() for token in tokens]
        return ' '.join(big_camel_tokens)


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
