# cracker_cli.py

import random
import time
import sys
import getpass
from core_logic import ATTACK_SPEEDS, format_time_duration, assess_password_strength, build_keyspace

def update_live_progress(attempts, final_speed, target_attempts):
    """Updates the current line in the console with live attack stats."""
    
    if final_speed <= 0:
        time_left_str = "Calculating..."
    else:
        remaining_attempts = max(0, target_attempts - attempts)
        time_left = remaining_attempts / final_speed
        time_left_str = format_time_duration(time_left)

    progress_line = (
        f"\rAttempts: {attempts:,} | "
        f"Speed: {final_speed:,.2f} attempts/s | "
        f"Time Left (Est.): {time_left_str}"
    )
    
    sys.stdout.write(progress_line)
    sys.stdout.flush()

def simulate_attack_session():
    """Contains the core logic for a single simulation run."""
    
    # 1. Input Password and Settings
    print("\n" + "="*50)
    print("🔒 New Simulation Session")
    print("="*50)
    
    # NOTE: Using input() for compatibility with IDEs like VS Code
    user_pass = input("Enter Password to Test (NOTE: Input is visible in IDE): ")
    
    if not user_pass:
        print("⚠️ Error: Password cannot be empty. Returning to menu.")
        return

    # Choose hardware speed (Ensuring valid input)
    print("\n--- Choose Attacker Hardware Speed ---")
    speeds_list = list(ATTACK_SPEEDS.keys())
    for i, name in enumerate(speeds_list):
        print(f"[{i+1}] {name} ({ATTACK_SPEEDS[name]:,} attempts/s)")
    
    while True:
        try:
            choice_input = input("Select speed option (1-3, default 1): ").strip()
            choice = int(choice_input) if choice_input else 1
            
            if 1 <= choice <= len(speeds_list):
                hardware_name = speeds_list[choice - 1]
                theoretical_speed = ATTACK_SPEEDS[hardware_name]
                break
            else:
                print("Invalid choice. Please select 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    # Choose prediction target (Ensuring valid input)
    print("\n--- Choose Prediction Target ---")
    print("[1] 50% (Average Case - Expected Crack Time)")
    print("[2] 100% (Worst Case - Maximum Time)")
    
    while True:
        try:
            target_input = input("Select target (1 or 2, default 1): ").strip()
            target_choice = int(target_input) if target_input else 1
            
            if target_choice == 1:
                crack_target = "50% (Average Case)"
                is_worst_case = False
                break
            elif target_choice == 2:
                crack_target = "100% (Worst Case)"
                is_worst_case = True
                break
            else:
                print("Invalid choice. Please select 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    
    # 2. Analysis Setup
    password_length = len(user_pass)
    
    strength_level, strength_score, strength_feedback, has_upper, has_lower, has_digit, has_special = assess_password_strength(
        user_pass)

    dynamic_charset, dynamic_charset_size, total_keyspace, keyspace_log_items = build_keyspace(
        user_pass, has_upper, has_lower, has_digit, has_special
    )
    
    target_factor = 1.0 if is_worst_case else 0.5
    target_attempts_needed = total_keyspace * target_factor
    
    time_to_crack_prediction = target_attempts_needed / theoretical_speed if theoretical_speed > 0 else float('inf')


    # 3. Pre-Attack Report (CLI)
    print("\n" + "="*50)
    print(f"--- PRE-ATTACK ANALYSIS REPORT ---")
    print("="*50)
    print(f"Password Length: {password_length}")
    print(f"Strength Level: {strength_level} (Score: {strength_score}/10)")
    print("Feedback:")
    for item in strength_feedback:
        print(f"  - {item}")
    
    print("\n--- Keyspace & Speed ---")
    print(f"Hardware Speed: {hardware_name} ({theoretical_speed:,.0f} attempts/s)")
    print(f"Keyspace Base: {dynamic_charset_size} characters ({', '.join(keyspace_log_items)})")
    print(f"Total Combinations: {total_keyspace:,}")
    print(f"Prediction Target: {crack_target}")
    print(f"Target Attempts: {target_attempts_needed:,.0f}")
    print(f"Predicted Time to Crack: {format_time_duration(time_to_crack_prediction)}")
    print("\nStarting simulated attack... (Look below for live progress)")


    # 4. Simulation 
    attempts = 0
    found = False
    start_time = time.time()
    
    benchmark_attempts = 100000 
    benchmark_start_time = time.time()
    benchmark_speed = 0
    final_speed_for_report = theoretical_speed # Start with theoretical speed
    
    # Update frequency for the live line (can be adjusted)
    live_update_frequency = 500000 

    # Brute-Force loop for benchmarking and finding short passwords
    while not found and attempts < target_attempts_needed:
        guess = "".join(random.choices(dynamic_charset, k=password_length))
        attempts += 1
        
        if guess == user_pass:
            found = True
            break

        # Benchmarking and updating the speed
        if attempts == benchmark_attempts and time.time() - benchmark_start_time > 0:
            benchmark_speed = benchmark_attempts / (time.time() - benchmark_start_time)
            # Use the min of measured or theoretical speed
            final_speed_for_report = min(benchmark_speed, theoretical_speed)
        
        # Live progress update
        if attempts % live_update_frequency == 0:
            update_live_progress(attempts, final_speed_for_report, target_attempts_needed)


    # Final live update after loop finishes
    update_live_progress(attempts, final_speed_for_report, target_attempts_needed)
    print() # Print a newline to separate the progress line from the report

    
    # 5. Final Report
    end_time = time.time()
    time_taken = end_time - start_time
    
    # Recalculate based on final speed
    time_to_crack_final_prediction = target_attempts_needed / final_speed_for_report if final_speed_for_report > 0 else float('inf')

    
    print("\n" + "="*50)
    print("--- FINAL SIMULATION REPORT ---")
    print("="*50)
    
    if found:
        print(f"🥳 MATCH FOUND! Password was found in {attempts:,} attempts.")
    elif attempts >= target_attempts_needed:
        # This should only happen for very short passwords since we stop at target_attempts
        print(f"✅ Simulation Finished (Hit target attempts: {target_attempts_needed:,.0f}).")
    else:
        # Should not happen in this simulation logic, but for safety
        print("⚠️ Simulation ended prematurely.") 

    print(f"Actual Attempts in Simulation: {attempts:,}")
    print(f"Time Taken for Simulation: {time_taken:.4f} seconds")
    print(f"Device Speed (Measured/Used): {final_speed_for_report:,.2f} attempts/s")
    
    print("\n--- Final Prediction ---")
    print(f"Total Combinations: {total_keyspace:,}")
    print(f"Target Attempts ({crack_target}): {target_attempts_needed:,.0f}")
    print(f"Predicted Total Time: {format_time_duration(time_to_crack_final_prediction)}")
    print("\n")


def run_cli_attack():
    """Main CLI entry point with loop to ask for continuous simulations."""
    
    print("\n" + "="*50)
    print("🔒 Brute-Force Cracking Simulator (CLI)")
    print("="*50)
    
    while True:
        simulate_attack_session()
        
        while True:
            # Ask the user if they want to run another test
            choice = input("Do you want to run another simulation? (y/n, default y): ").strip().lower()
            if choice in ['n', 'no']:
                print("\nThank you for using the Brute-Force Simulator! Goodbye. 👋")
                return
            elif choice in ['y', 'yes', '']:
                break
            else:
                print("Invalid choice. Please enter 'y' or 'n'.")


if __name__ == "__main__":
    run_cli_attack()