from io import TextIOWrapper

CREATURES = ["bat", "cat"]
PLAYER_PROPERTIES = ["name", "health"]
ITEMS = ["short_sword", "potion", "antidote"]

def load_file(filename: str) -> None:

    with open(filename, "r") as file, open("status.txt", "w") as output:

        line = file.readline()

        while line:

            print(line)

            if line[0] != "[":
                raise Exception("Invalid line found")
        
            line = line.rstrip()[1:-1]
        
            if line == "creatures":
                line = read_creature_data(file)
            elif line == "player":
                line = read_player_data(file)
            elif line == "player items":
                line = read_inventory_items(file)
            else:
                raise Exception("Unknown header!")
        
        output.write("Successfully loaded data from file.")

def read_creature_data(file: TextIOWrapper) -> str:

    line = file.readline()
    while line:

        if line[0] == "[":
            return line
        
        name,_,arguments = str.partition(line, "(")
        arguments,_,_ = str.partition(arguments, ")")
        arguments = arguments.replace(" ","")
        arguments = arguments.split(",")

        if name not in CREATURES:
            raise Exception("Unknown creature!")
        
        if name == "bat":
            make_bat(
                int(arguments[0]), 
                int(arguments[1]), 
                float(arguments[2])
            )
        if name == "cat":
            make_cat(
                int(arguments[0]), 
                int(arguments[1]), 
                arguments[2]
            )

        line = file.readline()

def read_player_data(file: TextIOWrapper) -> str:

    line = file.readline()
    name = None
    health = None

    while line:

        if line[0] == "[":
            return line
        
        property,_,value = str.partition(line, ": ")
        value = value.rstrip()

        if property not in PLAYER_PROPERTIES:
            raise Exception("Unknown Property!")
        
        if property == "name":
            name = value
        elif property == "health":
            health = float(value)
        
        if not(name is None or health is None):
            make_player(name, health)
        
        line = file.readline()

def read_inventory_items(file: TextIOWrapper) -> str:

    line = file.readline()
    inventory = {}

    while line:

        if line[0] == "[":
            return line
        
        line = line.rstrip()
        arguments = line.split(" ")
        if len(arguments) == 1:
            arguments.append(True)
        else:
            arguments[1] = int(arguments[1])
        
        item_type = arguments[0]
        status = arguments[1]

        if item_type not in ITEMS:
            raise Exception("Unknown item!")
        
        inventory[item_type] = status

        line = file.readline()
    
    print(inventory)
    return ""

def make_bat(x: int, y: int, health: float) -> None:
    print(f"Made a bat at ({x},{y}), having health = {health}")

def make_cat(x: int, y: int, name: str) -> None:
    print(f"Made a cat at ({x},{y}), having name = {name}")

def make_player(name: str, health: float) -> None:
    print(f"Made a player with name: {name}, health: {health}")

def main() -> None:

    load_file("level1.txt")

if __name__ == "__main__":
    main()