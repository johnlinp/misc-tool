#!/usr/bin/env python3

import sys
import argparse
import re
import logging
import csv


class Combine:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description='Combine budget tracking spreadsheets.')

        parser.add_argument('--input-file-path', '-i', type=str, required=True, action='append', help='The input file to combine')
        parser.add_argument('--output-file-path', '-o', type=str, required=True, help='The output file')

        return parser.parse_args()

    @staticmethod
    def run(args):
        Combine._config_logging()

        budget_tracking_spreadsheets = Combine._read_budget_tracking_spreadsheets(args.input_file_path)
        budget_tracking_spreadsheet = Combine._combine_budget_tracking_spreadsheets(budget_tracking_spreadsheets)
        Combine._write_budget_tracking_spreadsheet(budget_tracking_spreadsheet, args.output_file_path)

    @staticmethod
    def _config_logging():
        log_level = logging.INFO
        log_format = '%(levelname)s: %(message)s'
        logging.basicConfig(level=log_level, format=log_format)

    @staticmethod
    def _read_budget_tracking_spreadsheets(input_file_paths):
        budget_tracking_spreadsheets = []
        for input_file_path in input_file_paths:
            with open(input_file_path) as f:
                reader = csv.reader(f)
                budget_tracking_spreadsheet = {}
                for row in reader:
                    if len(row) == 1: # it's a date
                        date = row[0]
                        if date not in budget_tracking_spreadsheet:
                            budget_tracking_spreadsheet[date] = []
                    elif len(row) == 2: # it's a purchase
                        description = row[0]
                        amount = row[1]
                        budget_tracking_spreadsheet[date].append({
                            'description': description,
                            'amount': amount
                        })
                budget_tracking_spreadsheets.append(budget_tracking_spreadsheet)
        return budget_tracking_spreadsheets

    @staticmethod
    def _combine_budget_tracking_spreadsheets(budget_tracking_spreadsheets):
        combined_budget_tracking_spreadsheet = {}
        for budget_tracking_spreadsheet in budget_tracking_spreadsheets:
            for date in budget_tracking_spreadsheet:
                if date not in combined_budget_tracking_spreadsheet:
                    combined_budget_tracking_spreadsheet[date] = []
                combined_budget_tracking_spreadsheet[date].extend(budget_tracking_spreadsheet[date])
        return combined_budget_tracking_spreadsheet

    @staticmethod
    def _write_budget_tracking_spreadsheet(budget_tracking_spreadsheet, output_file_path):
        with open(output_file_path, 'w') as f:
            writer = csv.writer(f)
            for date in sorted(budget_tracking_spreadsheet.keys()):
                writer.writerow([date])
                for entry in budget_tracking_spreadsheet[date]:
                    writer.writerow([entry['description'], entry['amount']])


class Error(Exception):
    pass


def main():
    args = Combine.parse_args()
    Combine.run(args)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Error as e:
        logging.error(e)
        sys.exit(1)
