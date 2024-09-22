import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import random
import string
import time
import logging
from datetime import datetime
import subprocess
import sys
import os
import shlex
import json

# -----------------------------
# Configuration and Logging
# -----------------------------

# Configure Logging
logging.basicConfig(
    filename='cradium_core.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# -----------------------------
# Utility Functions
# -----------------------------

def generate_uuid() -> str:
    """
    Generates a unique UUID string.
    
    Returns:
        str: A unique UUID.
    """
    return str(uuid.uuid4())

def generate_procedural_name(syllables: Optional[list] = None, min_syllables: int = 2, max_syllables: int = 3) -> str:
    """
    Generates a procedurally created name by combining random syllables.
    
    Args:
        syllables (list, optional): List of syllables to use. Defaults to predefined list.
        min_syllables (int, optional): Minimum number of syllables in the name. Defaults to 2.
        max_syllables (int, optional): Maximum number of syllables in the name. Defaults to 3.
    
    Returns:
        str: A procedurally generated name.
    """
    if syllables is None:
        syllables = ['Crad', 'Ium', 'Vex', 'Lun', 'Tori', 'Plas', 'Zynth', 'Nor', 'Del', 'Xar']
    name_length = random.randint(min_syllables, max_syllables)
    name = ''.join(random.choice(syllables) for _ in range(name_length))
    return name.capitalize()

def generate_random_string(length: int = 8) -> str:
    """
    Generates a random alphanumeric string of specified length.
    
    Args:
        length (int, optional): Length of the string. Defaults to 8.
    
    Returns:
        str: A random string.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_current_timestamp() -> str:
    """
    Retrieves the current timestamp in ISO format.
    
    Returns:
        str: Current timestamp.
    """
    return datetime.utcnow().isoformat()

def execute_script(script_content: str) -> Optional[str]:
    """
    Executes a given script safely and returns the output.
    
    Args:
        script_content (str): The content of the script to execute.
    
    Returns:
        Optional[str]: The output of the script execution or None if failed.
    """
    try:
        # Write script to a temporary file
        temp_script = f"temp_script_{generate_random_string(6)}.py"
        with open(temp_script, 'w') as file:
            file.write(script_content)
        
        # Execute the script
        result = subprocess.run(
            [sys.executable, temp_script],
            capture_output=True,
            text=True,
            timeout=10  # Prevent long-running scripts
        )
        
        # Remove the temporary script file
        os.remove(temp_script)
        
        if result.returncode == 0:
            logging.info("Script executed successfully.")
            return result.stdout
        else:
            logging.error(f"Script execution failed: {result.stderr}")
            return None
    except Exception as e:
        logging.error(f"Error executing script: {e}")
        return None

def validate_coordinates(x: int, y: int, layer: int, grid_width: int, grid_height: int, grid_layers: int) -> bool:
    """
    Validates if the provided coordinates are within the grid boundaries.
    
    Args:
        x (int): X-coordinate.
        y (int): Y-coordinate.
        layer (int): Layer index.
        grid_width (int): Width of the grid.
        grid_height (int): Height of the grid.
        grid_layers (int): Number of layers in the grid.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    if 0 <= x < grid_width and 0 <= y < grid_height and 0 <= layer < grid_layers:
        return True
    else:
        logging.warning(f"Invalid coordinates attempted: ({x}, {y}, {layer})")
        return False

def log_event(message: str, level: str = 'INFO'):
    """
    Logs an event with the specified logging level.
    
    Args:
        message (str): The message to log.
        level (str, optional): Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). Defaults to 'INFO'.
    """
    if level.upper() == 'DEBUG':
        logging.debug(message)
    elif level.upper() == 'INFO':
        logging.info(message)
    elif level.upper() == 'WARNING':
        logging.warning(message)
    elif level.upper() == 'ERROR':
        logging.error(message)
    elif level.upper() == 'CRITICAL':
        logging.critical(message)
    else:
        logging.info(message)

def calculate_cooldown_end_time(cooldown_duration: float) -> float:
    """
    Calculates the timestamp when a cooldown will end.
    
    Args:
        cooldown_duration (float): Duration of the cooldown in seconds.
    
    Returns:
        float: The timestamp when cooldown ends.
    """
    return time.time() + cooldown_duration

def is_cooldown_over(cooldown_end_time: float) -> bool:
    """
    Checks if the current time has passed the cooldown end time.
    
    Args:
        cooldown_end_time (float): The timestamp when cooldown ends.
    
    Returns:
        bool: True if cooldown is over, False otherwise.
    """
    return time.time() >= cooldown_end_time

def save_game_state(player: 'Player', filename: str = 'savegame.json') -> bool:
    """
    Saves the current game state to a JSON file.
    
    Args:
        player (Player): The player object containing the game state.
        filename (str, optional): The filename to save the state. Defaults to 'savegame.json'.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with open(filename, 'w') as file:
            json.dump(player.to_dict(), file, indent=4, default=str)
        logging.info("Game state saved successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to save game state: {e}")
        return False

def load_game_state(filename: str = 'savegame.json') -> Optional['Player']:
    """
    Loads the game state from a JSON file.
    
    Args:
        filename (str, optional): The filename to load the state from. Defaults to 'savegame.json'.
    
    Returns:
        Optional[Player]: The loaded player object or None if failed.
    """
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        player = Player.from_dict(data)
        logging.info("Game state loaded successfully.")
        return player
    except Exception as e:
        logging.error(f"Failed to load game state: {e}")
        return None

def clear_console():
    """
    Clears the console screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def display_colored_text(text: str, color: str = 'white') -> None:
    """
    Displays colored text in the console.
    
    Args:
        text (str): The text to display.
        color (str, optional): The color name. Defaults to 'white'.
    """
    colors = {
        'black': '\u001b[30m',
        'red': '\u001b[31m',
        'green': '\u001b[32m',
        'yellow': '\u001b[33m',
        'blue': '\u001b[34m',
        'magenta': '\u001b[35m',
        'cyan': '\u001b[36m',
        'white': '\u001b[37m',
        'reset': '\u001b[0m'
    }
    color_code = colors.get(color.lower(), colors['white'])
    reset_code = colors['reset']
    print(f"{color_code}{text}{reset_code}")

def get_user_confirmation(prompt: str = "Are you sure? (y/n): ") -> bool:
    """
    Prompts the user for a yes/no confirmation.
    
    Args:
        prompt (str, optional): The prompt message. Defaults to "Are you sure? (y/n): ".
    
    Returns:
        bool: True if user confirms, False otherwise.
    """
    while True:
        response = input(prompt).strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please respond with 'y' or 'n'.")

def format_time(seconds: float) -> str:
    """
    Formats time in seconds to a human-readable string.
    
    Args:
        seconds (float): Time in seconds.
    
    Returns:
        str: Formatted time string.
    """
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours}h {mins}m {secs}s"

def delay_execution(duration: float):
    """
    Delays the execution for a specified duration.
    
    Args:
        duration (float): Duration in seconds.
    """
    time.sleep(duration)

def get_random_element(elements: list) -> Any:
    """
    Retrieves a random element from a list.
    
    Args:
        elements (list): The list to choose from.
    
    Returns:
        Any: A random element from the list.
    """
    return random.choice(elements) if elements else None

def shuffle_list(items: list) -> list:
    """
    Returns a shuffled copy of the given list.
    
    Args:
        items (list): The list to shuffle.
    
    Returns:
        list: Shuffled list.
    """
    shuffled = items[:]
    random.shuffle(shuffled)
    return shuffled

def get_random_rarity() -> str:
    """
    Randomly selects a rarity level based on predefined weights.
    
    Returns:
        str: Selected rarity level.
    """
    rarity_levels = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']
    rarity_weights = [40, 30, 20, 8, 2]
    return random.choices(rarity_levels, weights=rarity_weights, k=1)[0]

def get_current_time() -> float:
    """
    Retrieves the current time in seconds since the epoch.
    
    Returns:
        float: Current time.
    """
    return time.time()

def ensure_directory(path: str):
    """
    Ensures that a directory exists; creates it if it does not.
    
    Args:
        path (str): The directory path.
    """
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Created directory: {path}")
    else:
        logging.debug(f"Directory already exists: {path}")

def read_file_contents(file_path: str) -> Optional[str]:
    """
    Reads and returns the contents of a file.
    
    Args:
        file_path (str): Path to the file.
    
    Returns:
        Optional[str]: File contents or None if failed.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Failed to read file {file_path}: {e}")
        return None

def write_to_file(file_path: str, content: str) -> bool:
    """
    Writes content to a file.
    
    Args:
        file_path (str): Path to the file.
        content (str): Content to write.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        logging.info(f"Wrote to file {file_path} successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to write to file {file_path}: {e}")
        return False

def parse_user_input(input_str: str) -> list:
    """
    Parses a user input string into a list of arguments.
    
    Args:
        input_str (str): The raw input string.
    
    Returns:
        list: List of parsed arguments.
    """
    return input_str.strip().split()

def get_material_type_description(material_type: str) -> str:
    """
    Returns a description based on the material type.
    
    Args:
        material_type (str): The type of material.
    
    Returns:
        str: Description of the material type.
    """
    descriptions = {
        'Metal': 'A sturdy and malleable material, essential for machine parts.',
        'Mineral': 'A hard and durable substance, perfect for building structures.',
        'Plant': 'A living organism, useful for crafting biological items.'
    }
    return descriptions.get(material_type, 'Unknown material type.')

def calculate_material_quality_bonus(quality: float) -> float:
    """
    Calculates a bonus based on the material quality.
    
    Args:
        quality (float): The quality of the material (0.1 - 1.0).
    
    Returns:
        float: The calculated bonus.
    """
    return quality * 10  # Example: Quality scales bonus linearly

def get_user_input(prompt: str = "> ") -> str:
    """
    Retrieves input from the user.
    
    Args:
        prompt (str, optional): The input prompt. Defaults to "> ".
    
    Returns:
        str: The user's input.
    """
    try:
        return input(prompt)
    except EOFError:
        return 'exit'
    except KeyboardInterrupt:
        print("\nExiting Cradium Core. Goodbye!")
        sys.exit(0)

# -----------------------------
# Data Models
# -----------------------------

@dataclass
class Material:
    """
    Represents a procedurally generated material with unique attributes.
    """
    id: str
    name: str
    rarity: str
    quality: float
    material_type: str
    base_stone_type: str

    @staticmethod
    def generate_id() -> str:
        return generate_uuid()

@dataclass
class InventoryItem:
    """
    Associates a material with its quantity in the inventory.
    """
    material: Material
    quantity: int = 1

@dataclass
class Inventory:
    """
    Manages the player's inventory, allowing addition and removal of items.
    """
    items: Dict[str, InventoryItem] = field(default_factory=dict)

    def add_item(self, material: Material, quantity: int = 1):
        if material.id in self.items:
            self.items[material.id].quantity += quantity
        else:
            self.items[material.id] = InventoryItem(material, quantity)
        print(f"Added {quantity} x {material.name} to inventory.")
        log_event(f"Added {quantity} x {material.name} to inventory.", 'DEBUG')

    def remove_item(self, material_id: str, quantity: int = 1) -> bool:
        if material_id in self.items and self.items[material_id].quantity >= quantity:
            self.items[material_id].quantity -= quantity
            if self.items[material_id].quantity == 0:
                del self.items[material_id]
            print(f"Removed {quantity} x {material_id} from inventory.")
            log_event(f"Removed {quantity} x {material_id} from inventory.", 'DEBUG')
            return True
        print(f"Failed to remove {quantity} x {material_id} from inventory.")
        log_event(f"Failed to remove {quantity} x {material_id} from inventory.", 'WARNING')
        return False

    def get_item_by_name(self, name: str) -> Optional['InventoryItem']:
        for item in self.items.values():
            if item.material.name.lower() == name.lower():
                return item
        return None

    def list_inventory(self) -> List['InventoryItem']:
        return list(self.items.values())

    def to_dict(self) -> Dict:
        return {
            material_id: {
                'material': {
                    'id': item.material.id,
                    'name': item.material.name,
                    'rarity': item.material.rarity,
                    'quality': item.material.quality,
                    'material_type': item.material.material_type,
                    'base_stone_type': item.material.base_stone_type
                },
                'quantity': item.quantity
            }
            for material_id, item in self.items.items()
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Inventory':
        inventory = Inventory()
        for material_id, item_data in data.items():
            material_data = item_data['material']
            material = Material(
                id=material_data['id'],
                name=material_data['name'],
                rarity=material_data['rarity'],
                quality=material_data['quality'],
                material_type=material_data['material_type'],
                base_stone_type=material_data['base_stone_type']
            )
            inventory.items[material_id] = InventoryItem(material, item_data['quantity'])
        return inventory

@dataclass
class CraftingGrid:
    """
    Represents a multi-layered 10x10 crafting grid where players can place materials to build structures or machines.
    """
    width: int = 10
    height: int = 10
    layers: int = 3
    grid: List[List[List[Optional[Material]]]] = field(init=False)

    def __post_init__(self):
        self.grid = [[[None for _ in range(self.width)] for _ in range(self.height)] for _ in range(self.layers)]
        print(f"Initialized Crafting Grid with {self.layers} layers of {self.width}x{self.height}.")
        log_event(f"Initialized Crafting Grid with {self.layers} layers of {self.width}x{self.height}.", 'DEBUG')

    def place_item(self, x: int, y: int, layer: int, material: Material) -> bool:
        if self.is_valid_position(x, y, layer):
            if self.grid[layer][y][x] is None:
                self.grid[layer][y][x] = material
                print(f"Placed {material.name} at ({x}, {y}) on layer {layer}.")
                log_event(f"Placed {material.name} at ({x}, {y}) on layer {layer}.", 'INFO')
                return True
            else:
                print(f"Position ({x}, {y}) on layer {layer} is already occupied.")
                log_event(f"Attempted to place {material.name} at occupied position ({x}, {y}, {layer}).", 'WARNING')
        else:
            print(f"Invalid position: ({x}, {y}, {layer}).")
            log_event(f"Attempted to place item at invalid position ({x}, {y}, {layer}).", 'WARNING')
        return False

    def remove_item(self, x: int, y: int, layer: int) -> (bool, Optional[Material]):
        if self.is_valid_position(x, y, layer):
            material = self.grid[layer][y][x]
            if material:
                self.grid[layer][y][x] = None
                print(f"Removed {material.name} from ({x}, {y}) on layer {layer}.")
                log_event(f"Removed {material.name} from ({x}, {y}) on layer {layer}.", 'INFO')
                return True, material
            else:
                print(f"No item to remove at ({x}, {y}) on layer {layer}).")
                log_event(f"Attempted to remove item from empty position ({x}, {y}, {layer}).", 'WARNING')
                return False, None
        else:
            print(f"Invalid position: ({x}, {y}, {layer}).")
            log_event(f"Attempted to remove item from invalid position ({x}, {y}, {layer}).", 'WARNING')
            return False, None

    def is_valid_position(self, x: int, y: int, layer: int) -> bool:
        return validate_coordinates(x, y, layer, self.width, self.height, self.layers)

    def display_grid(self):
        for layer in range(self.layers):
            print(f"\nLayer {layer}:")
            for y in range(self.height):
                row = self.grid[layer][y]
                row_display = ' | '.join([item.name if item else 'Empty' for item in row])
                print(row_display)
            print("\n" + "-" * (self.width * 6))

    def to_dict(self) -> Dict:
        return {
            'width': self.width,
            'height': self.height,
            'layers': self.layers,
            'grid': [
                [
                    [material.id if material else None for material in row]
                    for row in layer
                ]
                for layer in self.grid
            ]
        }

    @staticmethod
    def from_dict(data: Dict, materials_lookup: Dict[str, Material]) -> 'CraftingGrid':
        grid = CraftingGrid(width=data['width'], height=data['height'], layers=data['layers'])
        for layer_idx, layer in enumerate(data['grid']):
            for y_idx, row in enumerate(layer):
                for x_idx, material_id in enumerate(row):
                    if material_id and material_id in materials_lookup:
                        grid.grid[layer_idx][y_idx][x_idx] = materials_lookup[material_id]
        return grid

@dataclass
class Recipe:
    """
    Defines a crafting recipe consisting of required materials and the resulting item or structure.
    """
    id: str
    name: str
    input_materials: Dict[str, int]  # Material ID and required quantity
    output_item: 'Item'  # The item produced by the recipe
    required_grid_layers: int  # Number of layers required in the crafting grid
    build_time: float  # Time required to craft in seconds

    @staticmethod
    def generate_id() -> str:
        return generate_uuid()

@dataclass
class Item:
    """
    Represents a generic item that can be used as an ingredient or produced as an output.
    """
    id: str
    name: str
    description: str
    item_type: str  # e.g., 'PassiveCollector', 'ActiveCollector', 'Ingredient', 'MachinePart', 'CraftedItem'
    properties: Dict[str, Any]  # Additional properties based on item type

    @staticmethod
    def generate_id() -> str:
        return generate_uuid()

@dataclass
class Machine:
    """
    Represents a machine that can perform actions like resource extraction or item processing.
    """
    id: str
    name: str
    hp: float
    parts: List[Item]
    functionality: str  # Description of what the machine does
    cooldown_time: float  # Time between actions in seconds

    @staticmethod
    def generate_id() -> str:
        return generate_uuid()

@dataclass
class PlantGenetics:
    """
    Represents the genetics of a plant, allowing for breeding and propagation under certain conditions.
    """
    id: str
    species: str
    genetic_traits: Dict[str, Any]  # Traits like growth rate, resistance, yield, etc.

    @staticmethod
    def generate_id() -> str:
        return generate_uuid()

@dataclass
class Plant:
    """
    Represents a plant that can be grown, bred, and harvested.
    """
    id: str
    genetics: PlantGenetics
    current_growth_stage: int
    max_growth_stage: int
    health: float
    environment_conditions: Dict[str, Any]  # Conditions required for proper growth

    @staticmethod
    def generate_id() -> str:
        return generate_uuid()

@dataclass
class ObjectDictionary:
    """
    Categorizes materials and items based on their properties and usage conditions.
    """
    categories: Dict[str, List[str]] = field(default_factory=dict)  # Category name and list of Material or Item IDs

    def add_to_category(self, category: str, item_id: str):
        if category in self.categories:
            if item_id not in self.categories[category]:
                self.categories[category].append(item_id)
        else:
            self.categories[category] = [item_id]
        print(f"Added Item ID {item_id} to category '{category}'.")
        log_event(f"Added Item ID {item_id} to category '{category}'.", 'DEBUG')

    def remove_from_category(self, category: str, item_id: str):
        if category in self.categories and item_id in self.categories[category]:
            self.categories[category].remove(item_id)
            print(f"Removed Item ID {item_id} from category '{category}'.")
            log_event(f"Removed Item ID {item_id} from category '{category}'.", 'DEBUG')

    def get_category_items(self, category: str) -> List[str]:
        return self.categories.get(category, [])

    def to_dict(self) -> Dict:
        return self.categories

    @staticmethod
    def from_dict(data: Dict) -> 'ObjectDictionary':
        return ObjectDictionary(categories=data)

@dataclass
class Script:
    """
    Represents a user-created script for automating tasks within the game.
    """
    id: str
    name: str
    content: str  # The actual code/content of the script
    created_at: str
    last_modified: str

    @staticmethod
    def generate_id() -> str:
        return generate_uuid()

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'created_at': self.created_at,
            'last_modified': self.last_modified
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Script':
        return Script(
            id=data['id'],
            name=data['name'],
            content=data['content'],
            created_at=data['created_at'],
            last_modified=data['last_modified']
        )

@dataclass
class Cooldown:
    """
    Represents cooldown timers for resources and automation processes based on setup quality.
    """
    resource_id: str
    cooldown_end_time: float  # Timestamp when the cooldown ends

    @staticmethod
    def generate_id() -> str:
        return generate_uuid()

    def to_dict(self) -> Dict:
        return {
            'resource_id': self.resource_id,
            'cooldown_end_time': self.cooldown_end_time
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Cooldown':
        return Cooldown(
            resource_id=data['resource_id'],
            cooldown_end_time=data['cooldown_end_time']
        )

@dataclass
class Player:
    """
    Represents a player in the game, managing their inventory, crafting grid, base, and other attributes.
    """
    name: str
    inventory: Inventory = field(default_factory=Inventory)
    crafting_grid: CraftingGrid = field(default_factory=CraftingGrid)
    base_initialized: bool = False
    scripts: List[Script] = field(default_factory=list)
    plants: List[Plant] = field(default_factory=list)
    machines: List[Machine] = field(default_factory=list)
    object_dictionary: ObjectDictionary = field(default_factory=ObjectDictionary)
    cooldowns: List[Cooldown] = field(default_factory=list)

    def initialize_base(self):
        self.base_initialized = True
        print(f"Base initialized for player {self.name}.")
        log_event(f"Base initialized for player {self.name}.", 'INFO')

    def add_script(self, script: Script):
        self.scripts.append(script)
        print(f"Added script '{script.name}' to player {self.name}.")
        log_event(f"Added script '{script.name}' to player {self.name}.", 'INFO')

    def add_plant(self, plant: Plant):
        self.plants.append(plant)
        print(f"Added plant '{plant.genetics.species}' to player {self.name}.")
        log_event(f"Added plant '{plant.genetics.species}' to player {self.name}.", 'INFO')

    def add_machine(self, machine: Machine):
        self.machines.append(machine)
        print(f"Added machine '{machine.name}' to player {self.name}.")
        log_event(f"Added machine '{machine.name}' to player {self.name}.", 'INFO')

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'inventory': self.inventory.to_dict(),
            'crafting_grid': self.crafting_grid.to_dict(),
            'base_initialized': self.base_initialized,
            'scripts': [script.to_dict() for script in self.scripts],
            'plants': [plant.to_dict() for plant in self.plants],
            'machines': [machine.__dict__ for machine in self.machines],  # Assuming machines have serializable fields
            'object_dictionary': self.object_dictionary.to_dict(),
            'cooldowns': [cd.to_dict() for cd in self.cooldowns]
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Player':
        inventory = Inventory.from_dict(data['inventory'])
        materials_lookup = {item['material']['id']: Material(**item['material']) for item in data['inventory'].values()}
        crafting_grid = CraftingGrid.from_dict(data['crafting_grid'], materials_lookup)
        object_dictionary = ObjectDictionary.from_dict(data['object_dictionary'])
        scripts = [Script.from_dict(s) for s in data.get('scripts', [])]
        plants = []
        for p in data.get('plants', []):
            genetics = PlantGenetics(**p['genetics'])
            plant = Plant(
                id=p['id'],
                genetics=genetics,
                current_growth_stage=p['current_growth_stage'],
                max_growth_stage=p['max_growth_stage'],
                health=p['health'],
                environment_conditions=p['environment_conditions']
            )
            plants.append(plant)
        machines = []
        for m in data.get('machines', []):
            parts = []
            for part in m['parts']:
                part_item = Item(**part)
                parts.append(part_item)
            machine = Machine(
                id=m['id'],
                name=m['name'],
                hp=m['hp'],
                parts=parts,
                functionality=m['functionality'],
                cooldown_time=m['cooldown_time']
            )
            machines.append(machine)
        cooldowns = [Cooldown.from_dict(cd) for cd in data.get('cooldowns', [])]
        player = Player(
            name=data['name'],
            inventory=inventory,
            crafting_grid=crafting_grid,
            base_initialized=data['base_initialized'],
            scripts=scripts,
            plants=plants,
            machines=machines,
            object_dictionary=object_dictionary,
            cooldowns=cooldowns
        )
        return player

# -----------------------------
# Command Parser
# -----------------------------

class CommandParser:
    """
    Parses and executes user commands within Cradium Core.
    """

    def __init__(self, player: Player):
        self.player = player
        self.commands: Dict[str, Callable[[List[str]], None]] = {
            'help': self.help,
            'mine': self.mine,
            'inventory': self.show_inventory,
            'place': self.place_item,
            'remove': self.remove_item,
            'showgrid': self.show_grid,
            'exit': self.exit_game,
            'editscript': self.edit_script,
            'runscript': self.run_script,
            'listscripts': self.list_scripts,
            'createscript': self.create_script,
            'deletescript': self.delete_script,
            'useitem': self.use_item,
            'listrecipes': self.list_recipes,
            'createrecipe': self.create_recipe,
            'deleterecipe': self.delete_recipe,
            'listmachines': self.list_machines,
            'addmachine': self.add_machine,
            'removemachine': self.remove_machine,
            'listplants': self.list_plants,
            'addplant': self.add_plant,
            'removeplant': self.remove_plant,
            'savegame': self.save_game,
            'loadgame': self.load_game,
            'helpcommands': self.help_commands,
            'helpautomation': self.help_automation,
            'helpcrafting': self.help_crafting,
            # Add more commands as needed to align with the creative vision
        }
        self.is_running = True

    def parse(self, input_line: str):
        """
        Parses the input line and executes the corresponding command.
        """
        tokens = shlex.split(input_line)
        if not tokens:
            return
        command = tokens[0].lower()
        args = tokens[1:]
        if command in self.commands:
            try:
                self.commands[command](args)
            except Exception as e:
                print(f"Error executing command '{command}': {e}")
                log_event(f"Error executing command '{command}': {e}", 'ERROR')
        else:
            print(f"Unknown command: '{command}'. Type 'help' for a list of commands.")
            log_event(f"Unknown command attempted: '{command}'", 'WARNING')

    def help(self, args: List[str]):
        """
        Displays the help message with available commands.
        """
        help_message = """
Available Commands:
  help                     Show this help message
  mine                     Mine a material and add it to your inventory
  inventory                Display your inventory
  place x y layer name     Place a material from inventory onto the crafting grid
  remove x y layer         Remove a material from the crafting grid back to inventory
  showgrid                 Display the crafting grid
  exit                     Exit the game
  editscript name          Edit a script using the in-game text editor
  runscript name           Run a specified script
  listscripts              List all available scripts
  createscript name        Create a new automation script
  deletescript name        Delete an existing script
  useitem name            Use an item from your inventory
  listrecipes              List all crafting recipes
  createrecipe             Create a new crafting recipe
  deleterecipe name        Delete an existing crafting recipe
  listmachines             List all owned machines
  addmachine name          Add a new machine to your inventory
  removemachine name       Remove a machine from your inventory
  listplants               List all owned plants
  addplant species         Add a new plant with specified species
  removeplant id           Remove a plant by its ID
  savegame [filename]      Save the current game state to a file
  loadgame [filename]      Load the game state from a file
  helpcommands             Show detailed help for commands
  helpautomation           Show detailed help for automation commands
  helpcrafting             Show detailed help for crafting commands
"""
        print(help_message)
        log_event("Displayed general help.", 'INFO')

    def help_commands(self, args: List[str]):
        """
        Provides detailed help for all commands.
        """
        self.help(args)

    def help_automation(self, args: List[str]):
        """
        Provides detailed help for automation-related commands.
        """
        automation_help = """
Automation Commands:
  editscript name          Edit a script using the in-game text editor
  runscript name           Run a specified script
  listscripts              List all available scripts
  createscript name        Create a new automation script
  deletescript name        Delete an existing script
  useitem name            Use an item from your inventory for automation
"""
        print(automation_help)
        log_event("Displayed automation help.", 'INFO')

    def help_crafting(self, args: List[str]):
        """
        Provides detailed help for crafting-related commands.
        """
        crafting_help = """
Crafting Commands:
  mine                     Mine a material and add it to your inventory
  inventory                Display your inventory
  place x y layer name     Place a material from inventory onto the crafting grid
  remove x y layer         Remove a material from the crafting grid back to inventory
  showgrid                 Display the crafting grid
  listrecipes              List all crafting recipes
  createrecipe             Create a new crafting recipe
  deleterecipe name        Delete an existing crafting recipe
"""
        print(crafting_help)
        log_event("Displayed crafting help.", 'INFO')

    def mine(self, args: List[str]):
        """
        Mines a new material and adds it to the player's inventory.
        """
        material = Material(
            id=generate_uuid(),
            name=generate_procedural_name(),
            rarity=self.get_random_rarity(),
            quality=random.uniform(0.1, 1.0),
            material_type=random.choice(['Metal', 'Mineral', 'Plant']),
            base_stone_type=random.choice(['Granite', 'Basalt', 'Marble'])
        )
        self.player.inventory.add_item(material)
        self.player.object_dictionary.add_to_category(material.material_type, material.id)
        print(f"Mined {material.name} (Rarity: {material.rarity}, Quality: {material.quality:.2f})")
        log_event(f"Player {self.player.name} mined {material.name}.", 'INFO')

    def get_random_rarity(self) -> str:
        """
        Determines the rarity of a newly mined material based on predefined probabilities.
        """
        rarity_levels = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']
        rarity_weights = [40, 30, 20, 8, 2]
        return random.choices(rarity_levels, weights=rarity_weights, k=1)[0]

    def show_inventory(self, args: List[str]):
        """
        Displays the player's current inventory.
        """
        if not self.player.inventory.items:
            print("Inventory is empty.")
            return
        print("Inventory:")
        for item in self.player.inventory.items.values():
            print(f"  ID: {item.material.id} | {item.material.name} x{item.quantity} (Rarity: {item.material.rarity})")
        log_event(f"Player {self.player.name} viewed inventory.", 'INFO')

    def place_item(self, args: List[str]):
        """
        Places an item from the inventory onto the crafting grid.
        Usage: place x y layer name
        """
        if len(args) < 4:
            print("Usage: place x y layer material_name")
            return
        try:
            x, y, layer = map(int, args[:3])
            name = ' '.join(args[3:]).capitalize()
            material_item = self.player.inventory.get_item_by_name(name)
            if material_item:
                if validate_coordinates(x, y, layer, self.player.crafting_grid.width, self.player.crafting_grid.height, self.player.crafting_grid.layers):
                    success = self.player.crafting_grid.place_item(x, y, layer, material_item.material)
                    if success:
                        self.player.inventory.remove_item(material_item.material.id)
                        print(f"Placed {material_item.material.name} at ({x}, {y}) on layer {layer}.")
                        log_event(f"Player {self.player.name} placed {material_item.material.name} on grid at ({x}, {y}, {layer}).", 'INFO')
                else:
                    print(f"Invalid coordinates: ({x}, {y}, {layer}).")
            else:
                print(f"Material '{name}' not found in inventory.")
        except ValueError:
            print("Invalid arguments. x, y, and layer should be integers.")
            log_event(f"Player {self.player.name} provided invalid arguments for 'place' command.", 'WARNING')

    def remove_item(self, args: List[str]):
        """
        Removes an item from the crafting grid back to the inventory.
        Usage: remove x y layer
        """
        if len(args) < 3:
            print("Usage: remove x y layer")
            return
        try:
            x, y, layer = map(int, args[:3])
            if validate_coordinates(x, y, layer, self.player.crafting_grid.width, self.player.crafting_grid.height, self.player.crafting_grid.layers):
                success, material = self.player.crafting_grid.remove_item(x, y, layer)
                if success and material:
                    self.player.inventory.add_item(material)
                    print(f"Removed {material.name} from ({x}, {y}) on layer {layer} back to inventory.")
                    log_event(f"Player {self.player.name} removed {material.name} from grid at ({x}, {y}, {layer}).", 'INFO')
                else:
                    print(f"No item found at ({x}, {y}) on layer {layer}).")
            else:
                print(f"Invalid coordinates: ({x}, {y}, {layer}).")
        except ValueError:
            print("Invalid arguments. x, y, and layer should be integers.")
            log_event(f"Player {self.player.name} provided invalid arguments for 'remove' command.", 'WARNING')

    def show_grid(self, args: List[str]):
        """
        Displays the current state of the crafting grid.
        """
        self.player.crafting_grid.display_grid()
        log_event(f"Player {self.player.name} viewed the crafting grid.", 'INFO')

    def exit_game(self, args: List[str]):
        """
        Exits the game gracefully.
        """
        confirmation = get_user_confirmation("Are you sure you want to exit? (y/n): ")
        if confirmation:
            print("Exiting Cradium Core. Goodbye!")
            log_event(f"Player {self.player.name} exited the game.", 'INFO')
            self.is_running = False
        else:
            print("Exit canceled.")

    def edit_script(self, args: List[str]):
        """
        Opens the in-game text editor to edit a specified script.
        Usage: editscript script_name
        """
        if len(args) < 1:
            print("Usage: editscript script_name")
            return
        script_name = ' '.join(args).strip()
        script = next((s for s in self.player.scripts if s.name.lower() == script_name.lower()), None)
        if script:
            print(f"Editing script '{script.name}'. Enter your script below. Type 'END' on a new line to finish.")
            lines = []
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
            script.content = '\n'.join(lines)
            script.last_modified = get_current_timestamp()
            print(f"Script '{script.name}' updated successfully.")
            log_event(f"Player {self.player.name} edited script '{script.name}'.", 'INFO')
        else:
            print(f"Script '{script_name}' not found.")
            log_event(f"Player {self.player.name} attempted to edit non-existent script '{script_name}'.", 'WARNING')

    def run_script(self, args: List[str]):
        """
        Executes a specified script.
        Usage: runscript script_name
        """
        if len(args) < 1:
            print("Usage: runscript script_name")
            return
        script_name = ' '.join(args).strip()
        script = next((s for s in self.player.scripts if s.name.lower() == script_name.lower()), None)
        if script:
            output = execute_script(script.content)
            if output:
                print(f"Script Output:\n{output}")
                log_event(f"Player {self.player.name} ran script '{script.name}' successfully.", 'INFO')
            else:
                print(f"Failed to execute script '{script.name}'. Check logs for details.")
                log_event(f"Player {self.player.name} failed to run script '{script.name}'.", 'ERROR')
        else:
            print(f"Script '{script_name}' not found.")
            log_event(f"Player {self.player.name} attempted to run non-existent script '{script_name}'.", 'WARNING')

    def list_scripts(self, args: List[str]):
        """
        Lists all available scripts for the player.
        """
        if not self.player.scripts:
            print("No scripts available.")
            return
        print("Available Scripts:")
        for script in self.player.scripts:
            print(f"  Name: {script.name} | Created At: {script.created_at} | Last Modified: {script.last_modified}")
        log_event(f"Player {self.player.name} listed scripts.", 'INFO')

    def create_script(self, args: List[str]):
        """
        Creates a new automation script.
        Usage: createscript script_name
        """
        if len(args) < 1:
            print("Usage: createscript script_name")
            return
        script_name = ' '.join(args).strip()
        existing_script = next((s for s in self.player.scripts if s.name.lower() == script_name.lower()), None)
        if existing_script:
            print(f"Script '{script_name}' already exists.")
            log_event(f"Player {self.player.name} attempted to create an existing script '{script_name}'.", 'WARNING')
            return
        new_script = Script(
            id=generate_uuid(),
            name=script_name,
            content='',
            created_at=get_current_timestamp(),
            last_modified=get_current_timestamp()
        )
        self.player.add_script(new_script)
        print(f"Script '{script_name}' created successfully. Use 'editscript {script_name}' to add content.")
        log_event(f"Player {self.player.name} created script '{script_name}'.", 'INFO')

    def delete_script(self, args: List[str]):
        """
        Deletes an existing script.
        Usage: deletescript script_name
        """
        if len(args) < 1:
            print("Usage: deletescript script_name")
            return
        script_name = ' '.join(args).strip()
        script = next((s for s in self.player.scripts if s.name.lower() == script_name.lower()), None)
        if script:
            confirmation = get_user_confirmation(f"Are you sure you want to delete script '{script.name}'? (y/n): ")
            if confirmation:
                self.player.scripts.remove(script)
                print(f"Script '{script.name}' deleted successfully.")
                log_event(f"Player {self.player.name} deleted script '{script.name}'.", 'INFO')
            else:
                print("Delete script canceled.")
        else:
            print(f"Script '{script_name}' not found.")
            log_event(f"Player {self.player.name} attempted to delete non-existent script '{script_name}'.", 'WARNING')

    def use_item(self, args: List[str]):
        """
        Uses an item from the inventory, triggering its passive or active effects.
        Usage: useitem item_name
        """
        if len(args) < 1:
            print("Usage: useitem item_name")
            return
        item_name = ' '.join(args).strip()
        inventory_item = self.player.inventory.get_item_by_name(item_name)
        if inventory_item:
            item = inventory_item.material  # Assuming items are stored as materials; adjust if different
            if item.item_type in ['PassiveCollector', 'ActiveCollector']:
                # Implement passive or active item effects
                print(f"Using item '{item.name}' of type '{item.item_type}'.")
                log_event(f"Player {self.player.name} used item '{item.name}'.", 'INFO')
                # Placeholder for actual effect implementation
            elif item.item_type == 'Ingredient':
                # Implement ingredient usage
                print(f"Using ingredient '{item.name}'.")
                log_event(f"Player {self.player.name} used ingredient '{item.name}'.", 'INFO')
                # Placeholder for actual effect implementation
            elif item.item_type == 'MachinePart':
                # Implement machine part usage
                print(f"Using machine part '{item.name}'.")
                log_event(f"Player {self.player.name} used machine part '{item.name}'.", 'INFO')
                # Placeholder for actual effect implementation
            elif item.item_type == 'CraftedItem':
                # Implement crafted item usage
                print(f"Using crafted item '{item.name}'.")
                log_event(f"Player {self.player.name} used crafted item '{item.name}'.", 'INFO')
                # Placeholder for actual effect implementation
            else:
                print(f"Item type '{item.item_type}' is not usable.")
                log_event(f"Player {self.player.name} attempted to use non-usable item type '{item.item_type}'.", 'WARNING')
        else:
            print(f"Item '{item_name}' not found in inventory.")
            log_event(f"Player {self.player.name} attempted to use non-existent item '{item_name}'.", 'WARNING')

    def list_recipes(self, args: List[str]):
        """
        Lists all available crafting recipes.
        """
        recipe_ids = self.player.object_dictionary.get_category_items('Recipe')
        if not recipe_ids:
            print("No crafting recipes available.")
            return
        print("Available Crafting Recipes:")
        for recipe_id in recipe_ids:
            recipe = self.get_recipe_by_id(recipe_id)
            if recipe:
                input_materials = ', '.join([f"{qty} x {self.get_material_name(mat_id)}" for mat_id, qty in recipe.input_materials.items()])
                print(f"  Name: {recipe.name} | Inputs: {input_materials} | Output: {recipe.output_item.name} | Build Time: {format_time(recipe.build_time)}")
        log_event(f"Player {self.player.name} listed all recipes.", 'INFO')

    def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """
        Retrieves a recipe by its ID.
        Placeholder implementation; adjust based on how recipes are stored.
        """
        # Placeholder: Implement recipe storage and retrieval
        # For example, store recipes in a global list or within the player object
        return None  # Replace with actual retrieval logic

    def create_recipe(self, args: List[str]):
        """
        Creates a new crafting recipe.
        Usage: createrecipe
        """
        print("Creating a new crafting recipe.")
        name = input("Enter recipe name: ").strip()
        if not name:
            print("Recipe name cannot be empty.")
            return
        existing_recipe = self.find_recipe_by_name(name)
        if existing_recipe:
            print(f"Recipe '{name}' already exists.")
            log_event(f"Player {self.player.name} attempted to create an existing recipe '{name}'.", 'WARNING')
            return
        input_materials = {}
        print("Enter required materials (type 'done' when finished):")
        while True:
            mat_name = input("  Material name: ").strip()
            if mat_name.lower() == 'done':
                break
            qty_input = input("  Quantity: ").strip()
            if qty_input.lower() == 'done':
                break
            try:
                qty = int(qty_input)
                material = self.player.inventory.get_item_by_name(mat_name)
                if material:
                    input_materials[material.material.id] = qty
                else:
                    print(f"Material '{mat_name}' not found in inventory. Please mine or add it first.")
            except ValueError:
                print("Invalid quantity. Please enter an integer.")
        if not input_materials:
            print("No materials added. Recipe creation canceled.")
            return
        output_name = input("Enter output item name: ").strip()
        if not output_name:
            print("Output item name cannot be empty.")
            return
        output_item = Item(
            id=generate_uuid(),
            name=output_name,
            description=f"A crafted item named {output_name}.",
            item_type='CraftedItem',
            properties={}
        )
        build_time_input = input("Enter build time in seconds: ").strip()
        try:
            build_time = float(build_time_input)
        except ValueError:
            print("Invalid build time. Please enter a number.")
            return
        required_grid_layers_input = input(f"Enter required grid layers (integer, max {self.player.crafting_grid.layers}): ").strip()
        try:
            required_grid_layers = int(required_grid_layers_input)
            if required_grid_layers > self.player.crafting_grid.layers or required_grid_layers < 1:
                print(f"Invalid number of layers. Must be between 1 and {self.player.crafting_grid.layers}.")
                return
        except ValueError:
            print("Invalid number of layers. Please enter an integer.")
            return
        new_recipe = Recipe(
            id=generate_uuid(),
            name=name,
            input_materials=input_materials,
            output_item=output_item,
            required_grid_layers=required_grid_layers,
            build_time=build_time
        )
        self.player.object_dictionary.add_to_category('Recipe', new_recipe.id)
        print(f"Recipe '{name}' created successfully.")
        log_event(f"Player {self.player.name} created recipe '{name}'.", 'INFO')

    def find_recipe_by_name(self, name: str) -> Optional[Recipe]:
        """
        Finds a recipe by its name.
        Placeholder implementation; adjust based on how recipes are stored.
        """
        # Placeholder: Implement recipe search
        return None  # Replace with actual search logic

    def delete_recipe(self, args: List[str]):
        """
        Deletes an existing crafting recipe.
        Usage: deleterecipe recipe_name
        """
        if len(args) < 1:
            print("Usage: deleterecipe recipe_name")
            return
        recipe_name = ' '.join(args).strip()
        recipe = self.find_recipe_by_name(recipe_name)
        if recipe:
            confirmation = get_user_confirmation(f"Are you sure you want to delete recipe '{recipe.name}'? (y/n): ")
            if confirmation:
                self.player.object_dictionary.remove_from_category('Recipe', recipe.id)
                print(f"Recipe '{recipe.name}' deleted successfully.")
                log_event(f"Player {self.player.name} deleted recipe '{recipe.name}'.", 'INFO')
            else:
                print("Delete recipe canceled.")
        else:
            print(f"Recipe '{recipe_name}' not found.")
            log_event(f"Player {self.player.name} attempted to delete non-existent recipe '{recipe_name}'.", 'WARNING')

    def list_machines(self, args: List[str]):
        """
        Lists all machines owned by the player.
        """
        if not self.player.machines:
            print("No machines owned.")
            return
        print("Owned Machines:")
        for machine in self.player.machines:
            print(f"  ID: {machine.id} | Name: {machine.name} | HP: {machine.hp} | Functionality: {machine.functionality} | Cooldown: {format_time(machine.cooldown_time)}")
        log_event(f"Player {self.player.name} listed all machines.", 'INFO')

    def add_machine(self, args: List[str]):
        """
        Adds a new machine to the player's inventory.
        Usage: addmachine machine_name
        """
        if len(args) < 1:
            print("Usage: addmachine machine_name")
            return
        machine_name = ' '.join(args).strip()
        existing_machine = next((m for m in self.player.machines if m.name.lower() == machine_name.lower()), None)
        if existing_machine:
            print(f"Machine '{machine_name}' already exists in your inventory.")
            log_event(f"Player {self.player.name} attempted to add existing machine '{machine_name}'.", 'WARNING')
            return
        hp_input = input("Enter machine HP (e.g., 100.0): ").strip()
        try:
            hp = float(hp_input)
        except ValueError:
            print("Invalid HP value. Please enter a number.")
            return
        functionality = input("Enter machine functionality description: ").strip()
        cooldown_input = input("Enter machine cooldown time in seconds: ").strip()
        try:
            cooldown_time = float(cooldown_input)
        except ValueError:
            print("Invalid cooldown time. Please enter a number.")
            return
        new_machine = Machine(
            id=generate_uuid(),
            name=machine_name,
            hp=hp,
            parts=[],  # Initially no parts; can be added later
            functionality=functionality,
            cooldown_time=cooldown_time
        )
        self.player.add_machine(new_machine)
        print(f"Machine '{machine_name}' added successfully.")
        log_event(f"Player {self.player.name} added machine '{machine_name}'.", 'INFO')

    def remove_machine(self, args: List[str]):
        """
        Removes a machine from the player's inventory.
        Usage: removemachine machine_name
        """
        if len(args) < 1:
            print("Usage: removemachine machine_name")
            return
        machine_name = ' '.join(args).strip()
        machine = next((m for m in self.player.machines if m.name.lower() == machine_name.lower()), None)
        if machine:
            confirmation = get_user_confirmation(f"Are you sure you want to remove machine '{machine.name}'? (y/n): ")
            if confirmation:
                self.player.machines.remove(machine)
                print(f"Machine '{machine.name}' removed successfully.")
                log_event(f"Player {self.player.name} removed machine '{machine.name}'.", 'INFO')
            else:
                print("Remove machine canceled.")
        else:
            print(f"Machine '{machine_name}' not found in your inventory.")
            log_event(f"Player {self.player.name} attempted to remove non-existent machine '{machine_name}'.", 'WARNING')

    def list_plants(self, args: List[str]):
        """
        Lists all plants owned by the player.
        """
        if not self.player.plants:
            print("No plants owned.")
            return
        print("Owned Plants:")
        for plant in self.player.plants:
            print(f"  ID: {plant.id} | Species: {plant.genetics.species} | Growth Stage: {plant.current_growth_stage}/{plant.max_growth_stage} | Health: {plant.health} | Conditions: {plant.environment_conditions}")
        log_event(f"Player {self.player.name} listed all plants.", 'INFO')

    def add_plant(self, args: List[str]):
        """
        Adds a new plant to the player's collection.
        Usage: addplant species
        """
        if len(args) < 1:
            print("Usage: addplant species")
            return
        species = ' '.join(args).strip()
        existing_plant = next((p for p in self.player.plants if p.genetics.species.lower() == species.lower()), None)
        if existing_plant:
            print(f"Plant species '{species}' already exists in your collection.")
            log_event(f"Player {self.player.name} attempted to add existing plant species '{species}'.", 'WARNING')
            return
        genetic_traits = {
            'growth_rate': random.uniform(0.5, 2.0),  # Example trait
            'resistance': random.uniform(0.0, 1.0),
            'yield': random.randint(1, 10)
        }
        new_genetics = PlantGenetics(
            id=generate_uuid(),
            species=species,
            genetic_traits=genetic_traits
        )
        new_plant = Plant(
            id=generate_uuid(),
            genetics=new_genetics,
            current_growth_stage=0,
            max_growth_stage=5,
            health=100.0,
            environment_conditions={'light': 'medium', 'water': 'regular', 'soil': 'fertile'}
        )
        self.player.add_plant(new_plant)
        print(f"Plant '{species}' added successfully.")
        log_event(f"Player {self.player.name} added plant '{species}'.", 'INFO')

    def remove_plant(self, args: List[str]):
        """
        Removes a plant from the player's collection by its ID.
        Usage: removeplant plant_id
        """
        if len(args) < 1:
            print("Usage: removeplant plant_id")
            return
        plant_id = args[0].strip()
        plant = next((p for p in self.player.plants if p.id == plant_id), None)
        if plant:
            confirmation = get_user_confirmation(f"Are you sure you want to remove plant '{plant.genetics.species}'? (y/n): ")
            if confirmation:
                self.player.plants.remove(plant)
                print(f"Plant '{plant.genetics.species}' removed successfully.")
                log_event(f"Player {self.player.name} removed plant '{plant.genetics.species}'.", 'INFO')
            else:
                print("Remove plant canceled.")
        else:
            print(f"Plant with ID '{plant_id}' not found.")
            log_event(f"Player {self.player.name} attempted to remove non-existent plant ID '{plant_id}'.", 'WARNING')

    def save_game(self, args: List[str]):
        """
        Saves the current game state to a file.
        Usage: savegame [filename]
        """
        filename = args[0] if args else 'savegame.json'
        success = save_game_state(self.player, filename)
        if success:
            print(f"Game saved successfully to '{filename}'.")
        else:
            print(f"Failed to save game to '{filename}'. Check logs for details.")

    def load_game(self, args: List[str]):
        """
        Loads the game state from a file.
        Usage: loadgame [filename]
        """
        filename = args[0] if args else 'savegame.json'
        loaded_player = load_game_state(filename)
        if loaded_player:
            self.player = loaded_player
            print(f"Game loaded successfully from '{filename}'.")
            log_event(f"Player {self.player.name} loaded game from '{filename}'.", 'INFO')
        else:
            print(f"Failed to load game from '{filename}'. Check logs for details.")

    def create_script_language(self, args: List[str]):
        """
        Placeholder for creating a new scripting language or extending existing one.
        Future implementation can include defining syntax, parser, and interpreter.
        """
        print("Creating a new scripting language is not yet implemented.")
        log_event(f"Player {self.player.name} attempted to create a new scripting language.", 'WARNING')

    # Additional helper methods

    def get_all_recipes(self) -> List[Recipe]:
        """
        Retrieves all recipes from the player's object dictionary.
        """
        recipe_ids = self.player.object_dictionary.get_category_items('Recipe')
        recipes = []
        for rid in recipe_ids:
            # Placeholder: Implement recipe retrieval logic
            # For demonstration, we'll skip actual retrieval
            pass
        return recipes

    def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """
        Retrieves a recipe by its ID.
        Placeholder implementation; adjust based on how recipes are stored.
        """
        # Placeholder: Implement recipe storage and retrieval
        # For example, store recipes in a global list or within the player object
        return None  # Replace with actual retrieval logic

    def find_recipe_by_name(self, name: str) -> Optional[Recipe]:
        """
        Finds a recipe by its name.
        Placeholder implementation; adjust based on how recipes are stored.
        """
        # Placeholder: Implement recipe search
        return None  # Replace with actual search logic

    def get_material_name(self, material_id: str) -> str:
        """
        Retrieves the name of a material by its ID.
        """
        for item in self.player.inventory.items.values():
            if item.material.id == material_id:
                return item.material.name
        # Search in crafting grid
        for layer in self.player.crafting_grid.grid:
            for row in layer:
                for material in row:
                    if material and material.id == material_id:
                        return material.name
        return "Unknown"

# -----------------------------
# Command-Line Interface
# -----------------------------

class CradiumCLI:
    """
    Handles the user interface and integrates the command parser.
    """

    def __init__(self, player: Player):
        self.player = player
        self.parser = CommandParser(self.player)

    def start(self):
        print("Welcome to Cradium Core!")
        print("Type 'help' to see available commands.\n")
        while self.parser.is_running:
            try:
                user_input = input("(cradium) ")
                self.parser.parse(user_input)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting Cradium Core. Goodbye!")
                log_event(f"Player {self.player.name} exited the game via interrupt.", 'INFO')
                break

# -----------------------------
# Game Class
# -----------------------------

class Game:
    """
    Manages the overall game state and progression.
    """

    def __init__(self, player_name: str):
        self.player = Player(name=player_name)
        # Initialize game state, e.g., base setup
        self.player.initialize_base()

    def run(self):
        # Placeholder for additional game mechanics like resource regeneration, cooldowns, etc.
        pass

# -----------------------------
# Main Entry Point
# -----------------------------

def main():
    player_name = input("Enter your player name: ").strip()
    if not player_name:
        print("Player name cannot be empty.")
        return
    game = Game(player_name)
    cli = CradiumCLI(game.player)
    cli.start()

if __name__ == "__main__":
    main()
