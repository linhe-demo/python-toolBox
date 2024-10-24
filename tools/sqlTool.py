class SqlTool:

    def __init__(self, data=None, table=None, condition=None):
        self.data = data
        self.table = table
        self.condition = condition

    def createInsertStatements(self):
        columns = ', '.join(self.data.keys())
        values = ', '.join(f'"{str(val)}"' for val in self.data.values())
        return f"INSERT INTO {self.table} ({columns}) VALUES ({values});"

    def createUpdateStatements(self):
        condition = self.data.get(self.condition)
        del self.data[self.condition]
        # 构造 SQL 更新语句
        set_clause = ", ".join([f"{key} = '%s'" for key in self.data.keys()])
        data = ()
        for key, value in self.data.items():
            data += (value,)
        data += (condition,)

        return f"UPDATE {self.table}  SET {set_clause} WHERE {self.condition} = %s;" % data
