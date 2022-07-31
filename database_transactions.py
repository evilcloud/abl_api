from deta import Deta
from collections import Counter


def load_file(filename: str) -> list:
    """
    It opens a file, reads the lines, strips the newline characters, and returns the data as a list

    :param filename: the name of the file to load
    :type filename: str
    :return: A list of strings.
    """
    with open(filename, "r") as f:
        data = f.readlines()
        data = [entry.strip("\n").strip() for entry in data]
    return data


def update_block_difference(data):
    """
    Deals with the issue of newly restarted Pinger machine by zeroing
    the block difference if the block difference is the same as the last block
    but not the first block (which means that this is genuenly the first block)

    :param data: the dataframe
    :return: The data is being returned.
    """
    if "update block difference" not in data:
        return data
    for entry in data:
        if (
            entry["update block difference"] == entry["block"]
            and entry["block"] > 256
            and entry["update amount"] == entry["balance"]
        ):
            entry["block difference"] = 0
            entry["update amount"] = 0


def get_duplicate_values(values):
    """
    It takes a list of values, converts it to a dictionary, and returns a list of the values that appear
    more than once.

    :param values: a list of values
    :return: A list of values that are duplicated in the list.
    """
    d = Counter(values)
    return list([item for item in d if d[item] > 1])


class Detadb:
    def __init__(self, deta, dbname):
        self.dbname = dbname
        self.db = deta.Base(dbname)

    def _get_entries(self):
        """
        This function gets the entries from the database and updates the block difference
        """
        entries_obj = self.db.fetch()
        self.entries = update_block_difference(entries_obj.items)
        machine_key = (
            "machine" if any("machine" in entry for entry in self.entries) else "key"
        )
        if machine_key == "key":
            self.machines = [entry[machine_key] for entry in self.entries]
            self.duplicate_machines = get_duplicate_values(self.machines)
            self.stats_version = Counter(
                [entry.get("version", "unknown") for entry in self.entries]
            )
            self.total_machines = len(self.machines)

    def get_all(self):
        self._get_entries()

    def get_mining(self):
        """
        It gets all the machines, then it separates the safe machines from the unknown machines, then it
        gets the total number of machines, the total balance, and the total number of programmatic
        machines

        All totals are SAFE MACHINES!
        """
        self.get_all()
        safe_machines_list = load_file("safe_machines.txt")
        self.safe_machines = []
        self.unknown_machines = []
        for entry in self.entries:
            if entry["key"] in safe_machines_list:
                self.safe_machines.append(entry)
            else:
                self.unknown_machines.append(entry)
        self.safe_machine_names = [machine["key"] for machine in self.safe_machines]
        self.unknown_machine_names = [
            machine["key"] for machine in self.unknown_machines
        ]
        self.stats_os = Counter([entry["os"] for entry in self.safe_machines])
        self.total = sum([entry["balance"] for entry in self.safe_machines])
        self.total_machines = len(self.safe_machines)
        self.stats_programmatic = sum(
            [entry["programmatic"] for entry in self.safe_machines]
        )

    def get_ping(self):
        self._get_entries()


def connect_to_db(key, dbname):
    """
    Connect to the database.
    """
    deta = Deta(key)
    db = Detadb(deta, dbname)
    return db


def mining_data(key, dbname):
    """
    It connects to the database, gets the mining data, and returns a dictionary with the data

    :param key: the key to access the database
    :param dbname: the name of the database you want to mine
    :return: A dictionary with the following keys:
        Database: The name of the database
        Total balance: The total balance of the database
        Safe machines nr: The number of safe machines in the database
        Safe machine names: The names of the safe machines in the database
        Unknown machines nr: The number of unknown machines in the database
        Unknown machine names: The names
    """
    db = connect_to_db(key, dbname)
    db.get_mining()
    return {
        "Database": db.dbname,
        "Total machines": db.total_machines,
        "Total balance": db.total,
        "Safe machines nr": len(db.safe_machines),
        "Safe machine names": db.safe_machine_names,
        "Unknown machines nr": len(db.unknown_machines),
        "Unknown machine names": db.unknown_machine_names,
        "Double entries nr": len(db.duplicate_machines),
        "Double entries": db.duplicate_machines,
        "OS": db.stats_os,
        "Versions": db.stats_version,
        "Programmatic": db.stats_programmatic,
        "Manual": db.total_machines - db.stats_programmatic,
    }


def ping_data(key, dbname):
    db = connect_to_db(key, dbname)
    db.get_ping()
    return {
        "Database": db.dbname,
        # "Total machines": db.total_machines,
        "Double entries nr": len(db.duplicate_machines),
        "Double entries": db.duplicate_machines,
        # "OS": db.stats_os,
        "Versions": db.stats_version,
        # "Programmatic": db.stats_programmatic,
        # "Manual": db.total_machines - db.stats_programmatic,
    }
