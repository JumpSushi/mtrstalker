from script.api import MTRAPI
import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from ttkthemes import ThemedTk

class mtrstalker:
    def __init__(self):
        self.STATION_SPACING = 90  
        self.MAP_MARGIN = 70      
        self.MAP_HEIGHT = 200     
        
        self.api = MTRAPI()
        self.root = ThemedTk(theme="arc")
        self.root.title("MTR Stalker (not really)")
        self.root.geometry("1400x800")
        self.sort_columns = {
            "station": True,
            "platform": True,
            "arrival": True,
            "minutes": True,
        }
        # Initialize map-related variables before setup_gui
        self.station_positions = {}
        self.map_canvas = None
        
        self.setup_gui()
        self.update_thread = None
        self.running = True
        self.last_update = 0
        self.update_interval = 5
        self.map_update_interval = 100 
        self.continuous_update = True
        self.current_up_trains = []
        self.current_down_trains = []

    def setup_gui(self):
        # Make main container expandable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        main_container = ttk.Frame(self.root, padding="20")
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # Make rows expandable
        main_container.grid_rowconfigure(1, weight=3)
        main_container.grid_rowconfigure(2, weight=1) 
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)

        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 24, "bold"), padding=10)
        style.configure("Subtitle.TLabel", font=("Helvetica", 12), padding=5)
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("Direction.TLabelframe", padding=10)

        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        title = ttk.Label(title_frame, text="MTR KTL Stalker",
                          style="Title.TLabel")
        title.pack()

        self.time_label = ttk.Label(title_frame, text="", style="Subtitle.TLabel")
        self.time_label.pack()

        up_frame = ttk.LabelFrame(main_container, text="→ Tiu Keng Leng (UP)", style="Direction.TLabelframe")
        up_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        down_frame = ttk.LabelFrame(main_container, text="→ Whampoa (DOWN)", style="Direction.TLabelframe")
        down_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        self.up_trains_display = ttk.Treeview(
            up_frame,
            columns=("station", "platform", "arrival", "minutes"),
            show="headings",
            height=20
        )
        self.down_trains_display = ttk.Treeview(
            down_frame,
            columns=("station", "platform", "arrival", "minutes"),
            show="headings",
            height=20
        )

        for tree in (self.up_trains_display, self.down_trains_display):
            for col in ("station", "platform", "arrival", "minutes"):
                tree.heading(col, text=col.title(),
                           command=lambda c=col, t=tree: self.sort_treeview(t, c))

            tree.column("station", width=200)
            tree.column("platform", width=100)
            tree.column("arrival", width=150)
            tree.column("minutes", width=100)

            tree.tag_configure('oddrow', background='#EFEFEF')
            tree.tag_configure('evenrow', background='#FFFFFF')

        for tree, frame in [(self.up_trains_display, up_frame), (self.down_trains_display, down_frame)]:
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y", pady=5)

        # Update map frame to be expandable
        map_frame = ttk.LabelFrame(main_container, text="Line Map", style="Direction.TLabelframe")
        map_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")
        
        # Make canvas responsive
        canvas_width = max(
            (len(self.api.STATION_NAMES) * self.STATION_SPACING) + (2 * self.MAP_MARGIN),
            800  # Minimum width
        )
        
        # Create canvas for map
        self.map_canvas = tk.Canvas(
            map_frame, 
            height=self.MAP_HEIGHT,
            width=canvas_width,
            bg='white'
        )
        self.map_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Bind resize event
        self.root.bind('<Configure>', self._on_window_resize)
        
        # Initialize station positions
        self._setup_map()

    def _setup_map(self):
        stations = list(self.api.STATION_NAMES.keys())
        
        self.map_canvas.create_line(
            self.MAP_MARGIN, self.MAP_HEIGHT/2,
            self.MAP_MARGIN + (len(stations)-1) * self.STATION_SPACING, self.MAP_HEIGHT/2,
            width=5, fill='#2ecc71',  # Bright green color
            tags="main_line"
        )
        
        # Add color key
        key_y = 30
        for color, label in [
            ('orange', 'Both Directions'),
            ('green', 'Up Train'),
            ('blue', 'Down Train'),
            ('white', 'No Trains')
        ]:
            # Draw key circle
            self.map_canvas.create_oval(
                10, key_y-8, 26, key_y+8,
                fill=color,
                outline='black',
                width=2
            )
            # Add label
            self.map_canvas.create_text(
                35, key_y,
                text=label,
                anchor='w',
                font=('Helvetica', 10)
            )
            key_y += 30
        
        # Draw stations and labels
        for i, station_code in enumerate(stations):
            x = self.MAP_MARGIN + (i * self.STATION_SPACING)
            self.station_positions[station_code] = x
            self.map_canvas.create_oval(
                x-8, (self.MAP_HEIGHT/2)-8,
                x+8, (self.MAP_HEIGHT/2)+8,
                fill='white',
                outline='black',
                width=2,
                tags=f"station_{station_code}"
            )
            
            # Larger, more readable station labels
            self.map_canvas.create_text(
                x, (self.MAP_HEIGHT/2)+30,
                text=self.api.STATION_NAMES[station_code],
                angle=45,
                anchor='w',
                font=('Helvetica', 10, 'bold'),
                tags="station_label"
            )

    def _update_map(self, up_trains, down_trains):
        """update train pos"""
        if not hasattr(self, 'station_positions') or not self.station_positions:
            return
            
        # Reset all stations to white
        for station_code in self.station_positions:
            station_items = self.map_canvas.find_withtag(f"station_{station_code}")
            for item in station_items:
                self.map_canvas.itemconfig(item, fill='white')
            
        # Track stations with trains
        stations_with_trains = {}
        
        # Process trains - only include trains with 0 minutes arrival time
        for train, direction in [(t, 'up') for t in (up_trains or [])] + [(t, 'down') for t in (down_trains or [])]:
            try:
                # Only process trains that have arrived (0 minutes)
                if int(train.get('minutes', '99')) != 0:  
                    continue
                    
                station = next((code for code, name in self.api.STATION_NAMES.items() 
                             if name == train['current_station']), None)
                if station:
                    if station in stations_with_trains:
                        stations_with_trains[station].append(direction)
                    else:
                        stations_with_trains[station] = [direction]
            except (KeyError, AttributeError):
                continue
        
        # Update station colors
        for station, trains in stations_with_trains.items():
            color = 'orange' if set(trains) == {'up', 'down'} else \
                   'green' if 'up' in trains else 'blue'
            
            station_items = self.map_canvas.find_withtag(f"station_{station}")
            for item in station_items:
                self.map_canvas.itemconfig(item, fill=color)

    def sort_treeview(self, tree: ttk.Treeview, col: str):
        items = [(tree.set(item, col), item) for item in tree.get_children('')]
        items.sort(reverse=self.sort_columns[col])

        for index, (_, item) in enumerate(items):
            tree.move(item, '', index)
            tree.tag_configure(item, tags=('evenrow' if index % 2 == 0 else 'oddrow',))

        self.sort_columns[col] = not self.sort_columns[col]

    def update_display(self, trains):
        if trains is None:
            return
            
        current_time = time.time()
        if current_time - self.last_update < 1:  # Debounce updates
            return
        self.last_update = current_time
        
        # Batch delete operations
        self.root.after(0, self._clear_displays)
        
        # Prepare data before updating UI
        up_trains = sorted([t for t in trains if t["direction"] == "UP"], 
                         key=lambda x: int(x["sequence"] or 999))
        down_trains = sorted([t for t in trains if t["direction"] == "DOWN"], 
                           key=lambda x: int(x["sequence"] or 999))
        
        # Batch insert operations
        self.root.after(0, self._update_displays, up_trains, down_trains)
        
    def _clear_displays(self):
        self.up_trains_display.delete(*self.up_trains_display.get_children())
        self.down_trains_display.delete(*self.down_trains_display.get_children())
        
    def _update_displays(self, up_trains, down_trains):
        # Store current trains for click handling
        self.current_up_trains = up_trains
        self.current_down_trains = down_trains
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.config(text=f"Last Updated: {current_time}")
        
        for i, train in enumerate(up_trains):
            self._insert_train(self.up_trains_display, train, i)
            
        for i, train in enumerate(down_trains):
            self._insert_train(self.down_trains_display, train, i)

        self._update_map(up_trains, down_trains)
        
        # Bind click events to train indicators
        for item in self.map_canvas.find_withtag("train"):
            self.map_canvas.tag_bind(item, '<Button-1>', self._show_train_info)
        
        if self.continuous_update:
            self.root.after(self.map_update_interval, 
                          lambda: self._continuous_map_update(up_trains, down_trains))

    def _continuous_map_update(self, up_trains, down_trains):
        if not self.continuous_update:
            return
            
        self._update_map(up_trains, down_trains)
        if self.running:
            self.root.after(self.map_update_interval, 
                          lambda: self._continuous_map_update(up_trains, down_trains))

    def _insert_train(self, tree, train, index):
        tree.insert("", "end", 
                   values=(train["current_station"], 
                          f"Platform {train['platform']}", 
                          train["arrival_time"].split()[1], 
                          f"{train['minutes']} min"),
                   tags=('evenrow' if index % 2 == 0 else 'oddrow',))

    def _show_train_info(self, event):
        x, y = event.x, event.y
        items = self.map_canvas.find_overlapping(x-10, y-10, x+10, y+10)
        
        for item in items:
            if "train" in self.map_canvas.gettags(item):
                # Find which station this train is at
                closest_station = min(
                    self.station_positions.items(),
                    key=lambda p: abs(p[1] - x)
                )[0]
                
                # Get train info
                train_info = []
                for train_list in [self.current_up_trains, self.current_down_trains]:
                    for train in train_list:
                        if train["current_station"] == self.api.STATION_NAMES[closest_station]:
                            train_info.append(
                                f"Direction: {train['direction']}\n"
                                f"Platform: {train['platform']}\n"
                                f"Arrival: {train['arrival_time'].split()[1]}\n"
                                f"Minutes: {train['minutes']}"
                            )
                
                if train_info:
                    # Show popup with train information
                    info_window = tk.Toplevel(self.root)
                    info_window.title("Train Information")
                    info_window.geometry("200x150")
                    
                    for info in train_info:
                        ttk.Label(
                            info_window,
                            text=info,
                            padding=10,
                            justify='left'
                        ).pack(fill='x')
                    
                    # Position popup near click
                    info_window.geometry(f"+{event.x_root}+{event.y_root}")

    def _on_window_resize(self, event):

        if event.widget == self.root:
            # Minimum sizes to prevent cramping
            min_width = 1000
            min_height = 600
            
            new_width = max(event.width, min_width)
            new_height = max(event.height, min_height)
            
            # Update canvas size
            canvas_width = max(
                (len(self.api.STATION_NAMES) * self.STATION_SPACING) + (2 * self.MAP_MARGIN),
                new_width - 40  # Account for padding
            )
            self.map_canvas.configure(width=canvas_width)
            
            # Redraw map
            self.map_canvas.delete("all")
            self._setup_map()
            self._update_map(self.current_up_trains or [], self.current_down_trains or [])

    def update_loop(self):
        while self.running:
            try:
                trains = self.api.get_ALL_trains()
                self.root.after(0, self.update_display, trains)
            except Exception as e:
                print(f"Error getting train data: {e}")
            time.sleep(1)

    def start(self):
        self.continuous_update = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        self.root.mainloop()
        self.running = False
        self.continuous_update = False
        if self.update_thread:
            self.update_thread.join(timeout=1)

def main():
    app = mtrstalker()
    app.start()

if __name__ == "__main__":
    main()