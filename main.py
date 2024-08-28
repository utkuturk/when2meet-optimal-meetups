import csv
import time as tm
import argparse

def find_best_times(filename, head_person, interval=4):
    with open(filename, "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        availability = list(reader)

    people = [person for person in header[1:]]
    times = [row[0] for row in availability]
    parsed_times = [
        tm.strptime(time_str, "%A %I:%M:%S %p") for time_str in times
    ]

    availability_dict = {}

    def is_next_time_valid(current_time, next_time):
        return (
            next_time.tm_hour == current_time.tm_hour
            and next_time.tm_min == current_time.tm_min + 15
        ) or (
            next_time.tm_hour == current_time.tm_hour + 1
            and next_time.tm_min == 0
            and current_time.tm_min == 45
        )

    for time_idx, current_time in enumerate(parsed_times):
        availability_dict[current_time] = []
        for person_idx, person in enumerate(people):
            is_available = True
            for i in range(interval):
                next_time_idx = time_idx + i
                if (
                    next_time_idx < len(parsed_times) - interval
                    and availability[time_idx + i][person_idx + 1] == "1"
                    and (
                        i == 0
                        or is_next_time_valid(
                            parsed_times[next_time_idx - 1], parsed_times[next_time_idx]
                        )
                    )
                ):
                    continue
                else:
                    is_available = False
                    break
            if is_available:
                availability_dict[parsed_times[time_idx]].append(person)

    head_availability = {time: people for time, people in availability_dict.items() if head_person in people}

    used_times = set()
    meetings = []

    for person in people:
        if person == head_person:
            continue

        suitable_times = [time for time, people in head_availability.items() if person in people and time not in used_times]

        if suitable_times:
            best_time = suitable_times[0]
            meetings.append((best_time, person))
            used_times.add(best_time)
        else:
            meetings.append(("No suitable time found for " + person, person))
            
    best_general_time = None

    for time, people in availability_dict.items():
        if len(people) == len(header) - 1 and time not in used_times:
            best_general_time = time
            break

    return meetings, best_general_time


def format_output(meetings, general_time_struct):
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    formatted_list = []

    for time_struct, person in meetings:
        if isinstance(time_struct, str):  # No suitable time found
            formatted_list.append(f"1-on-1 Meeting: {time_struct} with {person}")
        else:
            hour = time_struct.tm_hour % 12
            hour = 12 if hour == 0 else hour
            period = "AM" if time_struct.tm_hour < 12 else "PM"
            day = days[time_struct.tm_wday]
            formatted_time = f"{day}, {hour}:{str(time_struct.tm_min).zfill(2)} {period}"
            formatted_list.append(f"1-on-1 Meeting Time: {formatted_time} with {person}")

    if general_time_struct:
        hour = general_time_struct.tm_hour % 12
        hour = 12 if hour == 0 else hour
        period = "AM" if general_time_struct.tm_hour < 12 else "PM"
        day = days[general_time_struct.tm_wday]
        formatted_time = f"{day}, {hour}:{str(general_time_struct.tm_min).zfill(2)} {period}"
        formatted_list.append(f"Best General Meeting Time: {formatted_time}")

    return formatted_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the best times for meetings based on availability."
    )
    parser.add_argument(
        "filename", type=str, help="CSV file containing availability data."
    )
    parser.add_argument(
        "head_person", type=str, help="The head person for 1-1 meetings."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=4,
        help="Number of consecutive 15-minute intervals.",
    )

    args = parser.parse_args()

    meetings, best_general_time = find_best_times(
        args.filename, args.head_person, args.interval
    )

    formatted_list = format_output(meetings, best_general_time)
    for line in formatted_list:
        print(line)
