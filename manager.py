# manager.py

import json
import os
from tkinter import filedialog, messagebox
from config import Configuration
from datetime import datetime
from recipe import PizzaRecipe


class RecipeManager:
    @staticmethod
    def save_recipe(recipe):
        folder_path = Configuration.get_recipe_folder_path()
        os.makedirs(folder_path, exist_ok=True)

        base_filename = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(folder_path, f"{base_filename}.json")

        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(folder_path, f"{base_filename}_{counter}.json")
            counter += 1

        data = {
            "salt_percentage": recipe.salt,
            "oil_percentage": recipe.oil,
            "yeast_type": recipe.yeast_type,
            "hydration": recipe.hydration,
            "ball_weight": recipe.ball_weight,
            "num_balls": recipe.num_balls,
            "room_fer": recipe.room_fermentation,
            "fridge_fer": recipe.fridge_fermentation,
        }

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_recipe():
        recipe_path = filedialog.askopenfilename(
            title="Select Recipe File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not recipe_path:
            messagebox.showinfo("No File Selected", "No file was selected.")
            return None

        try:
            with open(recipe_path, 'r') as file:
                data = json.load(file)
                return PizzaRecipe(data.get('salt_percentage'),
                                   data.get('oil_percentage'),
                                   data.get('yeast_type'),
                                   data.get('hydration'),
                                   data.get('ball_weight'),
                                   data.get('num_balls'),
                                   data.get('room_fer'),
                                   data.get('fridge_fer'))
        except Exception as e:
            messagebox.showerror("Error Loading Recipe", f"An error occurred: {e}")
            return None
