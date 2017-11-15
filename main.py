

import argparse
from dateutil.parser import parse as dateutil_parse


def validate_arguments(args):
    try:
        dateutil_parse(args.start_date)
    except ValueError:
        raise ValueError("You gave invalid start_date")
    try:
        dateutil_parse(args.end_date)
    except ValueError:
        raise ValueError("You gave invalid end_date")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("start_date", help="Starting date of data gathering")
    parser.add_argument("end_date", help="Ending date of data gathering")
    parser.add_argument("access_token", help="Access token for the giosg REST API")
    return parser.parse_args()


def get_chat_data():
    pass


def main():
    args = parse_arguments()
    try:
        validate_arguments(args)
    except ValueError as e:
        print("INPUT ERROR: " + str(e))
        exit(1)
    get_chat_data()


if __name__ == "__main__":
    main()
