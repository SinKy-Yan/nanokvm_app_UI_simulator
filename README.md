# Framebuffer Script Simulator

This program is a graphical simulator designed to run Python scripts that were originally intended for a direct-write framebuffer display (like `/dev/fb0`). It uses Pygame to create a desktop window and render the output of these scripts, allowing for development and testing in a standard desktop environment.

## Features

- **Monkey Patching**: Dynamically replaces the hardware-specific display class (`RGB565Display`) from the target script with a Pygame-based simulation class at runtime.
- **Configurable Timeout**: Can be set to automatically exit after a certain number of seconds, which is useful for automated testing.
- **Rotated Display**: The output is rotated 90 degrees clockwise to a landscape orientation.

## How to Use

1.  **Activate the Virtual Environment**:
    All dependencies are located in the `nv` virtual environment. Activate it first.
    ```bash
    source nv/bin/activate
    ```

2.  **Run the Simulator**:
    Execute `simulator.py`, passing the path to the target script you want to simulate as the first argument.

    **Syntax**:
    ```bash
    python simulator.py <path_to_script> [--timeout <seconds>]
    ```

    **Examples**:

    - To run a script indefinitely:
      ```bash
      # Make sure you are in the parent directory of simulator_app
      python simulator_app/simulator.py coin.py
      ```

    - To run a script and have it automatically close after 10 seconds:
      ```bash
      python simulator_app/simulator.py conway.py --timeout 10
      ```
