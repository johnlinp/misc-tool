#!/usr/bin/env python3

import sys
import argparse
import logging
import csv


class ChaseStatement:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description='Parse a statement from Chase Bank.')

        parser.add_argument('--input-file-paths', '-i', type=str, required=True, nargs='+', help='The list of input files to parse')
        parser.add_argument('--output-file-path', '-o', type=str, required=True, help='The output file to parse')

        return parser.parse_args()

    @staticmethod
    def run(args):
        ChaseStatement._config_logging()

        statement_data = ChaseStatement._parse_statement(args.input_file_paths)
        ChaseStatement._write_records(statement_data, args.output_file_path)

    @staticmethod
    def _config_logging():
        log_level = logging.INFO
        log_format = '%(levelname)s: %(message)s'
        logging.basicConfig(level=log_level, format=log_format)

    @staticmethod
    def _parse_statement(input_file_paths):
        statement_data = []
        for input_file_path in input_file_paths:
            with open(input_file_path) as f:
                lines = f.readlines()

            if len(lines) % 3 != 0:
                raise Error('the number of lines are unexpected')

            num_records = len(lines) // 3
            dates = lines[:num_records]
            descriptions = lines[num_records:num_records * 2]
            amounts = lines[num_records * 2:]
            for entry in zip(dates, descriptions, amounts):
                statement_data.append({
                    'date': entry[0].strip(),
                    'description': ChaseStatement._big_camel(entry[1].strip()),
                    'amount': entry[2].strip()
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
    args = ChaseStatement.parse_args()
    ChaseStatement.run(args)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Error as e:
        logging.error(e)
        sys.exit(1)
