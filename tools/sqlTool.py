class SqlTool:

    def __init__(self, data=None, table=None):
        self.data = data
        self.table = table

    def createInsertStatements(self):
        columns = ', '.join(self.data.keys())
        values = ', '.join(f"'{str(val)}'" for val in self.data.values())
        return f"INSERT INTO {self.table} ({columns}) VALUES ({values});"
