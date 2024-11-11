# recipe.py

from config import Configuration
import math


class PizzaRecipe:
    """A class to manage pizza recipe calculations."""
    _recipe_defaults = None
    _xlsx_defaults = None
    _temperature_options = None
    _yeast_table_data = None

    def __init__(self, salt_percentage=None, oil_percentage=None, yeast_type=None,
                 hydration=None, ball_weight=None, num_balls=None, room_fer=None, fridge_fer=None):
        """Initialize the pizza recipe with given parameters or defaults."""
        if PizzaRecipe._recipe_defaults is None or PizzaRecipe._yeast_table_data is None \
                or PizzaRecipe._temperature_options is None or PizzaRecipe._xlsx_defaults is None:
            PizzaRecipe.initialize()

        self._salt = PizzaRecipe._recipe_defaults['salt_percentage'] if salt_percentage is None else salt_percentage
        self._oil = PizzaRecipe._recipe_defaults['oil_percentage'] if oil_percentage is None else oil_percentage
        self._hydration = PizzaRecipe._recipe_defaults['hydration'] if hydration is None else hydration
        self._ball_weight = PizzaRecipe._recipe_defaults['ball_weight'] if ball_weight is None else ball_weight
        self._num_balls = PizzaRecipe._recipe_defaults['num_balls'] if num_balls is None else num_balls

        self._flour = self._salt_weight = self._oil_weight = self._water = None
        self._yeast_percentage = self._yeast_weight = None

        self.recalculate()

        self._yeast_type = PizzaRecipe._recipe_defaults['yeast_types'][1] if yeast_type is None else yeast_type
        self._room_temp = self._temperature_options[self._xlsx_defaults['room_temperature_row']]
        self._fridge_temp = self._temperature_options[self._xlsx_defaults['fridge_temperature_row']]

        self._room_fermentation = self.get_hour_range_by_temp(self._room_temp)[
            PizzaRecipe._xlsx_defaults['room_time_default']] \
            if room_fer is None else room_fer
        self._fridge_fermentation = self.get_hour_range_by_temp(self._fridge_temp)[
            PizzaRecipe._xlsx_defaults['fridge_time_default']] \
            if fridge_fer is None else fridge_fer

        self.calculate_yeast_percentage_dual()

    def calculate_flour_weight(self):
        total_weight = 1 + (self._hydration + (0 if self._oil is None else self._oil) +
                            (0 if self._salt is None else self._salt)) / 100
        return (self._num_balls * self._ball_weight) / total_weight

    def calculate_water_weight(self):
        return (self._num_balls * self._ball_weight) - self._flour - \
               self._salt_weight - self.oil_weight

    def recalculate(self):
        self._flour = self.calculate_flour_weight()
        self._salt_weight = self.calculate_salt_weight()
        self._oil_weight = self.calculate_oil_weight()
        self._water = self.calculate_water_weight()

    def recalculate_yeast(self):
        f_tmp_time = min(PizzaRecipe.get_hour_range_by_temp(self.fridge_temp),
                         key=lambda x: abs(x - self.fridge_fermentation))
        r_tmp_time = min(PizzaRecipe.get_hour_range_by_temp(self.room_temp),
                         key=lambda x: abs(x - self.room_fermentation))
        if self._fridge_fermentation != f_tmp_time:
            self._fridge_fermentation = f_tmp_time
        if self._room_fermentation != r_tmp_time:
            self._room_fermentation = r_tmp_time
        self.calculate_yeast_percentage_dual()

    # Class Methods

    @classmethod
    def initialize(cls):
        cls._recipe_defaults = Configuration.get_recipe_defaults()
        cls._yeast_table_data = Configuration.get_yeast_table_data()
        cls._xlsx_defaults = Configuration.get_yeast_table_params()
        row_range_temp = slice(cls._xlsx_defaults['temp_row_range_l'], cls._xlsx_defaults['temp_row_range_r'])
        cls._temperature_options = cls._yeast_table_data.iloc[
            row_range_temp, cls._xlsx_defaults['temp_row_range_offset']].dropna().tolist()

    # Static Methods

    @staticmethod
    def get_temp_range():
        if PizzaRecipe._yeast_table_data is None:
            PizzaRecipe.initialize()
        return PizzaRecipe._temperature_options

    @staticmethod
    def get_hour_range_by_temp(temp):
        if PizzaRecipe._yeast_table_data is None:
            PizzaRecipe.initialize()
        try:
            row_index = PizzaRecipe._temperature_options.index(temp) + PizzaRecipe._xlsx_defaults['temp_row_range_l']
        except ValueError:
            print(f"{temp} is not in the list.")
            row_index = PizzaRecipe._xlsx_defaults['temp_row_range_l']

        s_index = PizzaRecipe._xlsx_defaults['start_hour_index']
        e_index = PizzaRecipe._xlsx_defaults['end_hour_index']
        return [
            value for value in PizzaRecipe._yeast_table_data.iloc[row_index, s_index:e_index].dropna().tolist()
            if value not in (None, 0)
        ]

    def calculate_yeast_percentage_dual(self):
        if PizzaRecipe._yeast_table_data is None:
            PizzaRecipe.initialize()

        try:
            row_room = PizzaRecipe._temperature_options.index(self._room_temp) + PizzaRecipe._xlsx_defaults[
                'temp_row_range_l']
            row_fridge = PizzaRecipe._temperature_options.index(self._fridge_temp) + PizzaRecipe._xlsx_defaults[
                'temp_row_range_l']
        except ValueError:
            raise ValueError(f"{self._room_temp} or {self._fridge_temp} is not in the list of temperature options.")

        yeast_data_row_room = PizzaRecipe._yeast_table_data.iloc[row_room]

        closest_diff = min(
            abs(yeast_data_row_room[col] - self._room_fermentation) for col in yeast_data_row_room.index)

        col_room = [col for col in yeast_data_row_room.index[2:] if
                    abs(yeast_data_row_room[col] - self._room_fermentation) == closest_diff][-1]

        yeast_data_row_fridge = PizzaRecipe._yeast_table_data.iloc[row_fridge]
        time_combined = yeast_data_row_fridge[col_room] + self._fridge_fermentation

        col_fridge = min(
            (col for col in yeast_data_row_fridge.index[2:] if not math.isnan(yeast_data_row_fridge[col])),
            key=lambda x: abs(yeast_data_row_fridge[x] - time_combined)
        )

        self._yeast_percentage = PizzaRecipe._yeast_table_data.iloc[
            PizzaRecipe._recipe_defaults['yeast_types'].index(self._yeast_type), col_fridge]

        self._yeast_weight = self.calculate_yeast_weight()

    def calculate_salt_weight(self):
        return 0 if self._salt is None else (self._flour * self._salt) / 100

    def calculate_oil_weight(self):
        return 0 if self._oil is None else (self._flour * self._oil) / 100

    def calculate_yeast_weight(self):
        return (self._flour * self._yeast_percentage) / 100

    # Getters and Setters

    @property
    def flour(self):
        return math.ceil(self._flour)

    @property
    def water(self):
        return math.ceil(self._water)

    @property
    def salt(self):
        return self._salt

    @salt.setter
    def salt(self, value):
        self._salt = value
        self.recalculate()
        self.recalculate_yeast()

    @property
    def salt_weight(self):
        return math.floor(self._salt_weight)

    @property
    def oil(self):
        return self._oil

    @oil.setter
    def oil(self, value):
        self._oil = value
        self.recalculate()
        self.recalculate_yeast()

    @property
    def oil_weight(self):
        return math.floor(self._oil_weight)

    @property
    def hydration(self):
        return self._hydration

    @hydration.setter
    def hydration(self, value):
        self._hydration = value
        self.recalculate()
        self.recalculate_yeast()

    @property
    def ball_weight(self):
        return self._ball_weight

    @ball_weight.setter
    def ball_weight(self, value):
        self._ball_weight = value
        self.recalculate()
        self.recalculate_yeast()

    @property
    def num_balls(self):
        return self._num_balls

    @num_balls.setter
    def num_balls(self, value):
        self._num_balls = value
        self.recalculate()
        self.recalculate_yeast()

    @property
    def yeast_type(self):
        return self._yeast_type

    @yeast_type.setter
    def yeast_type(self, value):
        self._yeast_type = value
        self.recalculate_yeast()

    @property
    def yeast_weight(self):
        return self._yeast_weight

    @property
    def room_temp(self):
        return self._room_temp

    @room_temp.setter
    def room_temp(self, value):
        self._room_temp = value
        self.recalculate_yeast()

    @property
    def fridge_temp(self):
        return self._fridge_temp

    @fridge_temp.setter
    def fridge_temp(self, value):
        self._fridge_temp = value
        self.recalculate_yeast()

    @property
    def room_fermentation(self):
        return self._room_fermentation

    @room_fermentation.setter
    def room_fermentation(self, value):
        self._room_fermentation = value
        self.recalculate_yeast()

    @property
    def fridge_fermentation(self):
        return self._fridge_fermentation

    @fridge_fermentation.setter
    def fridge_fermentation(self, value):
        self._fridge_fermentation = value
        self.recalculate_yeast()

    @staticmethod
    def get_yeast_types():
        return PizzaRecipe._recipe_defaults['yeast_types']

    def to_string(self):
        return (f"Flour: {self.flour}g\n"
                f"Water: {self.water}g\n"
                f"Salt: {self.salt_weight}g\n"
                f"Oil: {self.oil_weight}g\n"
                f"Yeast: {self.yeast_weight:.3f}g of {self.yeast_type}\n"
                f"Cold Proof: {round(self.fridge_fermentation)} hours at {self.fridge_temp:.1f}°C\n"
                f"Room Proof: {round(self.room_fermentation)} hours at {self.room_temp:.1f}°C\n"
                f"Total: {self.num_balls} dough balls, each weighing {self.ball_weight}g")
