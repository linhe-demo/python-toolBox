class CommonMap:
    def __init__(self, target):
        self.target = target
        self.warehouse = {
            2640152423: "FFWH0036",
            1049275063: "FFWH0008",
            1049275062: "FFWH0007",
            2771772189: "FFWH0039",
            3142292305: "FFWH0063",
        }

    def warehouseMap(self):
        return self.warehouse.get(self.target, "")
