import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageRotatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Rotator - Keyboard Shortcuts Enabled")
        self.root.geometry("1000x700")
        
        # Image data
        self.images = []
        self.current_index = 0
        self.original_img = None
        self.display_img = None
        self.label = None
        
        # Setup UI
        self.setup_ui()
        self.bind_keyboard_shortcuts()  # NEW: Add keyboard bindings
        
    def setup_ui(self):
        # Navigation frame
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)
        
        tk.Button(nav_frame, text="📁 Load Directory", 
                 command=self.load_directory).pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons
        tk.Button(nav_frame, text="⬅ Prev", command=self.prev_image).pack(side=tk.LEFT, padx=5)
        self.index_label = tk.Label(nav_frame, text="No images loaded")
        self.index_label.pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Next ➡", command=self.next_image).pack(side=tk.LEFT, padx=5)
        
        # Rotation buttons
        tk.Button(nav_frame, text="↺ Rotate Left (90°)", 
                 command=self.rotate_left).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="↻ Rotate Right (90°)", 
                 command=self.rotate_right).pack(side=tk.LEFT, padx=5)
        
        tk.Button(nav_frame, text="💾 Save", 
                 command=self.save_image).pack(side=tk.LEFT, padx=5)
        
        # Shortcut legend
        shortcuts_frame = tk.Frame(self.root)
        shortcuts_frame.pack(pady=5)
        tk.Label(shortcuts_frame, text="Shortcuts: ←→ arrows, A/D rotate, S save, L load", 
                font=("Arial", 10)).pack()
        
        # Image display
        self.image_frame = tk.Frame(self.root, bg='white')
        self.image_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
    def bind_keyboard_shortcuts(self):
        """NEW: Bind keyboard shortcuts to all methods"""
        self.root.bind('<Left>', lambda e: self.prev_image())      # ← Arrow: Previous
        self.root.bind('<Right>', lambda e: self.next_image())     # → Arrow: Next
        self.root.bind('<a>', lambda e: self.rotate_left())        # A: Rotate Left
        self.root.bind('<d>', lambda e: self.rotate_right())       # D: Rotate Right
        self.root.bind('<A>', lambda e: self.rotate_left())        # Shift+A: Rotate Left
        self.root.bind('<D>', lambda e: self.rotate_right())       # Shift+D: Rotate Right
        self.root.bind('<s>', lambda e: self.save_image())         # S: Save
        self.root.bind('<S>', lambda e: self.save_image())         # Shift+S: Save
        self.root.bind('<l>', lambda e: self.load_directory())     # L: Load Directory
        self.root.bind('<L>', lambda e: self.load_directory())     # Shift+L: Load
        
    def load_directory(self, event=None):  # Modified: accepts event
        directory = filedialog.askdirectory()
        if not directory:
            return
            
        self.images = [f for f in os.listdir(directory) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))]
        self.images = sorted(self.images, key=os.path.basename)
        self.image_dir = directory
        self.current_index = 0
        
        if self.images:
            self.load_current_image()
            self.update_index_label()
        else:
            messagebox.showinfo("Info", "No images found in directory")
    
    def load_current_image(self):
        if not self.images:
            return
            
        img_path = os.path.join(self.image_dir, self.images[self.current_index])
        self.original_img = Image.open(img_path)
        self.display_img = self.original_img.copy()
        self.show_image()
    
    def show_image(self):
        # Resize image to fit window (maintain aspect ratio)
        win_width = 800
        win_height = 500
        
        img_width, img_height = self.display_img.size
        ratio = min(win_width/img_width, win_height/img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        self.display_img.thumbnail(new_size, Image.Resampling.LANCZOS)
        
        # Update or create label
        photo = ImageTk.PhotoImage(self.display_img)
        if self.label:
            self.label.configure(image=photo)
            self.label.image = photo
        else:
            self.label = tk.Label(self.image_frame, image=photo)
            self.label.pack(expand=True)
            self.label.image = photo
    
    def next_image(self, event=None):  # Modified: accepts event
        if not self.images:
            return
        self.current_index = (self.current_index + 1) % len(self.images)
        self.load_current_image()
        self.update_index_label()
    
    def prev_image(self, event=None):  # Modified: accepts event
        if not self.images:
            return
        self.current_index = (self.current_index - 1) % len(self.images)
        self.load_current_image()
        self.update_index_label()
    
    def update_index_label(self):
        self.index_label.config(
            text=f"{self.current_index + 1} / {len(self.images)} - {self.images[self.current_index]}"
        )
    
    def rotate_left(self, event=None):  # Modified: accepts event
        if self.display_img:
            self.display_img = self.display_img.rotate(90, expand=True)
            self.show_image()
    
    def rotate_right(self, event=None):  # Modified: accepts event
        if self.display_img:
            self.display_img = self.display_img.rotate(-90, expand=True)
            self.show_image()
    
    def save_image(self, event=None):  # Modified: accepts event
        if not self.images or not self.display_img:
            return
            
        img_path = os.path.join(self.image_dir, self.images[self.current_index])
        self.display_img.save(img_path, quality=95)
        messagebox.showinfo("Saved", f"Saved: {self.images[self.current_index]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRotatorApp(root)
    root.mainloop()
