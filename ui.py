import tkinter as tk
from tkinter import ttk, PhotoImage
from recipe import PizzaRecipe
from manager import RecipeManager
from config import Configuration


def load_recipe(root):
    build_ui(root, pizza_recipe=RecipeManager.load_recipe())


def clear_ui(root):
    for widget in root.winfo_children():
        widget.destroy()  # Destroy existing widgets


def build_ui(root, pizza_recipe=None):
    clear_ui(root)
    pzr = PizzaRecipe() if pizza_recipe is None else pizza_recipe
    formatted_temp = [round(value, 1) for value in pzr.get_temp_range()]  # For display in dropdown

    root.title("Pizza Recipe")
    root.geometry("440x345")

    num_balls = tk.IntVar(value=pzr.num_balls)
    ball_weight = tk.IntVar(value=pzr.ball_weight)

    hydration = tk.IntVar(value=pzr.hydration)

    yeast_type = tk.StringVar(value=pzr.yeast_type)

    oil = tk.IntVar(value=pzr.oil)
    salt = tk.IntVar(value=pzr.salt)

    # Actual temperature variables
    cold_proof_temp = tk.DoubleVar(value=round(pzr.fridge_temp, 1))
    cold_proof_hours = tk.IntVar(value=int(pzr.fridge_fermentation))
    room_proof_temp = tk.DoubleVar(value=round(pzr.room_temp, 1))
    room_proof_hours = tk.IntVar(value=int(pzr.room_fermentation))

    def get_time_options(temp):
        return [str(int(value)) for value in sorted(set(pzr.get_hour_range_by_temp(temp)))]

    def bind_spinbox(spinbox, field_name, variable):
        def on_change():
            root.after_idle(lambda: general_update(field_name, variable))

        spinbox.bind('<KeyRelease>', lambda _: on_change())
        spinbox.bind('<ButtonRelease>', lambda _: on_change())

    def update_output():
        output_text_widget.config(state='normal')
        output_text_widget.delete(1.0, tk.END)
        output_text_widget.insert(tk.END, pzr.to_string())
        output_text_widget.config(state='disabled')

    def update_cold_temp():
        pzr.fridge_temp = min(pzr.get_temp_range(), key=lambda x: abs(x - cold_proof_temp.get()))
        # cold_proof_hours_entry['values'] = pzr.get_hour_range_by_temp(pzr.fridge_temp)
        cold_proof_hours_entry['values'] = get_time_options(pzr.fridge_temp)

        update_output()

    def update_room_temp():
        pzr.room_temp = min(pzr.get_temp_range(), key=lambda x: abs(x - room_proof_temp.get()))
        # room_proof_hours_entry['values'] = pzr.get_hour_range_by_temp(pzr.room_temp)
        room_proof_hours_entry['values'] = get_time_options(pzr.room_temp)
        update_output()

    def general_update(attribute, value):
        setattr(pzr, attribute, value.get())
        update_output()

    def save_recipe():
        RecipeManager.save_recipe(pzr)

    tk.Label(root, text="Main Recipe Inputs", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=4,
                                                                                   sticky='W', padx=(20, 0))

    tk.Label(root, text="Number of Balls").grid(row=1, column=0, sticky='W', padx=(20, 0))
    balls_dropdown = ttk.Combobox(root, textvariable=num_balls, values=list(range(1, 11)), state="readonly", width=10)
    balls_dropdown.grid(row=1, column=1)
    balls_dropdown.bind('<<ComboboxSelected>>', lambda _: general_update('num_balls', num_balls))

    tk.Label(root, text="Ball Weight (g)").grid(row=1, column=2, sticky='W', padx=(5, 0))
    ball_weight_entry = tk.Entry(root, textvariable=ball_weight, width=12)
    ball_weight_entry.grid(row=1, column=3)
    ball_weight_entry.bind('<KeyRelease>', lambda _: general_update('ball_weight', ball_weight))

    # Yeast type dropdown
    tk.Label(root, text="Yeast Type").grid(row=2, column=0, sticky='W', padx=(20, 0))
    yeast_dropdown = ttk.Combobox(root, textvariable=yeast_type, values=pzr.get_yeast_types(), state="readonly",
                                  width=10)
    yeast_dropdown.grid(row=2, column=1)
    yeast_dropdown.bind('<<ComboboxSelected>>', lambda _: general_update('yeast_type', yeast_type))

    # Hydration, salt and oil percentage
    tk.Label(root, text="Hydration (%)").grid(row=2, column=2, sticky='W', padx=(5, 0))
    hydration_spinpox = tk.Spinbox(root, from_=0, to=100, textvariable=hydration, width=10)
    hydration_spinpox.grid(row=2, column=3)
    bind_spinbox(hydration_spinpox, 'hydration', hydration)

    tk.Label(root, text="Salt (%)").grid(row=3, column=2, sticky='W', padx=(5, 0))
    salt_percentage_spinbox = tk.Spinbox(root, from_=0, to=100, textvariable=salt, width=10)
    salt_percentage_spinbox.grid(row=3, column=3)
    bind_spinbox(salt_percentage_spinbox, 'salt', salt)

    tk.Label(root, text="Oil (%)").grid(row=3, column=0, sticky='W', padx=(20, 0))
    oil_percentage_spinbox = tk.Spinbox(root, from_=0, to=100, textvariable=oil, width=11)
    oil_percentage_spinbox.grid(row=3, column=1)
    bind_spinbox(oil_percentage_spinbox, 'oil', oil)

    # Section 2: Proofing Details
    tk.Label(root, text="Proofing Details", font=("Helvetica", 16, "bold")).grid(row=5, column=0, columnspan=4,
                                                                                 sticky='W', padx=(20, 0))

    # Cold proof temp and hours
    tk.Label(root, text="Cold Proof Temp (°C)").grid(row=6, column=0, sticky='W', padx=(20, 0))
    cold_proof_temp_entry = ttk.Combobox(root, textvariable=cold_proof_temp, values=formatted_temp, state="readonly",
                                         width=11)
    cold_proof_temp_entry.grid(row=6, column=1)
    cold_proof_temp_entry.bind('<<ComboboxSelected>>', lambda _: update_cold_temp())

    tk.Label(root, text="Cold Proof Hours").grid(row=6, column=2, sticky='W', padx=(5, 0))
    # cold_proof_hours_entry = ttk.Combobox(root, textvariable=cold_proof_hours,
    #                                       values=pzr.get_hour_range_by_temp(pzr.fridge_temp), state="readonly",
    #                                       width=11)
    cold_proof_hours_entry = ttk.Combobox(root, textvariable=cold_proof_hours,
                                          values=get_time_options(pzr.fridge_temp),
                                          state="readonly", width=11)
    cold_proof_hours_entry.grid(row=6, column=3)
    cold_proof_hours_entry.bind('<<ComboboxSelected>>',
                                lambda _: general_update('fridge_fermentation', cold_proof_hours))

    # Room proof temp and hours
    tk.Label(root, text="Room Proof Temp (°C)").grid(row=7, column=0, sticky='W', padx=(20, 0))
    room_proof_temp_entry = ttk.Combobox(root, textvariable=room_proof_temp, values=formatted_temp, state="readonly",
                                         width=11)
    room_proof_temp_entry.grid(row=7, column=1)
    room_proof_temp_entry.bind('<<ComboboxSelected>>', lambda _: update_room_temp())

    tk.Label(root, text="Room Proof Hours").grid(row=7, column=2, sticky='W', padx=(5, 0))
    # room_proof_hours_entry = ttk.Combobox(root, textvariable=room_proof_hours, values=pzr.get_hour_range_by_temp(
    # pzr.room_temp), state="readonly", width=11)
    room_proof_hours_entry = ttk.Combobox(root, textvariable=room_proof_hours,
                                          values=get_time_options(pzr.room_temp), state="readonly", width=11)
    room_proof_hours_entry.grid(row=7, column=3)
    room_proof_hours_entry.bind('<<ComboboxSelected>>',
                                lambda _: general_update('room_fermentation', room_proof_hours))

    # Section 3: Output Instructions
    tk.Label(root, text="Ingredients and Proofing Instructions", font=("Helvetica", 16, "bold")).grid(row=8, column=0,
                                                                                                      columnspan=4,
                                                                                                      sticky='W',
                                                                                                      padx=(20, 0))

    output_text_widget = tk.Text(root, height=8, width=50, state='disabled')
    output_text_widget.grid(row=9, column=0, columnspan=4, pady=(0, 20), padx=(20, 0))
    output_text_widget.config(state='normal')
    output_text_widget.delete(1.0, tk.END)
    output_text_widget.insert(tk.END, pzr.to_string())
    output_text_widget.config(state='disabled')

    save_icon = PhotoImage(file=Configuration.get_save_icon_path())
    save_button = tk.Button(root, image=save_icon, command=save_recipe, bd=1)
    save_button.place(x=415, y=10)
    save_button.image = save_icon

    load_icon = PhotoImage(file=Configuration.get_load_icon_path())
    load_button = tk.Button(root, image=load_icon, command=lambda: load_recipe(root), bd=1)
    load_button.place(x=395, y=10)
    load_button.image = load_icon

    return root
