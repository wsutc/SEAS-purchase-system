import smartsheet


class SmartsheetSheet:
    def __init__(self, name):
        self.smartsheet_client = smartsheet.Smartsheet()
        self.smartsheet_client.errors_as_exceptions(True)
        self.sheet = self.get_sheet_by_name(name)
        self.name = name
        self.columns = self.get_column_map()

    def get_column_map(self):
        """Create a dict of {"column_name":column_id} for ease of use"""
        column_map = {}

        response = self.smartsheet_client.Sheets.get_columns(self.sheet.id)
        columns = response.data

        for column in columns:
            column_map[column.title] = column.id

        return column_map

    def add_sheet_rows(self, data: list[dict]):
        """Add rows to sheet"""
        rows = []
        for r in data:
            row = smartsheet.models.Row()
            row.to_top = True
            for column in r:
                row.cells.append(
                    {"column_id": self.columns[column], "value": r[column]}
                )
            # i += 1
            rows.append(row)

        return self.smartsheet_client.Sheets.add_rows(self.sheet.id, rows)

    def update_sheet_row_by_number(self, number: str):
        pass

    def get_sheet_by_name(self, name: str):
        """Get sheet object by sheet name"""
        response = self.smartsheet_client.Sheets.list_sheets(include_all=True)
        sheets = response.data
        for sheet in sheets:
            sheet_name = sheet.name
            if sheet_name == name:
                return sheet

        return

    # def get_column_id_by_name(column_name:str,column_map:dict):
    #     column_id = column_map[column_name]
    #     return column_id
