import random
import string
import time
import re
import tkinter as tk
from tkinter import scrolledtext, ttk
from threading import Thread

# --- Global Constants ---

# Theoretical cracking speeds based on hardware (Attempts/s)
ATTACK_SPEEDS = {
    "CPU (Default PC)": 500_000,      # 500K attempts/s
    "GPU (Gaming Card)": 10_000_000,    # 10M attempts/s
    "ASIC (Dedicated Hardware)": 1_000_000_000 # 1 Billion attempts/s
}

# --- Utility Functions ---


def format_time_duration(seconds):
    """Converts seconds into a human-readable duration (seconds, minutes, hours, days, years)."""
    if seconds is None or seconds == float('inf'):
        return "Decades (or more)"

    if seconds < 60:
        return f"{seconds:.4f} seconds"
    elif seconds < 3600:
        return f"{seconds / 60:.2f} minutes"
    elif seconds < 86400:
        return f"{seconds / 86400:.2f} days"
    elif seconds < 31536000:
        return f"{seconds / 31536000:.2f} years"
    else:
        return f"{seconds / 31536000:.2f} years"


def assess_password_strength(password):
    """Analyzes password complexity and returns 7 values."""
    score = 0
    feedback = []

    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^a-zA-Z0-9\s]", password))

    length = len(password)
    if length >= 12:
        score += 4
        feedback.append("Excellent length (12+ characters)")
    elif length >= 8:
        score += 2
        feedback.append("Good length (8-11 characters)")
    else:
        score += 1
        feedback.append("Short length (less than 8 characters)")

    if has_upper:
        score += 1
        feedback.append("Includes uppercase letters")
    if has_lower:
        score += 1
        feedback.append("Includes lowercase letters")
    if has_digit:
        score += 1
        feedback.append("Includes numbers")
    if has_special:
        score += 2
        feedback.append("Includes special characters")

    if score >= 8:
        strength_level = "Very Strong"
    elif score >= 5:
        strength_level = "Strong"
    elif score >= 3:
        strength_level = "Moderate"
    else:
        strength_level = "Weak"

    return strength_level, score, feedback, has_upper, has_lower, has_digit, has_special


# --- Main Application Class ---

class CrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Brute-Force Cracking Simulator (GUI) 🔒")
        master.geometry("1000x850")
        
        # NOTE: Adding an icon is complex without a file, 
        # so we'll skip the actual file loading but keep the intent for documentation.
        # master.iconbitmap('lock.ico') 
        # (This line is commented out as it requires an actual 'lock.ico' file)

        style = ttk.Style()
        style.theme_use('clam')

        # Define styles for the progress bar colors
        style.configure("Red.TProgressbar", foreground='red', background='red')
        style.configure("Yellow.TProgressbar",
                        foreground='yellow', background='yellow')
        style.configure("LightGreen.TProgressbar",
                        foreground='lightgreen', background='lightgreen')
        style.configure("Green.TProgressbar",
                        foreground='green', background='green')

        self.output_font = ('Consolas', 10)
        master.configure(bg='#F0F0F0')

        self.stop_requested = False
        self.show_password = True

        # Live dashboard variables
        self.time_var = tk.StringVar(value="N/A")
        self.speed_var = tk.StringVar(value="Speed: 0 attempts/s")
        self.attempts_var = tk.StringVar(value="Attempts: 0")
        self.worst_case_guesses_var = tk.StringVar(value="N/A")

        # Live strength meter variables
        self.strength_score_var = tk.IntVar(value=0)
        self.strength_text_var = tk.StringVar(value="Strength: N/A")

        # Attack control variables
        self.hardware_speed_var = tk.StringVar(
            value=list(ATTACK_SPEEDS.keys())[0])
        # NEW: Cracking Target variable (50% or 100%)
        self.crack_target_var = tk.StringVar(
            value="50% (Average Case)")


        # Character contribution variables
        self.len_var = tk.StringVar(value="Length: 0")
        self.lower_var = tk.StringVar(value="a-z: 0")
        self.upper_var = tk.StringVar(value="A-Z: 0")
        self.digit_var = tk.StringVar(value="0-9: 0")
        self.special_var = tk.StringVar(value="Symbols: 0")

        self.create_widgets()

    def create_widgets(self):
        # 1. Input and Control Frame
        input_frame = ttk.Frame(self.master, padding="10 10 10 10")
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Enter Password:").pack(
            side='left', padx=5)

        self.password_entry = ttk.Entry(input_frame, width=50)
        self.password_entry.pack(side='left', padx=5, expand=True, fill='x')
        self.password_entry.bind('<KeyRelease>', self.on_key_release)

        # Toggle Visibility Button
        self.toggle_button = ttk.Button(
            input_frame, text="👁️", command=self.toggle_password_visibility, width=4)
        self.toggle_button.pack(side='left', padx=(0, 10))

        self.crack_button = ttk.Button(
            input_frame, text="🚀 Start Attack", command=self.start_attack_thread)
        self.crack_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(
            input_frame, text="🛑 Stop Attack", command=self.stop_attack, state=tk.DISABLED)
        self.stop_button.pack(side='left', padx=5)
        
        # Recommendation Label
        ttk.Label(self.master, text="recommend don't add more than 4",
                  foreground='blue', font=('Helvetica', 9)).pack(padx=10, pady=(2, 2), anchor='w')

        # 1.5 Live Strength Meter Frame
        strength_frame = ttk.Frame(self.master, padding="10 5 10 5")
        strength_frame.pack(fill='x')

        ttk.Label(strength_frame, textvariable=self.strength_text_var,
                  font=('Helvetica', 10, 'bold')).pack(side='left', padx=10)
        self.strength_progress = ttk.Progressbar(
            strength_frame, orient='horizontal', length=200, mode='determinate', variable=self.strength_score_var)
        self.strength_progress.pack(
            side='left', padx=10, expand=True, fill='x')

        # 1.6 Character Contribution Analysis Frame
        contribution_frame = ttk.LabelFrame(
            self.master, text="Character Contribution Analysis (Keyspace Base)", padding="10")
        contribution_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(contribution_frame, textvariable=self.len_var).pack(
            side='left', padx=8)
        ttk.Separator(contribution_frame, orient=tk.VERTICAL).pack(
            side='left', padx=5, fill='y')
        ttk.Label(contribution_frame, textvariable=self.lower_var).pack(
            side='left', padx=8)
        ttk.Label(contribution_frame, textvariable=self.upper_var).pack(
            side='left', padx=8)
        ttk.Label(contribution_frame, textvariable=self.digit_var).pack(
            side='left', padx=8)
        ttk.Label(contribution_frame, textvariable=self.special_var).pack(
            side='left', padx=8)

        # 2. Attack Settings Frame
        settings_frame = ttk.LabelFrame(
            self.master, text="Attack Settings", padding="10")
        settings_frame.pack(fill='x', padx=10, pady=5)

        # Hardware Speed Combobox
        ttk.Label(settings_frame, text="Attacker Hardware Speed:").pack(
            side='left', padx=5)
        self.speed_combobox = ttk.Combobox(settings_frame, textvariable=self.hardware_speed_var, values=list(
            ATTACK_SPEEDS.keys()), state="readonly", width=20)
        self.speed_combobox.pack(side='left', padx=5)
        
        # NEW: Cracking Target Combobox
        ttk.Label(settings_frame, text=" | Prediction Target:").pack(
            side='left', padx=(20, 5))
        self.target_combobox = ttk.Combobox(settings_frame, textvariable=self.crack_target_var, values=[
            "50% (Average Case)", "100% (Worst Case)"
        ], state="readonly", width=20)
        self.target_combobox.pack(side='left', padx=5)


        # 3. Strength Dashboard Frame
        dashboard_frame = ttk.Frame(self.master, padding="10 0 10 10")
        dashboard_frame.pack(fill='x')

        # Predicted Cracking Time
        ttk.Label(dashboard_frame, text="Predicted Cracking Time:",
                  font=('Helvetica', 10, 'bold')).pack(side='left', padx=10)
        ttk.Label(dashboard_frame, textvariable=self.time_var, font=(
            'Consolas', 12, 'bold'), foreground='#CC0000').pack(side='left', padx=5)

        # Visual Separator
        ttk.Separator(dashboard_frame, orient=tk.VERTICAL).pack(
            side='left', padx=15, fill='y')

        # Worst-Case Combinations
        ttk.Label(dashboard_frame, text="Worst-Case Combinations:",
                  font=('Helvetica', 10, 'bold')).pack(side='left', padx=10)
        ttk.Label(dashboard_frame, textvariable=self.worst_case_guesses_var, font=(
            'Consolas', 12, 'bold'), foreground='#0000CC').pack(side='left', padx=5)

        # 4. Output Text Area
        ttk.Label(self.master, text="Simulation Output:", font=(
            'Helvetica', 12, 'bold')).pack(padx=10, pady=(10, 2), anchor='w')

        self.output_text = scrolledtext.ScrolledText(
            self.master,
            wrap=tk.WORD,
            height=15,
            bg='#1E1E1E',
            fg='#00FF00',
            font=self.output_font,
            insertbackground='#00FF00',
            state=tk.DISABLED
        )
        self.output_text.pack(padx=10, pady=5, fill='both', expand=True)
        self.log(
            "Welcome to the Brute-Force Simulator! Enter a password and click 'Start Attack'.", clear=True)

        # 5. Status Bar
        status_bar = ttk.Frame(
            self.master, padding="5 2 5 2", relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill='x')

        # Live Speed and Attempts Indicators
        ttk.Label(status_bar, textvariable=self.speed_var,
                  font=('Consolas', 9)).pack(side='left', padx=10)
        ttk.Label(status_bar, textvariable=self.attempts_var,
                  font=('Consolas', 9)).pack(side='right', padx=10)

        # Initial analysis update
        self.update_live_strength("")

    # --- GUI Control Methods ---

    def on_key_release(self, event):
        """Called when a key is released to update the strength meter and analysis."""
        password = self.password_entry.get()
        self.update_live_strength(password)
        self.update_character_contribution(password)

    # ... (Other GUI methods remain unchanged for brevity) ...
    
    def update_live_strength(self, password):
        """Analyzes password strength and updates the live UI elements."""
        if not password:
            self.strength_score_var.set(0)
            self.strength_text_var.set("Strength: N/A")
            self.strength_progress.config(style="TProgressbar")  # Reset style
            return

        strength_level, score, _, _, _, _, _ = assess_password_strength(
            password)

        # Convert score (max 10) to percentage (0-100)
        progress_value = min(score * 10, 100)

        self.strength_score_var.set(progress_value)
        self.strength_text_var.set(f"Strength: {strength_level}")

        # Change progress bar color based on strength
        if strength_level == "Very Strong":
            style_name = "Green.TProgressbar"
        elif strength_level == "Strong":
            style_name = "LightGreen.TProgressbar"
        elif strength_level == "Moderate":
            style_name = "Yellow.TProgressbar"
        else:  # Weak
            style_name = "Red.TProgressbar"

        self.strength_progress.config(style=style_name)

    def update_character_contribution(self, password):
        """Analyzes character types and updates the contribution labels."""
        length = len(password)
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_digit = any(c in string.digits for c in password)
        has_special = any(
            c not in string.ascii_letters and c not in string.digits and c not in string.whitespace for c in password)

        # Calculate character contribution to Keyspace Base
        lower_chars = 26 if has_lower else 0
        upper_chars = 26 if has_upper else 0
        digit_chars = 10 if has_digit else 0
        # Use 33 as an estimate for common symbol set size
        special_chars = 33 if has_special else 0

        total_chars = lower_chars + upper_chars + digit_chars + special_chars

        # Update variables
        self.len_var.set(f"Length: {length}")
        self.lower_var.set(f"a-z: {lower_chars}")
        self.upper_var.set(f"A-Z: {upper_chars}")
        self.digit_var.set(f"0-9: {digit_chars}")
        self.special_var.set(f"Symbols: {special_chars}")

        # Update worst-case combinations based on live analysis
        if total_chars > 0 and length > 0:
            keyspace = total_chars ** length
            self.worst_case_guesses_var.set(
                f"{keyspace:,.0f} (Base {total_chars})")
        else:
            self.worst_case_guesses_var.set("N/A")

    def toggle_password_visibility(self):
        """Toggles between showing and hiding the password in the entry field."""
        if self.show_password:
            self.password_entry.config(show="*")
            self.toggle_button.config(text="🙈")
            self.show_password = False
        else:
            self.password_entry.config(show="")
            self.toggle_button.config(text="👁️")
            self.show_password = True
            
    def update_dashboard(self, speed, attempts, time_to_crack):
        """Safely updates the live dashboard variables from the attack thread."""
        self.master.after(0, lambda: self._update_dashboard_ui(
            speed, attempts, time_to_crack))

    def _update_dashboard_ui(self, speed, attempts, time_to_crack):
        """Actual UI update logic for dashboard and status bar."""

        # Update dashboard
        self.time_var.set(format_time_duration(time_to_crack))

        # Update status bar (Live Speed)
        self.speed_var.set(f"Speed: {speed:,.2f} attempts/s")
        self.attempts_var.set(f"Attempts: {attempts:,}")

    def reset_dashboard(self):
        """Resets dashboard values when a new attack starts."""
        self.time_var.set("N/A")
        self.speed_var.set("Speed: 0 attempts/s")
        self.attempts_var.set("Attempts: 0")

    def log(self, message, clear=False):
        """Method to safely output text to the ScrolledText area."""
        self.master.after(0, lambda: self._update_log(message, clear))

    def _update_log(self, message, clear):
        # تفعيل الكتابة مؤقتاً
        self.output_text.config(state=tk.NORMAL)
        
        if clear:
            self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        
        # تعطيل الكتابة مرة أخرى
        self.output_text.config(state=tk.DISABLED)
        
    def stop_attack(self):
        """Sets the flag to stop the running attack thread."""
        self.stop_requested = True
        self.log("\n⚠️ Stop requested. Wrapping up current attempt...", clear=False)
        self.stop_button.config(state=tk.DISABLED, text="🛑 Stopping...")

    def start_attack_thread(self):
        """Starts the Brute-Force attack logic in a separate thread."""
        user_pass = self.password_entry.get()
        if not user_pass:
            self.log("⚠️ Please enter a password to test.", clear=True)
            return

        self.reset_dashboard()
        self.stop_requested = False

        self.log(f"Starting Brute-Force Attack on: {user_pass}", clear=True)
        self.crack_button.config(state=tk.DISABLED, text="⏳ Attacking...")
        self.stop_button.config(state=tk.NORMAL, text="🛑 Stop Attack")

        attack_thread = Thread(target=self.run_attack_logic, args=(user_pass,))
        attack_thread.start()

    # --- Core Logic Methods ---

    def run_attack_logic(self, user_pass):
        """The main password cracking logic (Brute-Force only)."""

        password_length = len(user_pass)
        attempts = 0
        found = False
        guess = ""
        start_time = time.time()

        # Read selected settings
        hardware_name = self.hardware_speed_var.get()
        theoretical_speed = ATTACK_SPEEDS[hardware_name]
        
        crack_target = self.crack_target_var.get()
        is_worst_case = "100%" in crack_target # Check for Worst Case setting

        # 2. Strength Analysis & Dynamic Keyspace Setup
        strength_level, strength_score, strength_feedback, has_upper, has_lower, has_digit, has_special = assess_password_strength(
            user_pass)

        # ------------------------------------------------------------------
        # --- PHASE 1: PRE-ATTACK ANALYSIS & PREDICTION ---
        # ------------------------------------------------------------------

        self.log("\n--- Password Strength Analysis ---")
        self.log(
            f"Strength Level: {strength_level} (Score: {strength_score}/10)")
        for item in strength_feedback:
            self.log(f"- {item}")
        self.log("----------------------------------")

        # --- Brute-Force Setup ---
        dynamic_charset = []
        
        # Educational Value: Calculate and log the Keyspace Base
        keyspace_log_items = []
        if has_lower:
            dynamic_charset.extend(list(string.ascii_lowercase))
            keyspace_log_items.append("26 Lower (a-z)")
        if has_upper:
            dynamic_charset.extend(list(string.ascii_uppercase))
            keyspace_log_items.append("26 Upper (A-Z)")
        if has_digit:
            dynamic_charset.extend(list(string.digits))
            keyspace_log_items.append("10 Digits (0-9)")
        if has_special:
            symbol_chars = list("!@#$%^&*()-_+=[]{}|:;\"'<,>.?/`~")
            dynamic_charset.extend(symbol_chars)
            keyspace_log_items.append(f"{len(symbol_chars)} Symbols")

        if not dynamic_charset:
            dynamic_charset = list(string.ascii_letters + string.digits) # Default if password is empty or only whitespace

        DYNAMIC_CHARSET_SIZE = len(dynamic_charset)
        total_keyspace = DYNAMIC_CHARSET_SIZE ** password_length
        
        # Calculate target attempts based on user choice
        target_factor = 1.0 if is_worst_case else 0.5
        target_attempts_needed = total_keyspace * target_factor

        self.log(f"Attack Mode: **Standard Brute-Force Attack**")
        self.log(f"Keyspace Base: **{DYNAMIC_CHARSET_SIZE}** characters ({', '.join(keyspace_log_items)})")
        self.log(f"Search space size (Total): **{total_keyspace:,}** possibilities")
        self.log(f"Prediction Target: **{crack_target}** (Total Attempts: {target_attempts_needed:,.0f})")
        self.log(
            f"Theoretical speed: {theoretical_speed:,.0f} attempts/s ({hardware_name})")

        # Update dashboard with predicted time
        time_to_crack_prediction = target_attempts_needed / theoretical_speed
        self.update_dashboard(theoretical_speed, 0, time_to_crack_prediction)

        self.log("----------------------------------")

        # --- Brute-Force Attack Phase (Fast & Stable Random Sampling) ---
        print_frequency = 100000
        dashboard_update_frequency = 500000
        benchmark_attempts = 100000
        benchmark_start_time = time.time()
        benchmark_speed = 0
        final_speed_for_report = theoretical_speed

        while not found and not self.stop_requested:
            # Generate a random guess
            guess = "".join(random.choices(dynamic_charset, k=password_length))
            attempts += 1

            if guess == user_pass:
                found = True
                break

            # Benchmarking and Live Update
            if attempts == benchmark_attempts and time.time() - benchmark_start_time > 0:
                benchmark_end_time = time.time()
                benchmark_time = benchmark_end_time - benchmark_start_time
                benchmark_speed = benchmark_attempts / benchmark_time

                # Use the minimum of benchmark speed or theoretical speed for prediction
                final_speed_for_report = min(
                    benchmark_speed, theoretical_speed)

                time_to_crack_real = target_attempts_needed / final_speed_for_report
                self.update_dashboard(
                    final_speed_for_report, attempts, time_to_crack_real)

                self.log(
                    f"\n[BENCHMARK] Device speed confirmed: {benchmark_speed:,.2f} attempts/s")
                self.log("----------------------------------")

            # Update status bar frequently
            if attempts % dashboard_update_frequency == 0 and final_speed_for_report > 0 and not self.stop_requested:
                time_to_crack_real = target_attempts_needed / final_speed_for_report
                self.update_dashboard(
                    final_speed_for_report, attempts, time_to_crack_real)

            if attempts % print_frequency == 0 and not self.stop_requested:
                self.log(f"Brute-Force Attempt #{attempts:,}")

        # Final speed calculation
        if benchmark_speed > 0:
            final_speed_for_report = min(benchmark_speed, theoretical_speed)
        
        # ------------------------------------------------------------------
        # --- PHASE 2: FINAL RESULTS AND ANALYSIS ---
        # ------------------------------------------------------------------

        end_time = time.time()
        time_taken = end_time - start_time

        # Final calculations
        time_to_crack_final_prediction = target_attempts_needed / \
            final_speed_for_report if final_speed_for_report > 0 else float(
                'inf')

        if found:
            report_title = "🥳 MATCH FOUND! FINAL REPORT"
            final_message = "✅ Attack Finished!"
            self.update_dashboard(final_speed_for_report,
                                  attempts, time_to_crack_final_prediction)
        else:
            report_title = "🛑 ATTACK STOPPED! INTERIM REPORT"
            final_message = "🛑 Attack Stopped"
            self.update_dashboard(final_speed_for_report,
                                  attempts, float('inf'))

        self.log(f"\n\n####################################")
        self.log(f"### {report_title} ###")
        self.log("####################################")
        self.log(
            f"Last Attempted Guess: {guess} (If not found, this is the last attempt)")
        self.log(f"Total Attempts: **{attempts:,}**")
        self.log(f"Time Taken (Actual): **{time_taken:.4f} seconds**")
        self.log(
            f"Device Speed (Used for Prediction): **{final_speed_for_report:,.2f} attempts/s**")

        self.log("\n--- Theoretical Cracking Analysis ---")
        self.log(f"Attack Type: **Brute-Force**")
        self.log(f"Prediction Target: **{crack_target}**")
        self.log(f"Target Attempts: **{target_attempts_needed:,.0f}**")
        self.log(
            f"Predicted Time to Crack: **{format_time_duration(time_to_crack_final_prediction)}**")

        self.master.after(0, lambda: self.crack_button.config(
            state=tk.NORMAL, text=final_message))
        self.master.after(0, lambda: self.stop_button.config(
            state=tk.DISABLED, text="🛑 Stop Attack"))


if __name__ == "__main__":
    root = tk.Tk()
    app = CrackerApp(root)
    root.mainloop()