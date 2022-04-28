import requests


def has_value(row, column):
    if not row.empty and column in row and row[column] and str(row[column]) != 'nan':
        return True
    else:
        return False


def download_file_from_url(url, filename):
    file = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(file.content)
