# 🛡️ Brute-Force Cracking Simulator: Your Password Strength Tester (GUI, CLI, & EXE)

**Attribution:** Inspired by the educational efforts of **Geekcomputers**. [Check out their GitHub here!](https://github.com/geekcomputers) The custom icons were made by alfredo-creates. [Go check him out here!](https://www.flaticon.com/authors/alfredo-creates)

---

## 💡 Why Test Your Passwords? (The Core Benefit)

**Wondering if your passwords are strong enough to withstand a real attack?** This educational tool is here to help! It provides a realistic simulation of **Brute-Force Attacks** so you can measure the **actual time** it would take for modern hardware (CPU, GPU, ASIC) to compromise your digital defenses.

In a world full of digital threats, the strongest defense starts with **self-assessment**. Use this simulator to:

* **Get a Reality Check:** Stop guessing! See the precise time estimate (in seconds, years, or decades) for your passwords to be cracked.
* **Learn the Security Ropes:** Witness how small changes—adding a symbol or increasing length—can dramatically impact security.
* **Choose Your Risk Level:** Select between the **50% (Average Case)** or the **100% (Worst-Case Scenario)**.

---

## ⚠️ CRITICAL NOTE: Windows Defender False Positive

# Man i dont know why the exe files get flagged as a virus:(

---

## ✨ Available Versions & Execution

The project offers full flexibility, whether you prefer visual feedback or command-line efficiency:

| Version | Files | Key Features |
| :--- | :--- | :--- |
| **Graphical User Interface (GUI)** | `cracker_app.py` | Users who prefer a **visual interface**, complete with a live dashboard and progress bars. |
| **Command Line Interface (CLI)** | `cracker_cli.py` | Developers who need **speed, raw data**, and a live-updating attempts counter. |
| **Executable (EXE)** | `cracker_cli.exe / cracker_app.exe` | **Windows users who don't want to install Python.** |

---

## 🚀 Quick Start

### 1. Run from Source Code (Python Source)

Ensure the project files (`core_logic.py`, `cracker_cli.py`, `cracker_app.py`) are together.

| Version | Command |
| :--- | :--- |
| **GUI** | `python cracker_app.py` |
| **CLI** | `python cracker_cli.py` |

### 2. Run the Executable (Windows EXE)

If you're using the ready-made executable (check the `dist` folder):

1.  Open Command Prompt (CMD) or PowerShell.
2.  Navigate to the executable's folder.
3.  Run it:
    ```bash
    .\cracker_cli.exe
    ```

---

## 🤝 Contribution

This project is complete, but patches and new features are always welcome!

* Open an **Issue** to report any problems or share ideas.
* Submit a **Pull Request** with your code changes.

**Test your security, learn the science, and stay safe!**
