import csv
import argparse
import requests
from dateutil.parser import parse as dateutil_parse


def validate_arguments(args):
    try:
        dateutil_parse(args.start_date)
    except ValueError:
        print("You gave invalid start_date")
        exit(1)
    try:
        dateutil_parse(args.end_date)
    except ValueError:
        print("You gave invalid end_date")
        exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_date", help="Starting date of data gathering", required=True)
    parser.add_argument("--end_date", help="Ending date of data gathering", required=True)
    parser.add_argument("--token", help="Access token for the giosg REST API", required=True)
    parser.add_argument("--csv_file", help="Saves results in CSV format in given file path")
    parser.add_argument("--n_days", type=int, help="Number of the busiest days to search for. Default is 3", default=3)
    return parser.parse_args()


def get_chat_stats(start_date, end_date, access_token):
    path = "https://api.giosg.com/api/reporting/v1/rooms/84e0fefa-5675-11e7-a349-00163efdd8db/chat-stats/daily/"
    headers = {"Authorization": "Token " + access_token}
    try:
        response = requests.get(path + "?start_date=" + start_date + "&" + "end_date=" + end_date,
                                timeout=5,
                                headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("HTTP ERROR: " + str(e))
        exit(1)


def get_user_presence_counts(start_date, end_date, access_token):
    path = "https://api.giosg.com/api/reporting/v1/rooms/84e0fefa-5675-11e7-a349-00163efdd8db/user-presence-counts/"
    headers = {"Authorization": "Token " + access_token}
    try:
        response = requests.get(path + "?start_date=" + start_date + "&" + "end_date=" + end_date,
                                timeout=5,
                                headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("HTTP ERROR: " + str(e))
        exit(1)


def get_busiest_days(start_date, end_date, n_of_days, access_token):
    chat_stats = get_chat_stats(start_date, end_date, access_token)
    return sorted(chat_stats["by_date"], key=lambda k: k['conversation_count'], reverse=True)[:n_of_days]


def write_to_csv(busiest_days, presence_counts_by_date, file_name):
    with open(file_name, "w", newline="") as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=["date", "conversation_count"],
                                    extrasaction="ignore")
        csv_writer.writeheader()
        for stats_of_date in busiest_days:
            csv_writer.writerow(stats_of_date)

        csv_writer = csv.DictWriter(csvfile, fieldnames=["date", "hour_of_day", "user_count"])
        csv_writer.writeheader()
        for stats_of_date in busiest_days:
            for presence_counts in presence_counts_by_date[stats_of_date["date"]]:
                csv_writer.writerow(presence_counts)


def get_presence_counts_by_date(presence_counts):
    presence_counts_by_date = {}
    for presence_count in presence_counts["hourly"]:
        date = presence_count["date"]
        if date not in presence_counts_by_date:
            presence_counts_by_date[date] = []
        presence_counts_by_date[date].append(presence_count)
        presence_counts_by_date[date] = sorted(presence_counts_by_date[date], key=lambda x: x["hour_of_day"])
    return presence_counts_by_date


def pretty_print(busiest_days, presence_counts_by_date):
    for stats_of_date in busiest_days:
        date = stats_of_date["date"]
        print("On " + date + " there were " + str(stats_of_date["conversation_count"]) + " chats")
        print("-----------------")
        for presence_count in presence_counts_by_date[date]:
            print(str(presence_count["hour_of_day"]) + ":00 there was " + str(presence_count["user_count"]) +
                  " users present")
        print("\n")


def main():
    args = parse_arguments()
    validate_arguments(args)
    busiest_days = get_busiest_days(args.start_date, args.end_date, args.n_days, args.token)
    presence_counts = get_user_presence_counts(args.start_date, args.end_date, args.token)
    presence_counts_by_date = get_presence_counts_by_date(presence_counts)
    pretty_print(busiest_days, presence_counts_by_date)
    if args.csv_file is not None:
        write_to_csv(busiest_days, presence_counts_by_date, args.csv_file)


if __name__ == "__main__":
    main()
