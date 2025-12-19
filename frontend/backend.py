import networkx as nx
import folium
import webbrowser
import os
from math import radians, sin, cos, sqrt, atan2

class DisasterReliefSystem:
    def __init__(self):
        self.areas = {}
        self.roads = []
        self.G = nx.Graph()
        self.center_location = (28.6129, 77.2295)  # Default center (Delhi)
        
    def add_area(self, name, severity, lat, lon):
        """Add area with coordinates"""
        self.areas[name] = {'severity': severity, 'lat': lat, 'lon': lon, 'served': False}
        self.G.add_node(name, severity=severity, lat=lat, lon=lon, served=False)
    
    def add_road(self, from_area, to_area, distance):
        """Add road between areas"""
        self.roads.append((from_area, to_area, distance))
        self.G.add_edge(from_area, to_area, weight=distance)
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates using Haversine formula"""
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def dijkstra_shortest_path(self, start, target):
        """Dijkstra's algorithm for shortest path"""
        try:
            path = nx.dijkstra_path(self.G, start, target, weight='weight')
            distance = nx.dijkstra_path_length(self.G, start, target, weight='weight')
            return path, distance
        except:
            return None, float('inf')
    
    def allocate_relief(self):
        """Main relief allocation algorithm"""
        if not self.areas:
            return "Error: No areas added!"
        
        # Priority based on severity and distance from center
        priority_list = []
        
        for area_name, info in self.areas.items():
            # Calculate distance from center
            distance_from_center = self.calculate_distance(
                self.center_location[0], self.center_location[1],
                info['lat'], info['lon']
            )
            
            # Priority score: higher severity = higher priority
            # Lower distance = higher priority
            priority_score = info['severity'] * 10 - distance_from_center
            
            priority_list.append({
                'name': area_name,
                'severity': info['severity'],
                'distance': distance_from_center,
                'priority_score': priority_score,
                'lat': info['lat'],
                'lon': info['lon']
            })
        
        # Sort by priority score (descending)
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_list
    
    def generate_map(self, priority_list, shortest_path=None):
        """Generate interactive map with Folium"""
        # Create base map centered on average of all locations
        if self.areas:
            lats = [info['lat'] for info in self.areas.values()]
            lons = [info['lon'] for info in self.areas.values()]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
        else:
            center_lat, center_lon = self.center_location
        
        relief_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Add relief center marker
        folium.Marker(
            [self.center_location[0], self.center_location[1]],
            popup='Relief Center',
            tooltip='Relief Center',
            icon=folium.Icon(color='blue', icon='home', prefix='fa')
        ).add_to(relief_map)
        
        # Add area markers with color coding
        for i, area in enumerate(priority_list):
            # Determine color based on severity
            if area['severity'] >= 8:
                color = 'red'
                zone = 'Red Zone'
            elif area['severity'] >= 5:
                color = 'orange'
                zone = 'Yellow Zone'
            else:
                color = 'green'
                zone = 'Green Zone'
            
            # Add marker
            folium.Marker(
                [area['lat'], area['lon']],
                popup=f"""
                <b>{area['name']}</b><br>
                Severity: {area['severity']}<br>
                Zone: {zone}<br>
                Priority: {i+1}<br>
                Distance: {area['distance']:.1f} km
                """,
                tooltip=f"{area['name']} (Priority: {i+1})",
                icon=folium.Icon(color=color, icon='exclamation-triangle', prefix='fa')
            ).add_to(relief_map)
            
            # Add circle for zone visualization
            folium.Circle(
                location=[area['lat'], area['lon']],
                radius=area['severity'] * 500,  # Radius based on severity
                popup=f"{zone}: {area['name']}",
                color=color,
                fill=True,
                fillOpacity=0.2
            ).add_to(relief_map)
        
        # Add shortest path if provided
        if shortest_path and len(shortest_path) > 1:
            path_coordinates = []
            for area_name in shortest_path:
                if area_name in self.areas:
                    info = self.areas[area_name]
                    path_coordinates.append([info['lat'], info['lon']])
            
            folium.PolyLine(
                path_coordinates,
                color='blue',
                weight=5,
                opacity=0.7,
                popup='Shortest Relief Path'
            ).add_to(relief_map)
        
        # Save map
        map_file = "relief_map.html"
        relief_map.save(map_file)
        return map_file

def allocate_relief(input_file="input.txt"):
    """Main function to run relief allocation"""
    system = DisasterReliefSystem()
    
    try:
        with open(input_file, "r") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return "Error: input.txt not found!"
    
    mode = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line == "AREAS":
            mode = "areas"
            continue
        elif line == "ROADS":
            mode = "roads"
            continue
        elif line == "COORDINATES":
            mode = "coordinates"
            continue
            
        if mode == "areas":
            parts = line.split()
            if len(parts) >= 2:
                name = " ".join(parts[:-1])
                severity = int(parts[-1])
                # Default coordinates (will be updated if COORDINATES section exists)
                system.add_area(name, severity, 0, 0)
        
        elif mode == "coordinates":
            parts = line.split()
            if len(parts) >= 3:
                name = " ".join(parts[:-2])
                lat = float(parts[-2])
                lon = float(parts[-1])
                if name in system.areas:
                    system.areas[name]['lat'] = lat
                    system.areas[name]['lon'] = lon
        
        elif mode == "roads":
            parts = line.split()
            if len(parts) >= 3:
                from_area = parts[0]
                to_area = parts[1]
                distance = float(parts[2])
                system.add_road(from_area, to_area, distance)
    
    # Run allocation
    priority_list = system.allocate_relief()
    
    # Generate result text
    result = "=== DISASTER RELIEF ALLOCATION REPORT ===\n\n"
    result += "PRIORITY ORDER FOR RELIEF DISTRIBUTION:\n"
    result += "=" * 50 + "\n"
    
    for i, area in enumerate(priority_list):
        status = "🟥 RED ZONE" if area['severity'] >= 8 else \
                "🟨 YELLOW ZONE" if area['severity'] >= 5 else "🟩 GREEN ZONE"
        
        result += f"{i+1}. {area['name']}\n"
        result += f"   Severity: {area['severity']}/10 | {status}\n"
        result += f"   Distance from Center: {area['distance']:.1f} km\n"
        result += f"   Priority Score: {area['priority_score']:.1f}\n"
        result += "-" * 30 + "\n"
    
    # Generate map
    map_file = system.generate_map(priority_list)
    result += f"\n🗺️ Interactive map generated: {map_file}\n"
    
    return result, system, priority_list