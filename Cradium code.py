import uuid
import random
import time
import logging
import sys
import shlex
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable

# Kivy imports
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
import functools
from kivy.clock import Clock

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
    return str(uuid.uuid4())

def generate_procedural_name(syllables: Optional[list] = None, min_syllables: int = 2, max_syllables: int = 3) -> str:
    if syllables is None:
        syllables = ['Crad', 'Ium', 'Vex', 'Lun', 'Tori', 'Plas', 'Zynth', 'Nor', 'Del', 'Xar']
    name_length = random.randint(min_syllables, max_syllables)
    name = ''.join(random.choice(syllables) for _ in range(name_length))
    return name.capitalize()

def get_current_timestamp() -> str:
    return datetime.utcnow().isoformat()

def validate_coordinates(x: int, y: int, layer: int, grid_width: int, grid_height: int, grid_layers: int) -> bool:
    if 0 <= x < grid_width and 0 <= y < grid_height and 0 <= layer < grid_layers:
        return True
    else:
        logging.warning(f"Invalid coordinates attempted: ({x}, {y}, {layer})")
        return False

def log_event(message: str, level: str = 'INFO'):
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

def save_game_state(player: 'Player', filename: str = 'savegame.json') -> bool:
    try:
        with open(filename, 'w') as file:
            json.dump(player.to_dict(), file, indent=4, default=str)
        logging.info("Game state saved successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to save game state: {e}")
        return False

def load_game_state(filename: str = 'savegame.json') -> Optional['Player']:
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        player = Player.from_dict(data)
        logging.info("Game state loaded successfully.")
        return player
    except Exception as e:
        logging.error(f"Failed to load game state: {e}")
        return None

def format_time(seconds: float) -> str:
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours}h {mins}m {secs}s"

# -----------------------------
# Data Models
# -----------------------------

@dataclass
class Material:
    id: str
    name: str
    rarity: str
    quality: float
    material_type: str
    base_stone_type: str

    def to_dict(self) -> Dict:
        return self.__dict__

@dataclass
class InventoryItem:
    material: Material
    quantity: int = 1

@dataclass
class Inventory:
    items: Dict[str, InventoryItem] = field(default_factory=dict)

    def add_item(self, material: Material, quantity: int = 1):
        if material.id in self.items:
            self.items[material.id].quantity += quantity
        else:
            self.items[material.id] = InventoryItem(material, quantity)
        log_event(f"Added {quantity} x {material.name} to inventory.", 'DEBUG')

    def remove_item(self, material_id: str, quantity: int = 1) -> bool:
        if material_id in self.items and self.items[material_id].quantity >= quantity:
            self.items[material_id].quantity -= quantity
            if self.items[material_id].quantity == 0:
                del self.items[material_id]
            log_event(f"Removed {quantity} x {material_id} from inventory.", 'DEBUG')
            return True
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
                'material': item.material.to_dict(),
                'quantity': item.quantity
            }
            for material_id, item in self.items.items()
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Inventory':
        inventory = Inventory()
        for material_id, item_data in data.items():
            material_data = item_data['material']
            # Use MATERIALS_LOOKUP to get the material
            if material_id in MATERIALS_LOOKUP:
                material = MATERIALS_LOOKUP[material_id]
            else:
                # Material not found in lookup, reconstruct from data
                material = Material(**material_data)
                MATERIALS_LOOKUP[material_id] = material
            inventory.items[material_id] = InventoryItem(material, item_data['quantity'])
        return inventory

@dataclass
class CraftingGrid:
    width: int = 5
    height: int = 5
    layers: int = 1
    grid: List[List[List[Optional[Material]]]] = field(init=False)

    def __post_init__(self):
        self.grid = [[[None for _ in range(self.width)] for _ in range(self.height)] for _ in range(self.layers)]
        log_event(f"Initialized Crafting Grid with {self.layers} layers of {self.width}x{self.height}.", 'DEBUG')

    def place_item(self, x: int, y: int, layer: int, material: Material) -> bool:
        if self.is_valid_position(x, y, layer):
            if self.grid[layer][y][x] is None:
                self.grid[layer][y][x] = material
                log_event(f"Placed {material.name} at ({x}, {y}) on layer {layer}.", 'INFO')
                return True
            else:
                log_event(f"Attempted to place {material.name} at occupied position ({x}, {y}, {layer}).", 'WARNING')
        else:
            log_event(f"Attempted to place item at invalid position ({x}, {y}, {layer}).", 'WARNING')
        return False

    def remove_item(self, x: int, y: int, layer: int) -> (bool, Optional[Material]):
        if self.is_valid_position(x, y, layer):
            material = self.grid[layer][y][x]
            if material:
                self.grid[layer][y][x] = None
                log_event(f"Removed {material.name} from ({x}, {y}) on layer {layer}.", 'INFO')
                return True, material
            else:
                log_event(f"Attempted to remove item from empty position ({x}, {y}, {layer}).", 'WARNING')
                return False, None
        else:
            log_event(f"Attempted to remove item from invalid position ({x}, {y}, {layer}).", 'WARNING')
            return False, None

    def is_valid_position(self, x: int, y: int, layer: int) -> bool:
        return validate_coordinates(x, y, layer, self.width, self.height, self.layers)

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
class Machine:
    id: str
    name: str
    description: str
    properties: Dict[str, Any]
    crafting_grid: Optional[CraftingGrid] = None
    cooldown_time: float = 0.0
    last_used_time: float = field(default_factory=time.time)
    power: float = 0.0  # Power level of the machine
    active: bool = False  # Whether the machine is currently active

    def to_dict(self) -> Dict:
        data = self.__dict__.copy()
        if self.crafting_grid:
            data['crafting_grid'] = self.crafting_grid.to_dict()
        return data

    @staticmethod
    def from_dict(data: Dict) -> 'Machine':
        crafting_grid = None
        if data.get('crafting_grid'):
            crafting_grid = CraftingGrid.from_dict(data['crafting_grid'], MATERIALS_LOOKUP)
        return Machine(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            properties=data['properties'],
            crafting_grid=crafting_grid,
            cooldown_time=data.get('cooldown_time', 0.0),
            last_used_time=data.get('last_used_time', time.time()),
            power=data.get('power', 0.0),
            active=data.get('active', False)
        )

    def can_use(self) -> bool:
        return time.time() - self.last_used_time >= self.cooldown_time

    def use(self):
        if self.can_use():
            self.last_used_time = time.time()
            # Implement machine's functionality here
            return True
        else:
            return False

@dataclass
class CraftingRecipe:
    id: str
    name: str
    ingredients: Dict[str, int]  # material_id to quantity
    output: Material
    output_quantity: int

# Global variables for materials and recipes
MATERIALS_LOOKUP = {}
RECIPES = {}

def load_sample_recipes():
    global MATERIALS_LOOKUP
    global RECIPES

    # Define some sample materials to use in recipes
    material_iron = Material(
        id='iron',
        name='Iron',
        rarity='Common',
        quality=1.0,
        material_type='Metal',
        base_stone_type=''
    )
    material_wood = Material(
        id='wood',
        name='Wood',
        rarity='Common',
        quality=1.0,
        material_type='Wood',
        base_stone_type=''
    )
    material_pickaxe = Material(
        id='pickaxe',
        name='Iron Pickaxe',
        rarity='Uncommon',
        quality=1.0,
        material_type='Tool',
        base_stone_type=''
    )

    # Add these materials to a materials lookup
    MATERIALS_LOOKUP.update({
        'iron': material_iron,
        'wood': material_wood,
        'pickaxe': material_pickaxe,
    })

    # Define recipes
    recipe_pickaxe = CraftingRecipe(
        id='recipe_pickaxe',
        name='Iron Pickaxe',
        ingredients={
            'iron': 3,
            'wood': 2
        },
        output=material_pickaxe,
        output_quantity=1
    )

    RECIPES['recipe_pickaxe'] = recipe_pickaxe

@dataclass
class Player:
    name: str
    inventory: Inventory = field(default_factory=Inventory)
    crafting_grid: CraftingGrid = field(default_factory=CraftingGrid)
    base_initialized: bool = False
    machines: List[Machine] = field(default_factory=list)
    developer_mode: bool = False
    power: float = 0.0  # Player's available power

    def initialize_base(self):
        self.base_initialized = True
        log_event(f"Base initialized for player {self.name}.", 'INFO')

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'inventory': self.inventory.to_dict(),
            'crafting_grid': self.crafting_grid.to_dict(),
            'base_initialized': self.base_initialized,
            'machines': [machine.to_dict() for machine in self.machines],
            'developer_mode': self.developer_mode,
            'power': self.power,
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Player':
        inventory = Inventory.from_dict(data['inventory'])
        materials_lookup = MATERIALS_LOOKUP
        crafting_grid = CraftingGrid.from_dict(data['crafting_grid'], materials_lookup)
        machines = [Machine.from_dict(m) for m in data.get('machines', [])]
        player = Player(
            name=data['name'],
            inventory=inventory,
            crafting_grid=crafting_grid,
            base_initialized=data['base_initialized'],
            machines=machines,
            developer_mode=data.get('developer_mode', False),
            power=data.get('power', 0.0),
        )
        return player

    def update_machines(self):
        for machine in self.machines:
            if machine.active and machine.can_use():
                self.power += machine.power  # Update power based on machine output
                machine.use()
                # For resource generation
                if 'resource_output' in machine.properties:
                    material = Material(
                        id=generate_uuid(),
                        name=machine.properties['resource_output'],
                        rarity='Common',
                        quality=1.0,
                        material_type='Generated',
                        base_stone_type=''
                    )
                    self.inventory.add_item(material)
                    log_event(f"Machine {machine.name} produced {material.name}.", 'INFO')

    def craft_item(self, recipe_id) -> bool:
        if recipe_id in RECIPES:
            recipe = RECIPES[recipe_id]
            # Check if the player has the required ingredients
            has_all_ingredients = True
            for material_id, quantity in recipe.ingredients.items():
                if material_id not in self.inventory.items or self.inventory.items[material_id].quantity < quantity:
                    has_all_ingredients = False
                    break
            if has_all_ingredients:
                # Remove ingredients from inventory
                for material_id, quantity in recipe.ingredients.items():
                    self.inventory.remove_item(material_id, quantity)
                # Add the crafted item to inventory
                self.inventory.add_item(recipe.output, recipe.output_quantity)
                log_event(f"Crafted {recipe.output_quantity} x {recipe.output.name}", 'INFO')
                return True
            else:
                log_event(f"Not enough materials to craft {recipe.output.name}", 'WARNING')
                return False
        else:
            log_event(f"Recipe {recipe_id} not found", 'ERROR')
            return False

# -----------------------------
# Kivy App
# -----------------------------

KV = '''
ScreenManager:
    MenuScreen:
    GameScreen:
    InventoryScreen:
    GridScreen:
    MachinesScreen
    CraftingScreen:

<MenuScreen>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            text: 'Welcome to Cradium Core!'
            font_size: '24sp'
        TextInput:
            id: player_name_input
            hint_text: 'Enter your player name'
            size_hint_y: None
            height: '40dp'
        Button:
            text: 'Start Game'
            size_hint_y: None
            height: '40dp'
            on_press:
                app.start_game(player_name_input.text)
        Button:
            text: 'Exit'
            size_hint_y: None
            height: '40dp'
            on_press:
                app.stop()

<GameScreen>:
    name: 'game'
    BoxLayout:
        orientation: 'vertical'
        TextInput:
            id: output_console
            text: ''
            readonly: True
            size_hint_y: 0.8
        TextInput:
            id: input_command
            hint_text: 'Enter command'
            multiline: False
            size_hint_y: None
            height: '40dp'
            on_text_validate:
                app.process_input(input_command.text)
                input_command.text = ''
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            spacing: 10
            Button:
                text: 'Inventory'
                on_press:
                    app.show_inventory()
            Button:
                text: 'Crafting Grid'
                on_press:
                    app.show_grid()
            Button:
                text: 'Crafting Table'
                on_press:
                    app.show_crafting()
            Button:
                text: 'Machines'
                on_press:
                    app.show_machines()
            Button:
                text: 'Modes'
                on_press:
                    app.show_modes()
            Button:
                text: 'Exit'
                on_press:
                    app.exit_game()

<InventoryScreen>:
    name: 'inventory'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            GridLayout:
                id: inventory_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: 'Back to Game'
            size_hint_y: None
            height: '48dp'
            on_press:
                app.go_back_to_game()

<GridScreen>:
    name: 'grid'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            GridLayout:
                id: grid_layout
                cols: 5
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            spacing: 10
            Button:
                text: 'Back to Game'
                on_press:
                    app.go_back_to_game()
            Button:
                text: 'Clear Grid'
                on_press:
                    app.clear_grid()
            Button:
                text: 'Craft'
                on_press:
                    app.craft_from_grid()

<MachinesScreen>:
    name: 'machines'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            text: 'Power Level: ' + app.get_power_level()
            size_hint_y: None
            height: '40dp'
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            GridLayout:
                id: machines_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            spacing: 10
            Button:
                text: 'Add Machine'
                on_press:
                    app.add_machine()
            Button:
                text: 'Back to Game'
                on_press:
                    app.go_back_to_game()

<CraftingScreen>:
    name: 'crafting'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            GridLayout:
                id: recipes_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: 'Back to Game'
            size_hint_y: None
            height: '48dp'
            on_press:
                app.go_back_to_game()
'''

class MenuScreen(Screen):
    pass

class GameScreen(Screen):
    output_console = ObjectProperty(None)
    input_command = ObjectProperty(None)

class InventoryScreen(Screen):
    inventory_grid = ObjectProperty(None)

class GridScreen(Screen):
    grid_layout = ObjectProperty(None)

class MachinesScreen(Screen):
    machines_grid = ObjectProperty(None)

class CraftingScreen(Screen):
    recipes_grid = ObjectProperty(None)

class CradiumApp(App):
    def build(self):
        self.player = None
        self.screen_manager = Builder.load_string(KV)
        load_sample_recipes()
        return self.screen_manager

    def get_power_level(self):
        if self.player:
            return str(round(self.player.power, 2))
        else:
            return '0.0'

    def start_game(self, player_name):
        if not player_name:
            player_name = "Player1"
        self.player = Player(name=player_name)
        self.player.initialize_base()
        self.screen_manager.current = 'game'
        self.update_output("Game started. Type 'mine' to gather materials.")
        Clock.schedule_interval(self.update_game_state, 1)

    def process_input(self, input_text):
        tokens = shlex.split(input_text)
        if not tokens:
            return
        command = tokens[0].lower()
        args = tokens[1:]
        if command == 'mine':
            self.mine()
        elif command == 'help':
            self.update_output("Available commands: mine, help")
        else:
            self.update_output(f"Unknown command: '{command}'. Type 'help' for a list of commands.")

    def update_output(self, message):
        game_screen = self.screen_manager.get_screen('game')
        console = game_screen.ids.output_console
        console.text += message + '\n'
        # Auto-scroll to the bottom
        console.cursor = (0, len(console.text.split('\n')))

    def mine(self):
        # Randomly choose between iron and wood
        materials = [MATERIALS_LOOKUP['iron'], MATERIALS_LOOKUP['wood']]
        material = random.choice(materials)
        self.player.inventory.add_item(material)
        self.update_output(f"Mined {material.name} (Rarity: {material.rarity}, Quality: {material.quality:.2f})")

    def show_inventory(self):
        inventory_screen = self.screen_manager.get_screen('inventory')
        inventory_grid = inventory_screen.ids.inventory_grid
        inventory_grid.clear_widgets()
        for item in self.player.inventory.list_inventory():
            item_button = Button(
                text=f"{item.material.name} x{item.quantity}",
                size_hint_y=None,
                height='40dp',
                on_press=functools.partial(self.show_material_details, item.material)
            )
            inventory_grid.add_widget(item_button)
        self.screen_manager.current = 'inventory'

    def show_material_details(self, material, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"Name: {material.name}"))
        content.add_widget(Label(text=f"Rarity: {material.rarity}"))
        content.add_widget(Label(text=f"Quality: {material.quality:.2f}"))
        content.add_widget(Label(text=f"Type: {material.material_type}"))
        content.add_widget(Label(text=f"Base Stone: {material.base_stone_type}"))
        close_button = Button(text='Close', size_hint_y=None, height='40dp')
        content.add_widget(close_button)
        popup = Popup(title='Material Details', content=content, size_hint=(0.6, 0.6))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def go_back_to_game(self):
        self.screen_manager.current = 'game'

    def show_grid(self):
        grid_screen = self.screen_manager.get_screen('grid')
        grid_layout = grid_screen.ids.grid_layout
        grid_layout.clear_widgets()
        grid = self.player.crafting_grid.grid[0]
        for y in range(self.player.crafting_grid.height):
            for x in range(self.player.crafting_grid.width):
                material = grid[y][x]
                btn_text = material.name if material else 'Empty'
                btn_color = (0.6, 0.6, 0.6, 1) if material else (0.8, 0.8, 0.8, 1)
                btn = Button(
                    text=btn_text,
                    background_color=btn_color,
                    size_hint_y=None,
                    height='60dp',
                    on_press=functools.partial(self.edit_grid_cell, x, y)
                )
                grid_layout.add_widget(btn)
        self.screen_manager.current = 'grid'

    def edit_grid_cell(self, x, y, *args):
        # Show a popup to place or remove material
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        material_items = self.player.inventory.list_inventory()
        if material_items:
            for item in material_items:
                btn = Button(text=item.material.name, size_hint_y=None, height='40dp')
                btn.bind(on_press=functools.partial(self.place_material_in_grid, x, y, item.material))
                content.add_widget(btn)
        else:
            content.add_widget(Label(text='No materials in inventory.'))
        remove_btn = Button(text='Remove', size_hint_y=None, height='40dp')
        remove_btn.bind(on_press=functools.partial(self.remove_material_from_grid, x, y))
        content.add_widget(remove_btn)
        close_button = Button(text='Close', size_hint_y=None, height='40dp')
        content.add_widget(close_button)
        popup = Popup(title=f'Edit Cell ({x}, {y})', content=content, size_hint=(0.6, 0.8))
        close_button.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()

    def place_material_in_grid(self, x, y, material, *args):
        material_item = self.player.inventory.get_item_by_name(material.name)
        if material_item:
            success = self.player.crafting_grid.place_item(x, y, 0, material_item.material)
            if success:
                self.player.inventory.remove_item(material_item.material.id)
                self.update_output(f"Placed {material_item.material.name} at ({x}, {y}) on grid.")
            else:
                self.update_output(f"Failed to place {material_item.material.name} at ({x}, {y}).")
            self.current_popup.dismiss()
            self.show_grid()
        else:
            self.update_output(f"Material '{material.name}' not found in inventory.")

    def remove_material_from_grid(self, x, y, *args):
        success, material = self.player.crafting_grid.remove_item(x, y, 0)
        if success and material:
            self.player.inventory.add_item(material)
            self.update_output(f"Removed {material.name} from ({x}, {y}) back to inventory.")
        else:
            self.update_output(f"No material to remove at ({x}, {y}).")
        self.current_popup.dismiss()
        self.show_grid()

    def clear_grid(self):
        for y in range(self.player.crafting_grid.height):
            for x in range(self.player.crafting_grid.width):
                success, material = self.player.crafting_grid.remove_item(x, y, 0)
                if success and material:
                    self.player.inventory.add_item(material)
        self.update_output("Cleared the crafting grid.")
        self.show_grid()

    def craft_from_grid(self):
        # Placeholder for crafting from grid
        self.update_output("Crafting from grid is not yet implemented.")

    def show_machines(self):
        machines_screen = self.screen_manager.get_screen('machines')
        machines_grid = machines_screen.ids.machines_grid
        machines_grid.clear_widgets()
        for machine in self.player.machines:
            machine_button = Button(
                text=f"{machine.name} ({'Active' if machine.active else 'Inactive'})",
                size_hint_y=None,
                height='40dp',
                on_press=functools.partial(self.show_machine_details, machine)
            )
            machines_grid.add_widget(machine_button)
        self.screen_manager.current = 'machines'

    def show_machine_details(self, machine, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"Name: {machine.name}"))
        content.add_widget(Label(text=f"Description: {machine.description}"))
        content.add_widget(Label(text=f"Power: {machine.power}"))
        content.add_widget(Label(text=f"Cooldown Time: {machine.cooldown_time}s"))
        properties_text = "\n".join([f"{k}: {v}" for k, v in machine.properties.items()])
        content.add_widget(Label(text=f"Properties:\n{properties_text}"))
        toggle_button = Button(text='Activate' if not machine.active else 'Deactivate', size_hint_y=None, height='40dp')
        toggle_button.bind(on_press=functools.partial(self.toggle_machine, machine))
        content.add_widget(toggle_button)
        close_button = Button(text='Close', size_hint_y=None, height='40dp')
        content.add_widget(close_button)
        popup = Popup(title='Machine Details', content=content, size_hint=(0.6, 0.8))
        close_button.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()

    def toggle_machine(self, machine, *args):
        machine.active = not machine.active
        status = 'activated' if machine.active else 'deactivated'
        self.update_output(f"Machine '{machine.name}' has been {status}.")
        self.current_popup.dismiss()
        self.show_machines()

    def add_machine(self):
        def create_machine(instance):
            name = name_input.text.strip()
            description = desc_input.text.strip()
            resource_output = resource_input.text.strip()
            cooldown = float(cooldown_input.text.strip()) if cooldown_input.text.strip() else 0.0
            power = float(power_input.text.strip()) if power_input.text.strip() else 0.0
            grid_width = int(grid_width_input.text.strip()) if grid_width_input.text.strip() else 5
            grid_height = int(grid_height_input.text.strip()) if grid_height_input.text.strip() else 5
            if not name:
                self.update_output("Machine name cannot be empty.")
                return
            properties = {'resource_output': resource_output} if resource_output else {}
            crafting_grid = CraftingGrid(width=grid_width, height=grid_height)
            new_machine = Machine(
                id=generate_uuid(),
                name=name,
                description=description,
                properties=properties,
                crafting_grid=crafting_grid,
                cooldown_time=cooldown,
                power=power,
                active=False
            )
            self.player.machines.append(new_machine)
            self.update_output(f"Machine '{name}' added.")
            self.current_popup.dismiss()
            self.show_machines()

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        name_input = TextInput(hint_text='Machine Name', multiline=False, size_hint_y=None, height='40dp')
        desc_input = TextInput(hint_text='Description', multiline=False, size_hint_y=None, height='40dp')
        resource_input = TextInput(hint_text='Resource Output', multiline=False, size_hint_y=None, height='40dp')
        cooldown_input = TextInput(hint_text='Cooldown Time (s)', multiline=False, size_hint_y=None, height='40dp')
        power_input = TextInput(hint_text='Power (positive for generation, negative for consumption)', multiline=False, size_hint_y=None, height='40dp')
        grid_width_input = TextInput(hint_text='Grid Width', multiline=False, size_hint_y=None, height='40dp')
        grid_height_input = TextInput(hint_text='Grid Height', multiline=False, size_hint_y=None, height='40dp')
        content.add_widget(name_input)
        content.add_widget(desc_input)
        content.add_widget(resource_input)
        content.add_widget(cooldown_input)
        content.add_widget(power_input)
        content.add_widget(grid_width_input)
        content.add_widget(grid_height_input)
        add_button = Button(text='Create Machine', size_hint_y=None, height='40dp')
        add_button.bind(on_press=create_machine)
        content.add_widget(add_button)
        close_button = Button(text='Cancel', size_hint_y=None, height='40dp')
        content.add_widget(close_button)
        popup = Popup(title='Add New Machine', content=content, size_hint=(0.8, 0.9))
        close_button.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()

    def show_modes(self):
        def switch_mode(instance):
            self.player.developer_mode = not self.player.developer_mode
            mode = 'Developer' if self.player.developer_mode else 'Crafter'
            self.update_output(f"Switched to {mode} Mode.")
            self.current_popup.dismiss()

        def save_game(instance):
            success = save_game_state(self.player)
            if success:
                self.update_output("Game saved successfully.")
            else:
                self.update_output("Failed to save game.")
            self.current_popup.dismiss()

        def load_game(instance):
            player = load_game_state()
            if player:
                self.player = player
                self.update_output("Game loaded successfully.")
            else:
                self.update_output("Failed to load game.")
            self.current_popup.dismiss()

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        mode = 'Developer' if self.player.developer_mode else 'Crafter'
        content.add_widget(Label(text=f"Current Mode: {mode}"))
        switch_button = Button(text='Switch Mode', size_hint_y=None, height='40dp')
        switch_button.bind(on_press=switch_mode)
        save_button = Button(text='Save Game', size_hint_y=None, height='40dp')
        save_button.bind(on_press=save_game)
        load_button = Button(text='Load Game', size_hint_y=None, height='40dp')
        load_button.bind(on_press=load_game)
        close_button = Button(text='Close', size_hint_y=None, height='40dp')
        content.add_widget(switch_button)
        content.add_widget(save_button)
        content.add_widget(load_button)
        content.add_widget(close_button)
        popup = Popup(title='Modes', content=content, size_hint=(0.6, 0.6))
        close_button.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()

    def show_crafting(self):
        crafting_screen = self.screen_manager.get_screen('crafting')
        recipes_grid = crafting_screen.ids.recipes_grid
        recipes_grid.clear_widgets()
        for recipe in RECIPES.values():
            recipe_button = Button(
                text=recipe.name,
                size_hint_y=None,
                height='40dp',
                on_press=functools.partial(self.show_recipe_details, recipe)
            )
            recipes_grid.add_widget(recipe_button)
        self.screen_manager.current = 'crafting'

    def show_recipe_details(self, recipe, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"Recipe: {recipe.name}"))
        ingredients_text = "\n".join([f"{MATERIALS_LOOKUP[material_id].name} x{quantity}" for material_id, quantity in recipe.ingredients.items()])
        content.add_widget(Label(text=f"Ingredients:\n{ingredients_text}"))
        content.add_widget(Label(text=f"Produces: {recipe.output.name} x{recipe.output_quantity}"))
        craft_button = Button(text='Craft', size_hint_y=None, height='40dp')
        craft_button.bind(on_press=functools.partial(self.craft_recipe, recipe))
        content.add_widget(craft_button)
        close_button = Button(text='Close', size_hint_y=None, height='40dp')
        content.add_widget(close_button)
        popup = Popup(title='Recipe Details', content=content, size_hint=(0.6, 0.8))
        close_button.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()

    def craft_recipe(self, recipe, *args):
        success = self.player.craft_item(recipe.id)
        if success:
            self.update_output(f"Crafted {recipe.output_quantity} x {recipe.output.name}")
        else:
            self.update_output(f"Failed to craft {recipe.output.name}. Not enough materials.")
        self.current_popup.dismiss()

    def update_game_state(self, dt):
        self.player.update_machines()
        # Update the power level display
        if self.screen_manager.current == 'machines':
            machines_screen = self.screen_manager.get_screen('machines')
            # Update the power level label
            for child in machines_screen.children[0].children:
                if isinstance(child, Label):
                    child.text = 'Power Level: ' + self.get_power_level()
                    break

    def save_game(self):
        success = save_game_state(self.player)
        if success:
            self.update_output("Game saved successfully.")
        else:
            self.update_output("Failed to save game.")

    def load_game(self):
        player = load_game_state()
        if player:
            self.player = player
            self.update_output("Game loaded successfully.")
        else:
            self.update_output("Failed to load game.")

    def exit_game(self):
        self.stop()

if __name__ == '__main__':
    CradiumApp().run()
