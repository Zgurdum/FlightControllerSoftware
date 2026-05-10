"""
3D Drone Visualizer - Embedded in tkinter
Real-time 3D visualization of drone orientation based on gyroscope data.
Embedded directly in tkinter GUI for smooth, responsive interaction.
"""

import queue
import numpy as np
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

MATPLOTLIB_AVAILABLE = False
_MATPLOTLIB_IMPORT_ATTEMPTED = False

def _ensure_matplotlib():
    """Check if matplotlib is available."""
    global MATPLOTLIB_AVAILABLE, _MATPLOTLIB_IMPORT_ATTEMPTED
    
    if _MATPLOTLIB_IMPORT_ATTEMPTED:
        return MATPLOTLIB_AVAILABLE
    
    _MATPLOTLIB_IMPORT_ATTEMPTED = True
    
    try:
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        MATPLOTLIB_AVAILABLE = True
        return True
    except Exception as e:
        logger.warning(f"Matplotlib not available: {e}")
        return False



class DroneVisualizer:
    """3D drone orientation visualizer embedded in tkinter."""
    
    def __init__(self, parent_frame=None, queue_size=100):
        """Initialize visualizer.
        
        Args:
            parent_frame: tkinter frame to embed in (optional)
            queue_size: Maximum queue size for gyro data
        """
        self.data_queue = queue.Queue(maxsize=queue_size)
        self.parent_frame = parent_frame
        self.running = False
        self.canvas = None
        self.figure = None
        self.ax = None
        
        # Euler angles
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        
        # Gyro scaling
        self.gyro_scale = (np.pi / 180.0) / 60.0
        
        self.update_count = 0
        
    def create_embedded_view(self, parent_frame) -> Optional[Any]:
        """Create embedded matplotlib figure in tkinter frame.
        
        Args:
            parent_frame: tkinter Frame to embed visualization in
            
        Returns:
            Canvas widget or None if creation failed
        """
        if not _ensure_matplotlib():
            logger.error("Matplotlib not available")
            return None
        
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
            
            # Create figure
            self.figure = Figure(figsize=(8, 8), facecolor='#1c1c1c', dpi=100)
            self.figure.suptitle("Drone 3D Orientation", fontsize=12, color='white', weight='bold')
            
            self.ax = self.figure.add_subplot(111, projection='3d')
            self.ax.set_facecolor('#0a0a0a')
            
            # Configure axes
            self.ax.xaxis.pane.fill = False
            self.ax.yaxis.pane.fill = False
            self.ax.zaxis.pane.fill = False
            self.ax.xaxis.pane.set_edgecolor('#333333')
            self.ax.yaxis.pane.set_edgecolor('#333333')
            self.ax.zaxis.pane.set_edgecolor('#333333')
            self.ax.grid(True, alpha=0.2, color='white')
            
            self.ax.set_xlim([-1.2, 1.2])
            self.ax.set_ylim([-1.2, 1.2])
            self.ax.set_zlim([-1.2, 1.2])
            self.ax.set_xlabel('X', fontsize=10, color='white')
            self.ax.set_ylabel('Y', fontsize=10, color='white')
            self.ax.set_zlabel('Z', fontsize=10, color='white')
            self.ax.tick_params(colors='white', labelsize=8)
            
            # Static world axes
            self.ax.quiver(0, 0, 0, 0.8, 0, 0, color='#ff4444', arrow_length_ratio=0.2, linewidth=1.5, alpha=0.4)
            self.ax.quiver(0, 0, 0, 0, 0.8, 0, color='#44ff44', arrow_length_ratio=0.2, linewidth=1.5, alpha=0.4)
            self.ax.quiver(0, 0, 0, 0, 0, 0.8, color='#4444ff', arrow_length_ratio=0.2, linewidth=1.5, alpha=0.4)
            
            # Create canvas
            self.canvas = FigureCanvasTkAgg(self.figure, master=parent_frame)
            self.canvas.draw()
            
            widget = self.canvas.get_tk_widget()
            widget.pack(fill='both', expand=True)
            
            self.running = True
            logger.info("Embedded visualizer created")
            return widget
            
        except Exception as e:
            logger.error(f"Failed to create embedded view: {e}")
            return None
    
    def start(self):
        """Start update loop (for compatibility)."""
        if not self.running:
            self.running = True
        return True
    
    def stop(self):
        """Stop visualizer."""
        self.running = False
        if self.canvas:
            try:
                self.canvas.get_tk_widget().destroy()
            except:
                pass
    
    def send_gyro_data(self, gyro_data: Dict[str, float]):
        """Queue gyroscope data."""
        if self.running:
            try:
                self.data_queue.put_nowait(gyro_data)
            except queue.Full:
                pass
    
    def update(self):
        """Update visualization (call periodically from GUI update loop)."""
        if not self.running or not self.ax:
            return
        
        # Process all queued gyro data
        try:
            while True:
                gyro = self.data_queue.get_nowait()
                self.roll += gyro.get('x', 0) * self.gyro_scale
                self.pitch += gyro.get('y', 0) * self.gyro_scale
                self.yaw += gyro.get('z', 0) * self.gyro_scale
        except queue.Empty:
            pass
        
        self.update_count += 1
        
        # Update plot every 3 calls (smoother than every frame)
        if self.update_count % 3 == 0:
            ax = self.ax
            ax.clear()
            
            # World axes
            ax.quiver(0, 0, 0, 0.8, 0, 0, color='#ff4444', arrow_length_ratio=0.2, linewidth=1.5, alpha=0.4)
            ax.quiver(0, 0, 0, 0, 0.8, 0, color='#44ff44', arrow_length_ratio=0.2, linewidth=1.5, alpha=0.4)
            ax.quiver(0, 0, 0, 0, 0, 0.8, color='#4444ff', arrow_length_ratio=0.2, linewidth=1.5, alpha=0.4)
            
            drone_frame = self._get_rotated_frame()
            
            # Drone axes (bright)
            ax.quiver(0, 0, 0, drone_frame[0, 0]*0.8, drone_frame[0, 1]*0.8, drone_frame[0, 2]*0.8,
                     color='#ff1111', arrow_length_ratio=0.2, linewidth=3)
            ax.quiver(0, 0, 0, drone_frame[1, 0]*0.8, drone_frame[1, 1]*0.8, drone_frame[1, 2]*0.8,
                     color='#11ff11', arrow_length_ratio=0.2, linewidth=3)
            ax.quiver(0, 0, 0, drone_frame[2, 0]*0.8, drone_frame[2, 1]*0.8, drone_frame[2, 2]*0.8,
                     color='#1111ff', arrow_length_ratio=0.2, linewidth=3)
            
            self._draw_quadcopter_frame(ax, drone_frame)
            
            ax.set_xlim([-1.2, 1.2])
            ax.set_ylim([-1.2, 1.2])
            ax.set_zlim([-1.2, 1.2])
            ax.set_xlabel('X', fontsize=10, color='white')
            ax.set_ylabel('Y', fontsize=10, color='white')
            ax.set_zlabel('Z', fontsize=10, color='white')
            ax.tick_params(colors='white', labelsize=8)
            ax.grid(True, alpha=0.2, color='white')
            
            # Angle display
            angle_text = (
                f"Roll: {np.degrees(self.roll):6.1f}°  "
                f"Pitch: {np.degrees(self.pitch):6.1f}°  "
                f"Yaw: {np.degrees(self.yaw):6.1f}°"
            )
            ax.text2D(0.02, 0.95, angle_text, transform=ax.transAxes,
                     fontsize=10, verticalalignment='top', color='#00ff00',
                     family='monospace', weight='bold',
                     bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8, 
                             edgecolor='#00ff00'))
            
            self.figure.canvas.draw_idle()
    
    def _get_rotated_frame(self) -> np.ndarray:
        """Get rotation matrix from Euler angles."""
        # Z-Y-X rotation order (yaw-pitch-roll)
        Rz = np.array([
            [np.cos(self.yaw), -np.sin(self.yaw), 0],
            [np.sin(self.yaw),  np.cos(self.yaw), 0],
            [0,                  0,                1]
        ])
        
        Ry = np.array([
            [np.cos(self.pitch),  0, np.sin(self.pitch)],
            [0,                   1, 0],
            [-np.sin(self.pitch), 0, np.cos(self.pitch)]
        ])
        
        Rx = np.array([
            [1, 0,                  0],
            [0, np.cos(self.roll), -np.sin(self.roll)],
            [0, np.sin(self.roll),  np.cos(self.roll)]
        ])
        
        return Rz @ Ry @ Rx
    
    def _draw_quadcopter_frame(self, ax, rotation_matrix: np.ndarray):
        """Draw quadcopter model."""
        arm_length = 0.6
        
        motors_body = np.array([
            [arm_length * np.cos(np.pi/4),  arm_length * np.sin(np.pi/4), 0],
            [-arm_length * np.cos(np.pi/4), -arm_length * np.sin(np.pi/4), 0],
            [arm_length * np.sin(np.pi/4),  -arm_length * np.cos(np.pi/4), 0],
            [-arm_length * np.sin(np.pi/4),  arm_length * np.cos(np.pi/4), 0]
        ])
        
        motors_rotated = motors_body @ rotation_matrix.T
        
        # Body
        ax.scatter([0], [0], [0], color='#ffff00', s=200, edgecolors='white', linewidths=1.5)
        
        # Motor arms
        motor_colors = ['#ff3333', '#3333ff', '#33ff33', '#ff9933']
        for motor_pos, color in zip(motors_rotated, motor_colors):
            ax.plot([0, motor_pos[0]], [0, motor_pos[1]], [0, motor_pos[2]], 
                   color=color, linewidth=4)
            ax.scatter([motor_pos[0]], [motor_pos[1]], [motor_pos[2]], 
                      color=color, s=150, edgecolors='white', linewidths=1)


def create_visualizer(parent_frame=None) -> Optional[DroneVisualizer]:
    """Factory function to create a drone visualizer."""
    if _ensure_matplotlib():
        return DroneVisualizer(parent_frame=parent_frame)
    else:
        logger.warning("Matplotlib not available - visualizer disabled")
        return None
