import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageRotatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Rotator - With Delete Option")
        self.root.geometry("1000x700")
        
        # Image data
        self.images = []
        self.current_index = 0
        self.original_img = None
        self.display_img = None
        self.label = None
        
        # Setup UI
        self.setup_ui()
        self.bind_keyboard_shortcuts()
        
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
        
        # NEW: Delete button (red color, warning)
        tk.Button(nav_frame, text="🗑️ Delete", 
                 command=self.delete_image, bg="red", fg="white",
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(nav_frame, text="💾 Save", 
                 command=self.save_image).pack(side=tk.LEFT, padx=5)
        
        # Shortcut legend
        shortcuts_frame = tk.Frame(self.root)
        shortcuts_frame.pack(pady=5)
        tk.Label(shortcuts_frame, 
                text="Shortcuts: ←→ arrows, A/D rotate, S save, L load, X delete", 
                font=("Arial", 10)).pack()
        
        # Image display
        self.image_frame = tk.Frame(self.root, bg='white')
        self.image_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
    def bind_keyboard_shortcuts(self):
        """Keyboard shortcuts including DELETE key"""
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<a>', lambda e: self.rotate_left())
        self.root.bind('<d>', lambda e: self.rotate_right())
        self.root.bind('<A>', lambda e: self.rotate_left())
        self.root.bind('<D>', lambda e: self.rotate_right())
        self.root.bind('<s>', lambda e: self.save_image())
        self.root.bind('<S>', lambda e: self.save_image())
        self.root.bind('<l>', lambda e: self.load_directory())
        self.root.bind('<L>', lambda e: self.load_directory())
        self.root.bind('<Delete>', lambda e: self.delete_image())  # NEW: Delete key
        self.root.bind('<x>', lambda e: self.delete_image())       # NEW: X key
        self.root.bind('<X>', lambda e: self.delete_image())
    
    def delete_image(self, event=None):
        """NEW: Delete current image with confirmation"""
        if not self.images:
            return
        
        current_filename = self.images[self.current_index]
        img_path = os.path.join(self.image_dir, current_filename)
        
        # Confirmation dialog
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Delete '{current_filename}'?\nThis cannot be undone.",
                                   icon='warning')
        
        if result:
            try:
                os.remove(img_path)
                # Remove from list and adjust index
                del self.images[self.current_index]
                
                # Adjust index after deletion
                if self.images:
                    self.current_index = min(self.current_index, len(self.images) - 1)
                    self.load_current_image()
                else:
                    self.clear_image_display()
                
                self.update_index_label()
                messagebox.showinfo("Deleted", f"Deleted: {current_filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete {current_filename}:\n{str(e)}")
    
    def clear_image_display(self):
        """Clear image display when no images left"""
        if self.label:
            self.label.destroy()
            self.label = None
        self.original_img = None
        self.display_img = None
        self.index_label.config(text="No images remaining")
    
    def load_directory(self, event=None):
        directory = filedialog.askdirectory()
        if not directory:
            return
            
        self.images = [f for f in os.listdir(directory) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))]
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
        win_width = 800
        win_height = 500
        
        img_width, img_height = self.display_img.size
        ratio = min(win_width/img_width, win_height/img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        self.display_img.thumbnail(new_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(self.display_img)
        if self.label:
            self.label.configure(image=photo)
            self.label.image = photo
        else:
            self.label = tk.Label(self.image_frame, image=photo)
            self.label.pack(expand=True)
            self.label.image = photo
    
    def next_image(self, event=None):
        if not self.images:
            return
        self.current_index = (self.current_index + 1) % len(self.images)
        self.load_current_image()
        self.update_index_label()
    
    def prev_image(self, event=None):
        if not self.images:
            return
        self.current_index = (self.current_index - 1) % len(self.images)
        self.load_current_image()
        self.update_index_label()
    
    def update_index_label(self):
        if not self.images:
            self.index_label.config(text="No images remaining")
        else:
            self.index_label.config(
                text=f"{self.current_index + 1} / {len(self.images)} - {self.images[self.current_index]}"
            )
    
    def rotate_left(self, event=None):
        if self.display_img:
            self.display_img = self.display_img.rotate(90, expand=True)
            self.show_image()
    
    def rotate_right(self, event=None):
        if self.display_img:
            self.display_img = self.display_img.rotate(-90, expand=True)
            self.show_image()
    
    def save_image(self, event=None):
        if not self.images or not self.display_img:
            return
            
        img_path = os.path.join(self.image_dir, self.images[self.current_index])
        self.display_img.save(img_path, quality=95)
        messagebox.showinfo("Saved", f"Saved: {self.images[self.current_index]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRotatorApp(root)
    root.mainloop()
