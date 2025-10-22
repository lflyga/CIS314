"""
Author: L. Flygare
Description: demonstrate file handling and data processing using a provided log file
"""

import re

#easy to swap file name in one spot if this needs to be used for a different file but same purpose
LOG_PATH = "assignments/access.log" 

#open and read the log file into list
def read_file_to_list(path):
    #try and except with errors caught and returned
    try:
        with open(path) as in_file:
            in_data = in_file.readlines()
        return in_data
    except FileNotFoundError:
        print(f"Error: '{path}' was not found")
        return[]
    #non-file not found errors. will return error code to user like no file permissions
    except OSError as error:
        print(f"OS error while reading file '{path}': {error}")
        return[]
    
#return only lines not containing botpoke in them. lines with botpoke will be ignored
def remove_botpoke(entries):
    return [line for line in entries if "BotPoke" not in line]
    
#regex to return remaining IPs after BotPoke removed
def get_unique_ips(entries):
    #\b word boundary, ?: groups things together without making separate match groups,
    #\d{1,3} match 1-3 digits/0-999, {3} repeats 3x
    ip_re = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    unique = set()  #to only store unique values, no repeat IPs
    for line in entries:
        m = ip_re.search(line)
        if m:
            unique.add(m.group())
    #IPs sorted for readability adn easy referencing
    return sorted(unique, key=lambda ip: tuple(map(int, ip.split("."))))

def main():
    all_entries = read_file_to_list(LOG_PATH)
    print("Total initial log entries: ", len(all_entries))

    filtered = remove_botpoke(all_entries)

    print("Remaining entries (sans BotPoke): ", len(filtered))

    unique_ips = get_unique_ips(filtered)
    print("\nUnique IP Addresses: ")
    for ip in unique_ips:
        print(ip)

if __name__ =="__main__":
    main()