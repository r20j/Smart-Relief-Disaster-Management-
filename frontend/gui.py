import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from math import radians, sin, cos, sqrt, atan2
import networkx as nx
import folium
import webbrowser

# Try to import matplotlib for graph
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Matplotlib not installed - Graph features disabled")

class DisasterReliefSystem:
    def __init__(self):
        self.areas = {}
        self.roads = []
        self.G = nx.Graph()
        self.center_location = (28.6129, 77.2295)  # Delhi
        
    def add_area(self, name, severity):
        """Add area with automatic coordinates"""
        # Automatic coordinates based on area count
        base_lat, base_lon = 28.6129, 77.2295
        lat_offset = (len(self.areas) % 4) * 0.08
        lon_offset = (len(self.areas) // 4) * 0.08
        
        lat = base_lat + lat_offset
        lon = base_lon + lon_offset
        
        self.areas[name] = {'severity': severity, 'lat': lat, 'lon': lon, 'served': False}
        self.G.add_node(name, severity=severity, lat=lat, lon=lon, served=False)
        return lat, lon
    
    def add_road(self, from_area, to_area, distance):
        self.roads.append((from_area, to_area, distance))
        self.G.add_edge(from_area, to_area, weight=distance)
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def dijkstra_shortest_path(self, start, target):
        try:
            path = nx.dijkstra_path(self.G, start, target, weight='weight')
            distance = nx.dijkstra_path_length(self.G, start, target, weight='weight')
            return path, distance
        except:
            return None, float('inf')
    
    def allocate_relief(self):
        if not self.areas:
            return "Error: No areas added!"
        
        # Add relief center
        self.G.add_node("Relief Center", severity=0, lat=self.center_location[0], 
                       lon=self.center_location[1], served=True)
        
        # Connect relief center to all areas
        for area_name, info in self.areas.items():
            distance_from_center = self.calculate_distance(
                self.center_location[0], self.center_location[1],
                info['lat'], info['lon']
            )
            self.G.add_edge("Relief Center", area_name, weight=distance_from_center)
        
        # Priority calculation
        priority_list = []
        for area_name, info in self.areas.items():
            distance_from_center = self.calculate_distance(
                self.center_location[0], self.center_location[1],
                info['lat'], info['lon']
            )
            
            priority_score = info['severity'] * 10 - (distance_from_center / 10)
            
            priority_list.append({
                'name': area_name,
                'severity': info['severity'],
                'distance': distance_from_center,
                'priority_score': priority_score,
                'lat': info['lat'],
                'lon': info['lon']
            })
        
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        return priority_list
    
    def create_graph_visualization(self):
        """Network graph create karta hai"""
        if not HAS_MATPLOTLIB or not self.areas:
            return None
            
        try:
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create position dictionary
            pos = {}
            node_colors = []
            node_sizes = []
            
            # Relief Center
            pos["Relief Center"] = (0, 0)
            node_colors.append('blue')
            node_sizes.append(1000)
            
            # Areas with positions based on coordinates
            for i, (name, info) in enumerate(self.areas.items()):
                # Convert lat/lon to x,y coordinates for graph
                x = (info['lon'] - 77.0) * 100
                y = (info['lat'] - 28.0) * 100
                pos[name] = (x, y)
                
                # Node color based on severity
                if info['severity'] >= 8:
                    node_colors.append('red')
                elif info['severity'] >= 5:
                    node_colors.append('orange')
                else:
                    node_colors.append('green')
                    
                node_sizes.append(800)
            
            # Draw the graph
            nx.draw_networkx_nodes(self.G, pos, node_color=node_colors, 
                                  node_size=node_sizes, alpha=0.8, ax=ax)
            nx.draw_networkx_edges(self.G, pos, edge_color='gray', 
                                  width=2, alpha=0.7, ax=ax)
            nx.draw_networkx_labels(self.G, pos, font_size=8, 
                                   font_weight='bold', ax=ax)
            
            # Edge labels (distances)
            edge_labels = nx.get_edge_attributes(self.G, 'weight')
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, 
                                       font_size=6, ax=ax)
            
            ax.set_title("Disaster Relief Network Graph\n🔴 High Severity (8-10)  🟠 Medium (5-7)  🟢 Low (1-4)  🔵 Relief Center", 
                        fontsize=12, fontweight='bold')
            ax.axis('off')
            ax.set_facecolor('#f8f9fa')
            fig.patch.set_facecolor('#f8f9fa')
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            print(f"Graph creation error: {e}")
            return None
    
    def generate_folium_map(self, priority_list):
        """Real Folium map generate karta hai"""
        try:
            if not self.areas:
                return None
                
            # Create base map with fixed location
            center_lat, center_lon = 28.6129, 77.2295  # Delhi
            
            # Simple Folium map
            relief_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=10,
                tiles='OpenStreetMap'
            )
            
            # Add relief center
            folium.Marker(
                [self.center_location[0], self.center_location[1]],
                popup='🏥 Relief Center',
                tooltip='Relief Center',
                icon=folium.Icon(color='blue', icon='home')
            ).add_to(relief_map)
            
            # Add area markers
            for i, area in enumerate(priority_list):
                if area['severity'] >= 8:
                    color = 'red'
                    icon_color = 'red'
                elif area['severity'] >= 5:
                    color = 'orange'
                    icon_color = 'orange'
                else:
                    color = 'green'
                    icon_color = 'green'
                
                folium.Marker(
                    [area['lat'], area['lon']],
                    popup=f"📍 {area['name']}<br>Severity: {area['severity']}/10<br>Priority: {i+1}",
                    tooltip=f"{area['name']} - Priority {i+1}",
                    icon=folium.Icon(color=icon_color, icon='info-sign')
                ).add_to(relief_map)
                
                # Add circle for zone
                folium.Circle(
                    location=[area['lat'], area['lon']],
                    radius=area['severity'] * 300,
                    popup=f"{area['name']} Zone",
                    color=color,
                    fill=True,
                    fillOpacity=0.2
                ).add_to(relief_map)
            
            # Add roads
            for from_area, to_area, distance in self.roads:
                if from_area in self.areas and to_area in self.areas:
                    from_lat, from_lon = self.areas[from_area]['lat'], self.areas[from_area]['lon']
                    to_lat, to_lon = self.areas[to_area]['lat'], self.areas[to_area]['lon']
                    
                    folium.PolyLine(
                        [[from_lat, from_lon], [to_lat, to_lon]],
                        color='blue',
                        weight=3,
                        opacity=0.7,
                        popup=f'Road: {from_area} ↔ {to_area} ({distance} km)'
                    ).add_to(relief_map)
            
            # Add legend as HTML
            legend_html = '''
            <div style="position: fixed; 
                        top: 10px; left: 10px; width: 220px; height: auto; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:12px; padding: 10px; border-radius: 5px;">
            <h4>🚑 Relief Map Legend</h4>
            <p>🔵 Relief Center</p>
            <p>🔴 Red Zone (Severity 8-10)</p>
            <p>🟠 Yellow Zone (Severity 5-7)</p>
            <p>🟢 Green Zone (Severity 1-4)</p>
            <p>🛣️ Blue Lines: Roads</p>
            </div>
            '''
            relief_map.get_root().html.add_child(folium.Element(legend_html))
            
            return relief_map
            
        except Exception as e:
            print(f"Map generation error: {e}")
            return None
    
    def save_map_to_file(self, map_obj, filename="relief_map.html"):
        """Map ko file mein save karta hai"""
        try:
            map_obj.save(filename)
            return os.path.abspath(filename)
        except Exception as e:
            print(f"Map save error: {e}")
            return None

class DisasterReliefApp:
    def __init__(self, root):
        self.root = root
        self.system = DisasterReliefSystem()
        self.current_map_path = None
        self.current_graph_fig = None
        self.setup_gui()
    
    def setup_gui(self):
        self.root.title("🗺️ Smart Disaster Relief - Graph + Map")
        self.root.geometry("1400x900")
        self.root.config(bg="#f0f4f7")
        
        # Header
        header = tk.Label(self.root, 
                         text="🚑 Smart Disaster Relief Resource Allocator", 
                         font=("Arial", 18, "bold"), 
                         bg="#f0f4f7",
                         fg="#2c3e50")
        header.pack(pady=10)
        
        # Create Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Input Data
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="📝 Input Data")
        self.setup_input_tab(input_frame)
        
        # Tab 2: Simulation Results
        result_frame = ttk.Frame(notebook)
        notebook.add(result_frame, text="📊 Results")
        self.setup_result_tab(result_frame)
        
        # Tab 3: Network Graph
        graph_frame = ttk.Frame(notebook)
        notebook.add(graph_frame, text="🕸️ Network Graph")
        self.setup_graph_tab(graph_frame)
        
        # Tab 4: Real Map
        map_frame = ttk.Frame(notebook)
        notebook.add(map_frame, text="🗺️ Live Map")
        self.setup_map_tab(map_frame)
    
    def setup_input_tab(self, parent):
        # Area Input Frame
        area_frame = tk.LabelFrame(parent, text="Add Affected Area", font=("Arial", 12, "bold"), 
                                  bg="#f0f4f7", padx=10, pady=10)
        area_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(area_frame, text="Area Name:", bg="#f0f4f7").grid(row=0, column=0, padx=5, pady=5)
        self.area_name_entry = tk.Entry(area_frame, width=20)
        self.area_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(area_frame, text="Severity (1-10):", bg="#f0f4f7").grid(row=0, column=2, padx=5, pady=5)
        self.severity_entry = tk.Entry(area_frame, width=10)
        self.severity_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Button(area_frame, text="Add Area", bg="#007bff", fg="white", 
                 command=self.add_area).grid(row=0, column=4, padx=10)
        
        # Road Input Frame
        road_frame = tk.LabelFrame(parent, text="Add Road Connection", font=("Arial", 12, "bold"), 
                                  bg="#f0f4f7", padx=10, pady=10)
        road_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(road_frame, text="From Area:", bg="#f0f4f7").grid(row=0, column=0, padx=5, pady=5)
        self.from_entry = tk.Entry(road_frame, width=15)
        self.from_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(road_frame, text="To Area:", bg="#f0f4f7").grid(row=0, column=2, padx=5, pady=5)
        self.to_entry = tk.Entry(road_frame, width=15)
        self.to_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(road_frame, text="Distance (km):", bg="#f0f4f7").grid(row=0, column=4, padx=5, pady=5)
        self.distance_entry = tk.Entry(road_frame, width=10)
        self.distance_entry.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Button(road_frame, text="Add Road", bg="#28a745", fg="white", 
                 command=self.add_road).grid(row=0, column=6, padx=10)
        
        # Control Buttons
        control_frame = tk.Frame(parent, bg="#f0f4f7")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(control_frame, text="▶ Run Simulation", bg="#ff6f00", fg="white",
                 font=("Arial", 11, "bold"), command=self.run_simulation).pack(side="left", padx=5)
        tk.Button(control_frame, text="🗑️ Clear All", bg="#dc3545", fg="white",
                 command=self.clear_all).pack(side="left", padx=5)
        
        # Data Display
        data_frame = tk.LabelFrame(parent, text="Current Data", font=("Arial", 12, "bold"), 
                                  bg="#f0f4f7", padx=10, pady=10)
        data_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Areas list
        tk.Label(data_frame, text="Areas:", font=("Arial", 10, "bold"), bg="#f0f4f7").pack(anchor="w")
        self.areas_text = tk.Text(data_frame, height=6, width=80)
        self.areas_text.pack(fill="x", pady=5)
        
        # Roads list
        tk.Label(data_frame, text="Roads:", font=("Arial", 10, "bold"), bg="#f0f4f7").pack(anchor="w")
        self.roads_text = tk.Text(data_frame, height=4, width=80)
        self.roads_text.pack(fill="x", pady=5)
        
        self.update_data_display()
    
    def setup_result_tab(self, parent):
        # Results display
        result_header = tk.Label(parent, text="Relief Allocation Results", 
                                font=("Arial", 14, "bold"), bg="#f0f4f7")
        result_header.pack(pady=10)
        
        self.result_text = tk.Text(parent, height=20, width=90, font=("Consolas", 10))
        self.result_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Result buttons
        btn_frame = tk.Frame(parent, bg="#f0f4f7")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(btn_frame, text="📍 Show Shortest Path", bg="#17a2b8", fg="white",
                 command=self.show_shortest_path).pack(side="left", padx=5)
        
        # ✅ "Generate Graph" button - Always show, even if matplotlib not installed
        self.graph_btn = tk.Button(btn_frame, text="🕸️ Generate Graph", bg="#28a745", fg="white",
                 command=self.generate_graph)
        self.graph_btn.pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="🗺️ Generate Map", bg="#6f42c1", fg="white",
                 command=self.generate_map).pack(side="left", padx=5)
    
    def setup_graph_tab(self, parent):
        # Graph display frame
        graph_header = tk.Label(parent, text="Network Graph Visualization", 
                               font=("Arial", 14, "bold"), bg="#f0f4f7")
        graph_header.pack(pady=10)
        
        if not HAS_MATPLOTLIB:
            warning_label = tk.Label(parent, 
                                   text="⚠️ Matplotlib not installed!\n\n"
                                        "To view network graph, please install:\n"
                                        "pip install matplotlib\n\n"
                                        "For now, check the Live Map tab for visualization.",
                                   font=("Arial", 12), bg="#f0f4f7", fg="red", justify="center")
            warning_label.pack(expand=True)
            return
        
        # Graph display area
        self.graph_display_frame = tk.Frame(parent, bg="white", relief="sunken", bd=2)
        self.graph_display_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Initial message
        self.graph_label = tk.Label(self.graph_display_frame, 
                                   text="Run simulation and click 'Generate Graph' to view network graph", 
                                   font=("Arial", 12), bg="white", fg="gray")
        self.graph_label.pack(expand=True)
    
    def setup_map_tab(self, parent):
        # Map display frame
        map_header = tk.Label(parent, text="Real-Time Disaster Relief Map", 
                             font=("Arial", 14, "bold"), bg="#f0f4f7")
        map_header.pack(pady=10)
        
        # Map control buttons
        map_control_frame = tk.Frame(parent, bg="#f0f4f7")
        map_control_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(map_control_frame, text="🗺️ Generate Map", bg="#007bff", fg="white",
                 command=self.generate_map).pack(side="left", padx=5)
        tk.Button(map_control_frame, text="📱 Open in Browser", bg="#28a745", fg="white",
                 command=self.open_map_in_browser).pack(side="left", padx=5)
        
        # Map display area
        self.map_display_frame = tk.Frame(parent, bg="white", relief="sunken", bd=2)
        self.map_display_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Initial map message
        self.map_message = tk.Label(self.map_display_frame, 
                                   text="Click 'Generate Map' to create interactive map\n\n"
                                        "📍 Real Folium Map Features:\n"
                                        "• Zoom In/Out with mouse wheel\n"
                                        "• Drag to pan around\n" 
                                        "• Click markers for area info\n"
                                        "• Color-coded zones (Red/Yellow/Green)\n"
                                        "• Road connections shown",
                                   font=("Arial", 11), bg="white", fg="gray", justify="left")
        self.map_message.pack(expand=True)
    
    def add_area(self):
        name = self.area_name_entry.get().strip()
        severity = self.severity_entry.get().strip()
        
        if not name or not severity:
            messagebox.showwarning("Input Error", "Please enter Area Name and Severity")
            return
        
        try:
            severity_val = int(severity)
            if not (1 <= severity_val <= 10):
                messagebox.showwarning("Input Error", "Severity must be between 1-10")
                return
                
            # Auto-generate coordinates
            lat, lon = self.system.add_area(name, severity_val)
            messagebox.showinfo("Success", f"Area '{name}' added!\nAuto-located at: ({lat:.4f}, {lon:.4f})")
            
            # Clear entries
            self.area_name_entry.delete(0, tk.END)
            self.severity_entry.delete(0, tk.END)
            
            self.update_data_display()
            
        except ValueError:
            messagebox.showerror("Input Error", "Severity must be a number")
    
    def add_road(self):
        from_area = self.from_entry.get().strip()
        to_area = self.to_entry.get().strip()
        distance = self.distance_entry.get().strip()
        
        if not all([from_area, to_area, distance]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return
        
        if from_area not in self.system.areas or to_area not in self.system.areas:
            messagebox.showerror("Error", "Both areas must be added first")
            return
        
        try:
            distance_val = float(distance)
            self.system.add_road(from_area, to_area, distance_val)
            messagebox.showinfo("Success", f"Road {from_area} ↔ {to_area} added!")
            
            self.from_entry.delete(0, tk.END)
            self.to_entry.delete(0, tk.END)
            self.distance_entry.delete(0, tk.END)
            
            self.update_data_display()
            
        except ValueError:
            messagebox.showerror("Input Error", "Distance must be a number")
    
    def update_data_display(self):
        self.areas_text.delete(1.0, tk.END)
        self.roads_text.delete(1.0, tk.END)
        
        # Display areas
        for name, info in self.system.areas.items():
            zone = "🔴 RED" if info['severity'] >= 8 else "🟠 YELLOW" if info['severity'] >= 5 else "🟢 GREEN"
            self.areas_text.insert(tk.END, 
                                  f"• {name}: Severity {info['severity']} ({zone}) | "
                                  f"Location: ({info['lat']:.4f}, {info['lon']:.4f})\n")
        
        # Display roads
        for from_area, to_area, dist in self.system.roads:
            self.roads_text.insert(tk.END, f"• {from_area} ↔ {to_area}: {dist} km\n")
    
    def run_simulation(self):
        if not self.system.areas:
            messagebox.showwarning("Error", "Please add areas first")
            return
        
        try:
            self.priority_list = self.system.allocate_relief()
            
            # Generate results
            result = "=== DISASTER RELIEF ALLOCATION REPORT ===\n\n"
            result += "PRIORITY ORDER FOR RELIEF DISTRIBUTION:\n"
            result += "=" * 50 + "\n"
            
            for i, area in enumerate(self.priority_list):
                status = "🔴 RED ZONE" if area['severity'] >= 8 else \
                        "🟠 YELLOW ZONE" if area['severity'] >= 5 else "🟢 GREEN ZONE"
                
                result += f"{i+1}. {area['name']}\n"
                result += f"   Severity: {area['severity']}/10 | {status}\n"
                result += f"   Distance from Center: {area['distance']:.1f} km\n"
                result += f"   Priority Score: {area['priority_score']:.1f}\n"
                
                # Show shortest path
                path, dist = self.system.dijkstra_shortest_path("Relief Center", area['name'])
                if path:
                    result += f"   Shortest Path: {' → '.join(path)}\n"
                    result += f"   Path Distance: {dist:.1f} km\n"
                result += "-" * 40 + "\n"
            
            result += f"\n✅ Simulation completed! Check Graph and Map tabs for visualization.\n"
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
            
            # ✅ AUTO-GENERATE GRAPH
            if HAS_MATPLOTLIB:
                self.generate_graph()
            
            messagebox.showinfo("Success", "Simulation completed!\n\nNow you can:\n• View Network Graph tab\n• Generate interactive Map\n• See shortest paths")
            
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
    
    def generate_graph(self):
        """Network graph generate karta hai"""
        if not HAS_MATPLOTLIB:
            messagebox.showwarning("Matplotlib Required", 
                                  "Please install matplotlib to view graphs:\n\n"
                                  "pip install matplotlib\n\n"
                                  "After installation, restart the application.")
            return
        
        if not hasattr(self, 'priority_list') or not self.priority_list:
            messagebox.showwarning("Error", "Please run simulation first")
            return
        
        try:
            # Clear previous graph
            for widget in self.graph_display_frame.winfo_children():
                widget.destroy()
            
            # Create new graph
            fig = self.system.create_graph_visualization()
            if fig:
                canvas = FigureCanvasTkAgg(fig, self.graph_display_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
                
                # Store reference
                self.current_graph_fig = fig
                messagebox.showinfo("Success", "Network graph generated!")
            else:
                error_label = tk.Label(self.graph_display_frame, 
                                      text="Failed to generate graph", 
                                      font=("Arial", 12), bg="white", fg="red")
                error_label.pack(expand=True)
                
        except Exception as e:
            error_label = tk.Label(self.graph_display_frame, 
                                  text=f"Graph Error: {str(e)}", 
                                  font=("Arial", 12), bg="white", fg="red")
            error_label.pack(expand=True)
    
    def generate_map(self):
        """Map generate karta hai"""
        if not hasattr(self, 'priority_list') or not self.priority_list:
            messagebox.showwarning("Error", "Please run simulation first")
            return
        
        try:
            # Generate Folium map
            folium_map = self.system.generate_folium_map(self.priority_list)
            
            if folium_map:
                # Save map to file
                map_path = self.system.save_map_to_file(folium_map, "relief_map.html")
                self.current_map_path = map_path
                
                if map_path:
                    # Update map message
                    for widget in self.map_display_frame.winfo_children():
                        widget.destroy()
                    
                    success_label = tk.Label(self.map_display_frame, 
                                           text="✅ Map Generated Successfully!\n\n"
                                                "Click 'Open in Browser' to view interactive map\n\n"
                                                "🗺️ Map Features:\n"
                                                "• Real OpenStreetMap\n"
                                                "• Zoom with mouse wheel\n"
                                                "• Drag to pan\n"
                                                "• Click markers for info\n"
                                                "• Color-coded zones\n"
                                                "• Road connections",
                                           font=("Arial", 11), bg="white", justify="left")
                    success_label.pack(expand=True)
                    
                    messagebox.showinfo("Success", 
                                      "🎉 Map Generated!\n\n"
                                      "Click 'Open in Browser' to view the interactive map.")
                else:
                    messagebox.showerror("Error", "Failed to save map file")
            else:
                messagebox.showerror("Error", "Failed to generate map")
                
        except Exception as e:
            messagebox.showerror("Error", f"Map generation failed: {str(e)}")
    
    def open_map_in_browser(self):
        """Map ko browser mein open karta hai"""
        if self.current_map_path and os.path.exists("relief_map.html"):
            webbrowser.open('file://' + os.path.abspath("relief_map.html"))
        else:
            messagebox.showwarning("Error", "Map not found. Please generate map first.")
    
    def show_shortest_path(self):
        if not hasattr(self, 'priority_list') or not self.priority_list:
            messagebox.showwarning("Error", "Please run simulation first")
            return
        
        target = self.priority_list[0]['name']
        path, distance = self.system.dijkstra_shortest_path("Relief Center", target)
        
        if path:
            path_str = " → ".join(path)
            messagebox.showinfo("Shortest Path", 
                              f"To {target}:\nPath: {path_str}\nDistance: {distance:.1f} km")
        else:
            messagebox.showwarning("Path Error", "No path found to target area")
    
    def clear_all(self):
        self.system = DisasterReliefSystem()
        self.update_data_display()
        self.result_text.delete(1.0, tk.END)
        
        # Clear graph
        if HAS_MATPLOTLIB:
            for widget in self.graph_display_frame.winfo_children():
                widget.destroy()
            self.graph_label = tk.Label(self.graph_display_frame, 
                                       text="Run simulation and click 'Generate Graph' to view network graph", 
                                       font=("Arial", 12), bg="white", fg="gray")
            self.graph_label.pack(expand=True)
        
        # Clear map
        for widget in self.map_display_frame.winfo_children():
            widget.destroy()
        self.map_message = tk.Label(self.map_display_frame, 
                                   text="Click 'Generate Map' to create interactive map", 
                                   font=("Arial", 11), bg="white", fg="gray")
        self.map_message.pack(expand=True)
        
        messagebox.showinfo("Cleared", "All data cleared!")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = DisasterReliefApp(root)
    root.mainloop()