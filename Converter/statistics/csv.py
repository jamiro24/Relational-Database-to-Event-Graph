import csv


def write(collection, header, name):
    with open(f'statistics-csv/{name}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for entree in collection:
            writer.writerow(entree)
