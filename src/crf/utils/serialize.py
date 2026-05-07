import csv
import pickle

def stream_pickle_dump(obj, file_handle):
    pickle.dump(obj, file_handle)

def write_csv_row(writer: csv.DictWriter, row: dict, headers: list[str]):
    writer.writerow({h: row.get(h, None) for h in headers})
