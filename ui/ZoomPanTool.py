class ZoomPanTool:
    def __init__(self):
        self.zoom_level = 1.0
        self.zoom_min = 1.0
        self.zoom_max = 5.0
        self.zoom_step = 0.2
        self.pan_x = 0
        self.pan_y = 0
        self.panning = False
        self.last_pan_x = 0
        self.last_pan_y = 0
    
    def reset_zoom_pan(self):
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.panning = False
    
    def tem_zoom_ativo(self, zoom_level, pan_x, pan_y):
        #Verifica se há zoom ou pan ativo
        return zoom_level != 1.0 or pan_x != 0 or pan_y != 0
    
    def zoom_in(self):
        if self.zoom_level < self.zoom_max:
            self.zoom_level = min(self.zoom_level + self.zoom_step, self.zoom_max)
            return True
        return False
    
    def zoom_out(self):
        if self.zoom_level > self.zoom_min:
            self.zoom_level = max(self.zoom_level - self.zoom_step, self.zoom_min)
            return True
        return False
    
    def on_pan_start(self, event):
        self.panning = True
        self.last_pan_x = event.x
        self.last_pan_y = event.y
        return "fleur"
    
    def on_pan_move(self, event, graph_manager, canvas_width, canvas_height):
        if not self.panning:
            return False
        dx = event.x - self.last_pan_x
        dy = event.y - self.last_pan_y
        if graph_manager.eh_grafo_osm():
            nodes = list(graph_manager.grafo.nodes(data=True))
            xs = [data['x'] for _, data in nodes]
            ys = [data['y'] for _, data in nodes]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x, min_y, max_x, max_y = graph_manager.bbox or (0, 0, 900, 650)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        range_x = (max_x - min_x) / self.zoom_level
        range_y = (max_y - min_y) / self.zoom_level
        world_dx = (dx / (canvas_width - 40)) * range_x
        world_dy = (dy / (canvas_height - 40)) * range_y
        self.pan_x -= world_dx
        self.pan_y += world_dy
        self.last_pan_x = event.x
        self.last_pan_y = event.y
        return True
    
    def on_pan_end(self):
        self.panning = False
        return ""
    
    def on_mousewheel_zoom(self, event, graph_manager, canvas_width, canvas_height):
        if graph_manager.eh_grafo_osm():
            nodes = list(graph_manager.grafo.nodes(data=True))
            xs = [data['x'] for _, data in nodes]
            ys = [data['y'] for _, data in nodes]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x, min_y, max_x, max_y = graph_manager.bbox or (0, 0, 900, 650)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        range_x = (max_x - min_x) / self.zoom_level
        range_y = (max_y - min_y) / self.zoom_level
        mouse_offset_x = event.x - canvas_width / 2
        mouse_offset_y = event.y - canvas_height / 2
        world_offset_x = (mouse_offset_x / (canvas_width - 40)) * range_x
        world_offset_y = (mouse_offset_y / (canvas_height - 40)) * range_y
        zoom_in = event.delta > 0
        new_zoom = self.zoom_level + self.zoom_step if zoom_in else self.zoom_level - self.zoom_step
        new_zoom = max(self.zoom_min, min(new_zoom, self.zoom_max))
        if new_zoom == self.zoom_level:
            return False
        zoom_factor = new_zoom / self.zoom_level
        self.zoom_level = new_zoom
        if zoom_in:
            self.pan_x -= world_offset_x * (zoom_factor - 1)
            self.pan_y += world_offset_y * (zoom_factor - 1)
        else:
            self.pan_x += world_offset_x * (1 - zoom_factor)
            self.pan_y -= world_offset_y * (1 - zoom_factor)
        return True