"""
GUI Interface for ID Card Printer
Provides visual interface with Photoshop Bridge to Epson 4830
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
from PIL import Image, ImageTk
import threading
from card_printer import create_card_image, create_dual_card_layout, print_cards
from excel_reader import read_card_data, create_sample_excel
from alignment_test import print_alignment_test
from subscription_manager import get_subscription_status


class PhotoshopBridgeInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("ID Card Printer - Photoshop Bridge to Epson 4830")
        self.geometry("900x700")
        self.configure(bg='#2b2b2b')
        
        # Load configuration
        self.config = self.load_config()
        self.card_data = []
        self.current_preview = None
        self.subscription_status = get_subscription_status(self.config)
        
        # Create UI
        self.create_menu()
        self.create_main_interface()
        
        # Show subscription warning after UI is built
        if not self.subscription_status['active']:
            self.after(100, self._show_subscription_expired_warning)
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "config.json not found!")
            return {}
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Excel Data", command=self.load_excel_data)
        file_menu.add_command(label="Create Sample Excel", command=self.create_sample)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Alignment Test", command=self.run_alignment_test)
        tools_menu.add_command(label="Printer Status", command=self.check_printer_status)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Create main interface layout"""        
        # Title bar
        title_frame = tk.Frame(self, bg='#1e1e1e', height=60)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(
            title_frame, 
            text="Photoshop Bridge → Epson 4830 (2-Card Tray)",
            font=("Arial", 16, "bold"),
            bg='#1e1e1e',
            fg='#00a4ef'
        )
        title_label.pack(pady=15)
        
        # Main content area
        content_frame = tk.Frame(self, bg='#2b2b2b')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(content_frame, bg='#3c3c3c', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Printer info
        printer_info = tk.LabelFrame(
            left_panel, 
            text="Printer Information",
            bg='#3c3c3c',
            fg='white',
            font=("Arial", 10, "bold")
        )
        printer_info.pack(fill=tk.X, padx=10, pady=10)
        
        printer_name = self.config.get('printer', {}).get('name', 'Not configured')
        tk.Label(
            printer_info,
            text=f"Printer: {printer_name}",
            bg='#3c3c3c',
            fg='#cccccc',
            wraplength=250
        ).pack(anchor=tk.W, padx=5, pady=5)
        
        tk.Label(
            printer_info,
            text=f"Tray: 2-Card Plastic Tray",
            bg='#3c3c3c',
            fg='#cccccc'
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Subscription status
        sub_frame = tk.LabelFrame(
            left_panel,
            text="Subscription",
            bg='#3c3c3c',
            fg='white',
            font=("Arial", 10, "bold")
        )
        sub_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if self.subscription_status['active']:
            sub_color = '#ffcc00' if (
                self.subscription_status['days_remaining'] is not None
                and self.subscription_status['days_remaining'] <= 30
            ) else '#00ff00'
        else:
            sub_color = '#ff4444'
        
        self.sub_status_label = tk.Label(
            sub_frame,
            text=self.subscription_status['message'],
            bg='#3c3c3c',
            fg=sub_color,
            wraplength=250,
            justify=tk.LEFT
        )
        self.sub_status_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Data source
        data_frame = tk.LabelFrame(
            left_panel,
            text="Data Source",
            bg='#3c3c3c',
            fg='white',
            font=("Arial", 10, "bold")
        )
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            data_frame,
            text="📂 Load Excel Data",
            command=self.load_excel_data,
            bg='#0078d4',
            fg='white',
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(fill=tk.X, padx=5, pady=5)
        
        self.data_status_label = tk.Label(
            data_frame,
            text="No data loaded",
            bg='#3c3c3c',
            fg='#ffcc00'
        )
        self.data_status_label.pack(padx=5, pady=5)
        
        # Card list
        list_frame = tk.LabelFrame(
            left_panel,
            text="Card Queue",
            bg='#3c3c3c',
            fg='white',
            font=("Arial", 10, "bold")
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.card_listbox = tk.Listbox(
            list_frame,
            bg='#2b2b2b',
            fg='white',
            selectbackground='#0078d4',
            font=("Arial", 9)
        )
        self.card_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.card_listbox.bind('<<ListboxSelect>>', self.on_card_select)
        
        # Action buttons
        action_frame = tk.Frame(left_panel, bg='#3c3c3c')
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            action_frame,
            text="🔍 Preview Cards",
            command=self.preview_cards,
            bg='#00a4ef',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            height=2
        ).pack(fill=tk.X, pady=5)
        
        print_btn_bg = '#555555' if not self.subscription_status['active'] else '#107c10'
        self.print_button = tk.Button(
            action_frame,
            text="🖨️ Print All Cards",
            command=self.print_all_cards,
            bg=print_btn_bg,
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            height=2,
            state=tk.NORMAL if self.subscription_status['active'] else tk.DISABLED
        )
        self.print_button.pack(fill=tk.X, pady=5)
        
        tk.Button(
            action_frame,
            text="⚙️ Alignment Test",
            command=self.run_alignment_test,
            bg='#ff8c00',
            fg='white',
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(fill=tk.X, pady=5)
        
        # Right panel - Preview and Console
        right_panel = tk.Frame(content_frame, bg='#2b2b2b')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Preview area
        preview_frame = tk.LabelFrame(
            right_panel,
            text="Card Preview",
            bg='#3c3c3c',
            fg='white',
            font=("Arial", 10, "bold")
        )
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Console output
        console_frame = tk.LabelFrame(
            right_panel,
            text="Console Output",
            bg='#3c3c3c',
            fg='white',
            font=("Arial", 10, "bold")
        )
        console_frame.pack(fill=tk.X, pady=(0, 0))
        
        self.console = scrolledtext.ScrolledText(
            console_frame,
            height=8,
            bg='#1e1e1e',
            fg='#00ff00',
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.console.pack(fill=tk.X, padx=5, pady=5)
        
        self.log("System initialized. Ready to print.")
        self.log(f"Printer: {self.config.get('printer', {}).get('name', 'Not configured')}")
        self.log(f"Subscription: {self.subscription_status['message']}")
    
    def _show_subscription_expired_warning(self):
        """Show a modal warning when the subscription is not active."""
        messagebox.showwarning(
            "Subscription Expired",
            self.subscription_status['message'] + "\n\n"
            "Printing has been disabled. Please renew your subscription\n"
            "and update the expiry_date in config.json to continue."
        )

    def log(self, message):
        """Add message to console"""
        self.console.insert(tk.END, f"> {message}\n")
        self.console.see(tk.END)
        self.update()
    
    def load_excel_data(self):
        """Load card data from Excel file"""
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if filename:
            self.log(f"Loading data from: {filename}")
            try:
                # Temporarily update config with selected file
                original_file = self.config['excel']['data_file']
                self.config['excel']['data_file'] = filename
                
                self.card_data = read_card_data()
                
                if self.card_data:
                    self.card_listbox.delete(0, tk.END)
                    for idx, card in enumerate(self.card_data, 1):
                        name = card.get('Name', 'Unknown')
                        id_num = card.get('ID', '')
                        self.card_listbox.insert(tk.END, f"{idx}. {name} (ID: {id_num})")
                    
                    self.data_status_label.config(
                        text=f"✓ {len(self.card_data)} cards loaded",
                        fg='#00ff00'
                    )
                    self.log(f"Successfully loaded {len(self.card_data)} cards")
                else:
                    self.log("No card data found in file")
                    self.data_status_label.config(text="No data found", fg='#ff0000')
                
            except Exception as e:
                self.log(f"Error loading data: {e}")
                messagebox.showerror("Error", f"Failed to load data:\n{e}")
    
    def create_sample(self):
        """Create sample Excel file"""
        self.log("Creating sample Excel file...")
        create_sample_excel()
        self.log("Sample Excel created: card_data.xlsx")
        messagebox.showinfo("Success", "Sample Excel file created: card_data.xlsx")
    
    def on_card_select(self, event):
        """Handle card selection from list"""
        selection = self.card_listbox.curselection()
        if selection:
            idx = selection[0]
            self.preview_single_card(idx)
    
    def preview_single_card(self, idx):
        """Preview a single card"""
        if idx < len(self.card_data):
            self.log(f"Previewing card {idx + 1}")
            card_img = create_card_image(self.card_data[idx], self.config)
            self.display_preview(card_img)
    
    def preview_cards(self):
        """Preview cards in dual layout"""
        if not self.card_data:
            messagebox.showwarning("No Data", "Please load card data first")
            return
        
        self.log("Generating preview for 2-card layout...")
        
        # Preview first 2 cards
        card1 = self.card_data[0]
        card2 = self.card_data[1] if len(self.card_data) > 1 else None
        
        dual_img = create_dual_card_layout(card1, card2, self.config)
        self.display_preview(dual_img)
        self.log("Preview generated")
    
    def display_preview(self, pil_image):
        """Display PIL image in canvas"""
        # Resize to fit canvas
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            img_copy = pil_image.copy()
            img_copy.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
            
            self.current_preview = ImageTk.PhotoImage(img_copy)
            
            self.preview_canvas.delete("all")
            x = (canvas_width - self.current_preview.width()) // 2
            y = (canvas_height - self.current_preview.height()) // 2
            self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.current_preview)
    
    def print_all_cards(self):
        """Print all loaded cards"""
        if not self.subscription_status['active']:
            messagebox.showerror(
                "Subscription Expired",
                self.subscription_status['message']
            )
            return
        
        if not self.card_data:
            messagebox.showwarning("No Data", "Please load card data first")
            return
        
        response = messagebox.askyesno(
            "Confirm Print",
            f"Print {len(self.card_data)} cards?\n\n"
            f"This will print {(len(self.card_data) + 1) // 2} batches (2 cards per batch)"
        )
        
        if response:
            self.log("=" * 50)
            self.log("Starting print job...")
            
            # Run printing in separate thread to avoid freezing UI
            thread = threading.Thread(target=self.print_worker)
            thread.start()
    
    def print_worker(self):
        """Worker thread for printing"""
        try:
            print_cards(self.card_data, self.config)
            self.log("Print job completed successfully!")
            messagebox.showinfo("Success", "Cards printed successfully!")
        except Exception as e:
            self.log(f"Print error: {e}")
            messagebox.showerror("Error", f"Print failed:\n{e}")
    
    def run_alignment_test(self):
        """Run alignment test"""
        response = messagebox.askyesno(
            "Alignment Test",
            "This will print an alignment test pattern.\n\n"
            "Make sure you have blank PVC cards in the 2-card tray.\n\nContinue?"
        )
        
        if response:
            self.log("Running alignment test...")
            try:
                print_alignment_test(self.config)
                self.log("Alignment test completed")
                messagebox.showinfo(
                    "Test Complete",
                    "Check the printed cards:\n\n"
                    "- Do borders align with card edges?\n"
                    "- Are corner marks at corners?\n\n"
                    "Adjust config.json if needed."
                )
            except Exception as e:
                self.log(f"Alignment test error: {e}")
                messagebox.showerror("Error", str(e))
    
    def check_printer_status(self):
        """Check printer status"""
        printer_name = self.config.get('printer', {}).get('name', 'Unknown')
        self.log(f"Checking printer: {printer_name}")
        messagebox.showinfo(
            "Printer Status",
            f"Printer: {printer_name}\n\n"
            f"Check Windows Devices and Printers for status"
        )
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#2b2b2b')
        
        tk.Label(
            settings_window,
            text="Edit config.json for detailed settings",
            bg='#2b2b2b',
            fg='white',
            font=("Arial", 12)
        ).pack(pady=20)
        
        tk.Button(
            settings_window,
            text="Open config.json",
            command=lambda: os.startfile('config.json') if os.path.exists('config.json') else None,
            bg='#0078d4',
            fg='white'
        ).pack(pady=10)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "ID Card Printer\n"
            "Photoshop Bridge to Epson 4830\n\n"
            "Features:\n"
            "- 2-card tray support\n"
            "- Adobe color profiles\n"
            "- Alignment calibration\n"
            "- Excel integration\n\n"
            "Version 1.0"
        )


if __name__ == '__main__':
    app = PhotoshopBridgeInterface()
    app.mainloop()