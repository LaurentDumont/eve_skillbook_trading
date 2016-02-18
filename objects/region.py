class Region:
    typeID = ""
    name = ""

    def __init__(self, typeID, name):
        self.typeID = typeID
        self.name = name


def create_region(typeID, name):

    region = Region(typeID, name)
    return region