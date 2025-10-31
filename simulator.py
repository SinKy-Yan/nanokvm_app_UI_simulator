import sys
import importlib.util
import threading
import numpy as np
import pygame
import gc
import argparse

# Screen dimensions
ORIGINAL_WIDTH = 172
ORIGINAL_HEIGHT = 320
SCALE_FACTOR = 2
# Rotated screen dimensions for landscape view
SCREEN_WIDTH = ORIGINAL_HEIGHT * SCALE_FACTOR
SCREEN_HEIGHT = ORIGINAL_WIDTH * SCALE_FACTOR

def main():
    parser = argparse.ArgumentParser(description="Run a simulation of a display-based Python script.")
    parser.add_argument("script", help="Path to the demo script to simulate.")
    parser.add_argument("--timeout", type=int, help="Number of seconds to run the simulation before automatically exiting.")
    
    args = parser.parse_args()
    
    script_path = args.script
    timeout_seconds = args.timeout

    # Load the specified demo script as a module
    spec = importlib.util.spec_from_file_location("demo_module", script_path)
    demo_module = importlib.util.module_from_spec(spec)
    
    # First, execute the module to load all its contents
    spec.loader.exec_module(demo_module)

    # Get a reference to the original hardware-dependent class
    OriginalDisplay = demo_module.RGB565Display

    # THIS IS THE CORRECTED MONKEY PATCH using inheritance
    class PygameDisplay(OriginalDisplay):
        def __init__(self, fb_device=None):
            # 首先, 调用父类的构造函数来设置字体、逻辑尺寸等.
            # 传入 fb_device=None 来避免在Mac上尝试打开真实的framebuffer.
            super().__init__(fb_device=None)

            # 然后, 用我们自己的numpy数组覆盖父类中的framebuffer, 以便模拟.
            self.fb_array = np.zeros((self.physical_height, self.physical_width), dtype=np.uint16)

        def update_screen(self, img):
            """
            这个方法会被主脚本调用. 在模拟器中, 我们将传入的Pillow图像
            转换为numpy数组, 存入我们伪造的framebuffer中, 以便被模拟器的主循环读取并显示.
            """
            physical_img = img.rotate(90, expand=True)
            rgb_array = np.array(physical_img)
            r = (rgb_array[:,:,0] >> 3).astype(np.uint16)
            g = (rgb_array[:,:,1] >> 2).astype(np.uint16)
            b = (rgb_array[:,:,2] >> 3).astype(np.uint16)
            rgb565 = (r << 11) | (g << 5) | b
            self.fb_array[:,:] = rgb565

        def close(self):
            # 模拟器负责窗口关闭, 这里什么都不用做.
            pass

    # Now, we replace the class in the loaded module with our new, patched class.
    demo_module.RGB565Display = PygameDisplay
    
    # The demo script's main function runs an infinite loop.
    # We must run it in a separate thread so it doesn't block our pygame loop.
    demo_thread = threading.Thread(target=demo_module.main, daemon=True)
    demo_thread.start()
    
    # --- Pygame Simulation Loop ---
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Simulator - {script_path}")
    clock = pygame.time.Clock()
    
    display_instance = None
    find_instance_timeout = 5 # seconds
    find_start_time = pygame.time.get_ticks()
    
    while not display_instance:
        for obj in gc.get_objects():
            if isinstance(obj, PygameDisplay):
                display_instance = obj
                break
        if display_instance:
            break
        
        if (pygame.time.get_ticks() - find_start_time) > find_instance_timeout * 1000:
            print("Error: Could not find the display instance created by the demo script.")
            pygame.quit()
            sys.exit(1)
        pygame.time.wait(100) # Check every 100ms

    if timeout_seconds:
        print(f"Simulator started. Will auto-exit in {timeout_seconds} seconds.")
    else:
        print("Simulator started. Press Ctrl+C or close the window to exit.")

    running = True
    start_time = pygame.time.get_ticks()
    
    while running:
        # Conditional auto-exit after timeout
        if timeout_seconds:
            if (pygame.time.get_ticks() - start_time) > timeout_seconds * 1000:
                print(f"Simulation timed out after {timeout_seconds} seconds.")
                running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get the raw RGB565 data from the fake framebuffer
        fb_data = display_instance.fb_array

        if fb_data is None or not hasattr(fb_data, "ndim") or fb_data.ndim != 2:
            clock.tick(60)
            continue

        # Rotate the framebuffer data 90 degrees clockwise for landscape display
        rotated_fb = np.rot90(fb_data, k=3)

        # Convert RGB565 to RGB888 for pygame
        r5 = ((rotated_fb >> 11) & 0x1F).astype(np.uint8) << 3
        g6 = ((rotated_fb >> 5) & 0x3F).astype(np.uint8) << 2
        b5 = (rotated_fb & 0x1F).astype(np.uint8) << 3
        
        # Combine into an RGB888 numpy array
        rgb888 = np.stack([r5, g6, b5], axis=-1)

        # Create a pygame surface from the numpy array.
        surface = pygame.surfarray.make_surface(rgb888.transpose(1, 0, 2))
        
        # Scale the surface to the final window size
        scaled_surface = pygame.transform.scale(surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Draw the scaled surface to the screen
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()
    print("Simulator closed.")

if __name__ == "__main__":
    main()
