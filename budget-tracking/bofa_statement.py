#!/usr/bin/env python3

import sys
import argparse
import re
import logging
import csv


class BofaStatement:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description='Parse a statement from Bank of America.')

        parser.add_argument('--input-file-path', '-i', type=str, required=True, help='The input file to parse')
        parser.add_argument('--output-file-path', '-o', type=str, required=True, help='The output file')
        parser.add_argument('--description-conversion-file-path', '-d', type=str, required=False, help='The description conversion file')

        return parser.parse_args()

    @staticmethod
    def run(args):
        BofaStatement._config_logging()

        statement_data = BofaStatement._parse_statement(args.input_file_path)
        if args.description_conversion_file_path:
            statement_data = BofaStatement._convert_descriptions(statement_data, args.description_conversion_file_path)
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
                'description': ' '.join(tokens[2:-3]),
                'amount': tokens[-1]
            })

        return statement_data

    @staticmethod
    def _convert_descriptions(statement_data, description_conversion_file_path):
        with open(description_conversion_file_path) as f:
            reader = csv.DictReader(f)

            description_conversions = {}
            for row in reader:
                description_conversions[row['Description Regex Pattern']] = row['Substituting Name']

        return [BofaStatement._convert_entry_description(entry, description_conversions) for entry in statement_data]

    @staticmethod
    def _convert_entry_description(entry, description_conversions):
        for pattern in description_conversions:
            if re.search(pattern, entry['description']):
                return {
                    'date': entry['date'],
                    'description': description_conversions[pattern],
                    'amount': entry['amount'],
                }
        return entry

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
