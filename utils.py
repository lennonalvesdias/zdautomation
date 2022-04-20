def has_value(self, row, column):
    if not row.empty and column in row and row[column] and str(row[column]) != 'nan':
        return True
    else:
        return False
