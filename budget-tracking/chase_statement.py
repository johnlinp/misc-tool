#!/usr/bin/env python3

import sys
import argparse
import re
import logging
import csv


class ChaseStatement:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description='Parse a statement from Chase Bank.')

        parser.add_argument('--input-file-paths', '-i', type=str, required=True, nargs='+', help='The list of input files to parse')
        parser.add_argument('--output-file-path', '-o', type=str, required=True, help='The output file to parse')
        parser.add_argument('--description-conversion-file-path', '-d', type=str, required=False, help='The description conversion file')

        return parser.parse_args()

    @staticmethod
    def run(args):
        ChaseStatement._config_logging()

        statement_data = ChaseStatement._parse_statement(args.input_file_paths)
        if args.description_conversion_file_path:
            statement_data = ChaseStatement._convert_descriptions(statement_data, args.description_conversion_file_path)
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
                    'description': entry[1].strip(),
                    'amount': entry[2].strip()
                })

        return statement_data

    @staticmethod
    def _convert_descriptions(statement_data, description_conversion_file_path):
        with open(description_conversion_file_path) as f:
            reader = csv.DictReader(f)

            description_conversions = {}
            for row in reader:
                description_conversions[row['Description Regex Pattern']] = row['Substituting Name']

        return [ChaseStatement._convert_entry_description(entry, description_conversions) for entry in statement_data]

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
    args = ChaseStatement.parse_args()
    ChaseStatement.run(args)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Error as e:
        logging.error(e)
        sys.exit(1)
