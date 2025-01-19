import tkinter as tk
import random
import pickle


class Pet:
    def __init__(self, name, pet_type="Dog"):
        self.name = name
        self.pet_type = pet_type
        self.hunger = 50  # Hunger level (0-100)
        self.happiness = 50  # Happiness level (0-100)
        self.health = 100  # Health level (0-100)
        self.cleanliness = 100  # Cleanliness (0-100)
        self.boredom = 50  # Boredom level (0-100)
        self.energy = 100  # Energy (0-100)
        self.age = 1  # Age of the pet
        self.coins = 0  # Player's coins
        self.alive = True  # Pet's life status
        self.achievements = []  # List of achievements
        self.sick = False  # Track if the pet is sick
        self.level = 1  # Pet's level (based on age)

    def earn_coins(self, amount):
        """Increase the coin balance."""
        self.coins += amount

    def spend_coins(self, amount):
        """Spend coins to unlock features or purchase items."""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def feed(self):
        """Feed the pet to reduce hunger."""
        if self.hunger > 0:
            self.hunger -= 20  # Reduce hunger when fed
            self.earn_coins(5)  # Reward for feeding pet
        if self.hunger < 0:
            self.hunger = 0  # Ensure hunger does not go below 0

    def play(self):
        """Play with the pet to increase happiness and reduce boredom."""
        if self.boredom > 0:
            self.happiness = min(100, self.happiness + 20)  # Increase happiness
            self.boredom = max(0, self.boredom - 20)  # Decrease boredom
            self.energy -= 10  # Reduce energy after playing
            self.earn_coins(10)  # Reward for playing with pet

    def clean(self):
        """Clean the pet to restore cleanliness."""
        if self.cleanliness < 100:
            self.cleanliness = 100  # Cleanliness is restored to 100
            self.earn_coins(3)  # Reward for cleaning pet

    def sleep(self):
        """Put the pet to sleep to restore energy."""
        self.energy = 100  # Restores energy when the pet sleeps
        self.health = min(100, self.health + 5)  # Health improves slightly when sleeping
        self.earn_coins(2)  # Reward for letting the pet sleep

    def check_stats(self):
        """Return the current stats of the pet."""
        return {
            "Hunger": self.hunger,
            "Happiness": self.happiness,
            "Health": self.health,
            "Cleanliness": self.cleanliness,
            "Boredom": self.boredom,
            "Energy": self.energy,
            "Coins": self.coins
        }

    def decrease_stats(self):
        """Simulate the passage of time and adjust stats"""
        # Hunger and Boredom increase over time
        self.hunger += 5
        self.boredom += 5
        self.cleanliness -= 5
        self.energy -= 10
        if self.hunger > 100:
            self.hunger = 100
        if self.boredom > 100:
            self.boredom = 100
        if self.cleanliness < 0:
            self.cleanliness = 0
        if self.energy < 0:
            self.energy = 0

        # If hunger and boredom are too high, health decreases
        if self.hunger > 80:
            self.health -= 5
        if self.boredom > 80:
            self.health -= 5
        if self.cleanliness < 20:
            self.health -= 10

        self.age += 1  # Increase the pet's age over time
        self.level = self.age  # Level is based on pet's age

        # Unlock achievements based on age
        if self.age == 5:
            self.achievements.append("Achieved: 5 Years Old!")
        if self.age == 10:
            self.achievements.append("Achieved: 10 Years Old!")
        if self.age == 15:
            self.achievements.append("Achieved: 15 Years Old!")

    def random_event(self):
        """Random events affecting the pet's stats."""
        event_chance = random.randint(1, 100)
        if event_chance <= 10:  # 10% chance for a random event
            event = random.choice(["Pet found a toy!", "Pet got sick!", "Pet feels lonely!"])
            if event == "Pet got sick!" and not self.sick:
                self.sick = True  # Pet gets sick
                self.health = max(0, self.health - 10)  # Health decreases when sick
            elif event == "Pet feels lonely!":
                self.happiness = max(0, self.happiness - 10)
            else:
                self.happiness = min(100, self.happiness + 10)

    def heal(self):
        """Heal the pet when a health potion is used"""
        if self.sick:
            self.health = min(100, self.health + 50)  # Health potion restores 50 health
            self.sick = False  # Pet is no longer sick

    def is_alive(self):
        """Check if the pet is still alive."""
        return self.health > 0  # Pet is alive if health is above 0

    def save(self):
        """Save the pet's data to a file."""
        with open(f"{self.name}_pet_data.pkl", "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load(name):
        """Load a pet's data from a file."""
        try:
            with open(f"{name}_pet_data.pkl", "rb") as file:
                pet = pickle.load(file)
                return pet
        except FileNotFoundError:
            return None


class PetGUI:
    def __init__(self, root, pet_name="Buddy"):
        self.root = root
        self.root.title("Virtual Pet Game")
        self.pet = Pet(pet_name)
        self.pet_name = pet_name

        # Set up the main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=10, pady=10)

        # Stats display
        self.stats_label = tk.Label(self.main_frame, text="", font=("Arial", 14), justify="left")
        self.stats_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Pet Name Display
        self.pet_name_label = tk.Label(self.main_frame, text=f"Pet Name: {self.pet_name}", font=("Arial", 14))
        self.pet_name_label.grid(row=1, column=0, columnspan=3, pady=5)

        # Action buttons
        self.feed_button = tk.Button(self.main_frame, text="Feed Pet", command=self.feed_pet)
        self.feed_button.grid(row=2, column=0, padx=10, pady=5)

        self.play_button = tk.Button(self.main_frame, text="Play with Pet", command=self.play_pet)
        self.play_button.grid(row=2, column=1, padx=10, pady=5)

        self.clean_button = tk.Button(self.main_frame, text="Clean Pet", command=self.clean_pet)
        self.clean_button.grid(row=2, column=2, padx=10, pady=5)

        self.sleep_button = tk.Button(self.main_frame, text="Put Pet to Sleep", command=self.sleep_pet)
        self.sleep_button.grid(row=3, column=0, padx=10, pady=5)

        self.check_stats_button = tk.Button(self.main_frame, text="Check Stats", command=self.check_stats)
        self.check_stats_button.grid(row=3, column=1, padx=10, pady=5)

        self.save_button = tk.Button(self.main_frame, text="Save Progress", command=self.save_progress)
        self.save_button.grid(row=4, column=0, padx=10, pady=5)

        self.quit_button = tk.Button(self.main_frame, text="Quit", command=self.quit_game)
        self.quit_button.grid(row=4, column=1, columnspan=2, pady=20)

        self.update_stats()

    def feed_pet(self):
        """Handle the feed action."""
        self.pet.feed()  # Feed the pet
        self.pet.decrease_stats()  # Decrease stats based on time
        self.pet.random_event()  # Trigger random events
        self.update_stats()  # Update stats on GUI

    def play_pet(self):
        """Handle the play action."""
        self.pet.play()
        self.pet.decrease_stats()
        self.pet.random_event()
        self.update_stats()

    def clean_pet(self):
        """Handle the clean action."""
        self.pet.clean()
        self.pet.decrease_stats()
        self.pet.random_event()
        self.update_stats()

    def sleep_pet(self):
        """Handle the sleep action."""
        self.pet.sleep()
        self.pet.decrease_stats()
        self.pet.random_event()
        self.update_stats()

    def check_stats(self):
        """Display the pet stats."""
        stats = self.pet.check_stats()
        stats_text = "\n".join([f"{key}: {value}/100" for key, value in stats.items()])
        if self.pet.health <= 0:
            self.stats_label.config(fg="red", text="Oh no! Your pet has passed away...")
        else:
            self.stats_label.config(fg="black", text=stats_text + "\nAchievements: " + "\n".join(self.pet.achievements))

    def update_stats(self):
        """Refresh the stats on the GUI."""
        stats = self.pet.check_stats()
        stats_text = "\n".join([f"{key}: {value}/100" for key, value in stats.items()])
        self.stats_label.config(text=f"Pet Name: {self.pet.name}\n{stats_text}")

    def save_progress(self):
        """Save the pet's progress to a file."""
        self.pet.save()
        self.stats_label.config(text="Progress saved successfully!")

    def quit_game(self):
        """Exit the game."""
        self.root.quit()


# Run the game with pet name input prompt
def start_game():
    def on_submit():
        pet_name = pet_name_entry.get()
        if pet_name:
            root = tk.Tk()
            game_gui = PetGUI(root, pet_name)
            root.mainloop()
        else:
            error_label.config(text="Please enter a pet name!")

    start_window = tk.Tk()
    start_window.title("Enter Pet Name")

    prompt_label = tk.Label(start_window, text="Enter your pet's name:", font=("Arial", 14))
    prompt_label.pack(padx=10, pady=10)

    pet_name_entry = tk.Entry(start_window, font=("Arial", 14))
    pet_name_entry.pack(padx=10, pady=10)

    submit_button = tk.Button(start_window, text="Start Game", command=on_submit)
    submit_button.pack(padx=10, pady=10)

    error_label = tk.Label(start_window, text="", fg="red", font=("Arial", 12))
    error_label.pack(padx=10, pady=10)

    start_window.mainloop()


start_game()
