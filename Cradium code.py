#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# ------------------------------
# Game Object Classes
# ------------------------------

class Item:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.name}: {self.description}"

class Machine:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.name}: {self.description}"

class Recipe:
    def __init__(self, name, output, inputs, machine_required=None, process_type="craft"):
        """
        output: tuple (item_name, quantity)
        inputs: dict {item_name: quantity}
        """
        self.name = name
        self.output = output      # e.g. ("IronIngot", 1)
        self.inputs = inputs      # e.g. {"IronOre": 2, "Coal": 1}
        self.machine_required = machine_required
        self.process_type = process_type

    def __str__(self):
        input_parts = [f"{itm} x{qty}" for itm, qty in self.inputs.items()]
        machine_part = f" | Machine: {self.machine_required}" if self.machine_required else ""
        return (f"{self.name}: {', '.join(input_parts)} => "
                f"{self.output[0]} x{self.output[1]} [Type: {self.process_type}{machine_part}]")


# ------------------------------
# Game Logic Class
# ------------------------------

class CradiumGame:
    def __init__(self):
        self.items = {}      # Defined items: name -> Item
        self.machines = {}   # Defined machines: name -> Machine
        self.recipes = {}    # Defined recipes: name -> Recipe
        self.inventory = {}  # Player's inventory: item_name -> quantity
        self.developer_mode = False

    def add_item(self, name, description=""):
        if name in self.items:
            return f"Item '{name}' already exists."
        self.items[name] = Item(name, description)
        return f"Added item: {name}"

    def add_machine(self, name, description=""):
        if name in self.machines:
            return f"Machine '{name}' already exists."
        self.machines[name] = Machine(name, description)
        return f"Added machine: {name}"

    def add_recipe(self, name, output, inputs, machine_required=None, process_type="craft"):
        if name in self.recipes:
            return f"Recipe '{name}' already exists."
        # Validate output item exists
        output_item, output_qty = output
        if output_item not in self.items:
            return f"Output item '{output_item}' is not defined. Please add it first."
        # Validate all input items exist
        for in_item in inputs:
            if in_item not in self.items:
                return f"Input item '{in_item}' is not defined. Please add it first."
        # Validate machine requirement if given
        if machine_required and machine_required not in self.machines:
            return f"Machine '{machine_required}' is not defined. Please add it first."
        self.recipes[name] = Recipe(name, output, inputs, machine_required, process_type)
        return f"Added recipe: {name}"

    def add_to_inventory(self, item_name, quantity):
        if item_name not in self.items:
            return f"Item '{item_name}' is not defined. Please add it first."
        self.inventory[item_name] = self.inventory.get(item_name, 0) + quantity
        return f"Added {quantity} of '{item_name}' to inventory."

    def craft(self, recipe_name):
        if recipe_name not in self.recipes:
            return f"Recipe '{recipe_name}' does not exist."
        recipe = self.recipes[recipe_name]

        # Check for machine if required (assuming crafted machines are stored in inventory)
        if recipe.machine_required:
            if self.inventory.get(recipe.machine_required, 0) < 1:
                return f"Crafting requires machine '{recipe.machine_required}' which is not available in inventory."

        # Check that all required inputs are available
        for input_item, required_qty in recipe.inputs.items():
            available = self.inventory.get(input_item, 0)
            if available < required_qty:
                return f"Not enough '{input_item}'. Required: {required_qty}, available: {available}"

        # Deduct the input items
        for input_item, required_qty in recipe.inputs.items():
            self.inventory[input_item] -= required_qty

        # Add the output item
        output_item, output_qty = recipe.output
        self.inventory[output_item] = self.inventory.get(output_item, 0) + output_qty
        return f"Crafted {output_item} x{output_qty} using recipe '{recipe_name}'."

    def list_items(self):
        if not self.items:
            return "No items defined."
        return "\n".join(str(item) for item in self.items.values())

    def list_machines(self):
        if not self.machines:
            return "No machines defined."
        return "\n".join(str(machine) for machine in self.machines.values())

    def list_recipes(self):
        if not self.recipes:
            return "No recipes defined."
        return "\n".join(str(recipe) for recipe in self.recipes.values())

    def get_inventory(self):
        if not self.inventory:
            return "Inventory is empty."
        return "\n".join(f"{item}: {qty}" for item, qty in self.inventory.items())


# ------------------------------
# GUI Application Class
# ------------------------------

class CradiumGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cradium - Sandbox Crafting Game")
        self.game = CradiumGame()
        
        # Create main frames and menu
        self.create_menu()
        self.create_main_frames()
        self.create_developer_tab()
        self.create_game_tab()
        self.create_inventory_area()
        self.create_log_area()
        
        self.update_inventory_list()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        dev_menu = tk.Menu(menubar, tearoff=0)
        self.developer_mode_var = tk.BooleanVar(value=self.game.developer_mode)
        dev_menu.add_checkbutton(label="Developer Mode",
                                 variable=self.developer_mode_var,
                                 onvalue=True,
                                 offvalue=False,
                                 command=self.toggle_developer_mode)
        menubar.add_cascade(label="Options", menu=dev_menu)
        self.root.config(menu=menubar)
    
    def create_main_frames(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Notebook for tabs on the right
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(side="right", fill="both", expand=True)
        
        # Left frame for inventory and log messages
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side="left", fill="y", padx=(0, 10))
    
    def create_inventory_area(self):
        inv_label = ttk.Label(self.left_frame, text="Inventory")
        inv_label.pack(pady=5)
        self.inventory_listbox = tk.Listbox(self.left_frame, width=30, height=15)
        self.inventory_listbox.pack(pady=5)
        refresh_button = ttk.Button(self.left_frame, text="Refresh Inventory", command=self.update_inventory_list)
        refresh_button.pack(pady=5)
    
    def create_log_area(self):
        log_label = ttk.Label(self.left_frame, text="Log")
        log_label.pack(pady=5)
        self.log_text = scrolledtext.ScrolledText(self.left_frame, width=30, height=10, state="disabled")
        self.log_text.pack(pady=5)
    
    def create_developer_tab(self):
        self.developer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.developer_frame, text="Developer Tools")
        
        # --- Add Item Section ---
        add_item_frame = ttk.LabelFrame(self.developer_frame, text="Add Item")
        add_item_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(add_item_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.item_name_entry = ttk.Entry(add_item_frame)
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(add_item_frame, text="Description:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.item_desc_entry = ttk.Entry(add_item_frame)
        self.item_desc_entry.grid(row=1, column=1, padx=5, pady=2)
        add_item_button = ttk.Button(add_item_frame, text="Add Item", command=self.add_item)
        add_item_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # --- Add Machine Section ---
        add_machine_frame = ttk.LabelFrame(self.developer_frame, text="Add Machine")
        add_machine_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(add_machine_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.machine_name_entry = ttk.Entry(add_machine_frame)
        self.machine_name_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(add_machine_frame, text="Description:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.machine_desc_entry = ttk.Entry(add_machine_frame)
        self.machine_desc_entry.grid(row=1, column=1, padx=5, pady=2)
        add_machine_button = ttk.Button(add_machine_frame, text="Add Machine", command=self.add_machine)
        add_machine_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # --- Add Recipe Section ---
        add_recipe_frame = ttk.LabelFrame(self.developer_frame, text="Add Recipe")
        add_recipe_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(add_recipe_frame, text="Recipe Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.recipe_name_entry = ttk.Entry(add_recipe_frame)
        self.recipe_name_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(add_recipe_frame, text="Output (item:qty):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.recipe_output_entry = ttk.Entry(add_recipe_frame)
        self.recipe_output_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(add_recipe_frame, text="Inputs (item:qty, ...):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.recipe_inputs_entry = ttk.Entry(add_recipe_frame)
        self.recipe_inputs_entry.grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(add_recipe_frame, text="Machine (optional):").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.recipe_machine_entry = ttk.Entry(add_recipe_frame)
        self.recipe_machine_entry.grid(row=3, column=1, padx=5, pady=2)
        ttk.Label(add_recipe_frame, text="Process Type:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.recipe_process_entry = ttk.Entry(add_recipe_frame)
        self.recipe_process_entry.insert(0, "craft")
        self.recipe_process_entry.grid(row=4, column=1, padx=5, pady=2)
        add_recipe_button = ttk.Button(add_recipe_frame, text="Add Recipe", command=self.add_recipe)
        add_recipe_button.grid(row=5, column=0, columnspan=2, pady=5)
    
    def create_game_tab(self):
        self.game_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.game_frame, text="Game Actions")
        
        # --- Craft Section ---
        craft_frame = ttk.LabelFrame(self.game_frame, text="Craft")
        craft_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(craft_frame, text="Recipe Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.craft_recipe_entry = ttk.Entry(craft_frame)
        self.craft_recipe_entry.grid(row=0, column=1, padx=5, pady=2)
        craft_button = ttk.Button(craft_frame, text="Craft", command=self.craft)
        craft_button.grid(row=1, column=0, columnspan=2, pady=5)
        
        # --- Add Inventory Section (for testing) ---
        inventory_frame = ttk.LabelFrame(self.game_frame, text="Add Inventory (for testing)")
        inventory_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(inventory_frame, text="Item Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.inv_item_entry = ttk.Entry(inventory_frame)
        self.inv_item_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(inventory_frame, text="Quantity:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.inv_qty_entry = ttk.Entry(inventory_frame)
        self.inv_qty_entry.grid(row=1, column=1, padx=5, pady=2)
        add_inv_button = ttk.Button(inventory_frame, text="Add to Inventory", command=self.add_inventory)
        add_inv_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # --- List Definitions Section ---
        list_frame = ttk.LabelFrame(self.game_frame, text="List Definitions")
        list_frame.pack(fill="x", padx=10, pady=5)
        list_items_button = ttk.Button(list_frame, text="List Items", command=self.list_items)
        list_items_button.grid(row=0, column=0, padx=5, pady=2)
        list_machines_button = ttk.Button(list_frame, text="List Machines", command=self.list_machines)
        list_machines_button.grid(row=0, column=1, padx=5, pady=2)
        list_recipes_button = ttk.Button(list_frame, text="List Recipes", command=self.list_recipes)
        list_recipes_button.grid(row=0, column=2, padx=5, pady=2)
    
    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def update_inventory_list(self):
        self.inventory_listbox.delete(0, tk.END)
        for item, qty in self.game.inventory.items():
            self.inventory_listbox.insert(tk.END, f"{item}: {qty}")
    
    def toggle_developer_mode(self):
        self.game.developer_mode = self.developer_mode_var.get()
        # Show or hide the Developer Tools tab accordingly
        if self.game.developer_mode:
            self.notebook.tab(0, state="normal")
            self.log_message("Developer mode enabled.")
        else:
            self.notebook.tab(0, state="hidden")
            self.log_message("Developer mode disabled.")
    
    def add_item(self):
        if not self.game.developer_mode:
            messagebox.showerror("Error", "Developer mode is disabled.")
            return
        name = self.item_name_entry.get().strip()
        desc = self.item_desc_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Item name is required.")
            return
        result = self.game.add_item(name, desc)
        self.log_message(result)
    
    def add_machine(self):
        if not self.game.developer_mode:
            messagebox.showerror("Error", "Developer mode is disabled.")
            return
        name = self.machine_name_entry.get().strip()
        desc = self.machine_desc_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Machine name is required.")
            return
        result = self.game.add_machine(name, desc)
        self.log_message(result)
    
    def add_recipe(self):
        if not self.game.developer_mode:
            messagebox.showerror("Error", "Developer mode is disabled.")
            return
        name = self.recipe_name_entry.get().strip()
        output_str = self.recipe_output_entry.get().strip()
        inputs_str = self.recipe_inputs_entry.get().strip()
        machine_req = self.recipe_machine_entry.get().strip()
        process_type = self.recipe_process_entry.get().strip()
        if not name or not output_str or not inputs_str:
            messagebox.showerror("Error", "Recipe name, output, and inputs are required.")
            return
        # Parse output (format "item:qty" or just "item" for qty=1)
        if ":" in output_str:
            out_item, out_qty = output_str.split(":", 1)
            try:
                out_qty = int(out_qty)
            except ValueError:
                messagebox.showerror("Error", "Invalid output quantity.")
                return
        else:
            out_item = output_str
            out_qty = 1
        # Parse inputs (format "item:qty, item:qty, ...")
        inputs = {}
        try:
            for pair in inputs_str.split(","):
                pair = pair.strip()
                if not pair:
                    continue
                if ":" in pair:
                    item_name, qty_str = pair.split(":", 1)
                    inputs[item_name.strip()] = int(qty_str.strip())
                else:
                    inputs[pair] = 1
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing inputs: {e}")
            return
        if machine_req == "":
            machine_req = None
        result = self.game.add_recipe(name, (out_item, out_qty), inputs, machine_req, process_type)
        self.log_message(result)
    
    def craft(self):
        recipe_name = self.craft_recipe_entry.get().strip()
        if not recipe_name:
            messagebox.showerror("Error", "Recipe name is required.")
            return
        result = self.game.craft(recipe_name)
        self.log_message(result)
        self.update_inventory_list()
    
    def add_inventory(self):
        item_name = self.inv_item_entry.get().strip()
        try:
            qty = int(self.inv_qty_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer.")
            return
        if not item_name:
            messagebox.showerror("Error", "Item name is required.")
            return
        result = self.game.add_to_inventory(item_name, qty)
        self.log_message(result)
        self.update_inventory_list()
    
    def list_items(self):
        result = self.game.list_items()
        self.log_message("Items:\n" + result)
    
    def list_machines(self):
        result = self.game.list_machines()
        self.log_message("Machines:\n" + result)
    
    def list_recipes(self):
        result = self.game.list_recipes()
        self.log_message("Recipes:\n" + result)

# ------------------------------
# Main Application Entry Point
# ------------------------------

def main():
    root = tk.Tk()
    app = CradiumGUI(root)
    # Hide the Developer Tools tab if developer mode is initially disabled
    if not app.game.developer_mode:
        app.notebook.tab(0, state="hidden")
    root.mainloop()

if __name__ == "__main__":
    main()
