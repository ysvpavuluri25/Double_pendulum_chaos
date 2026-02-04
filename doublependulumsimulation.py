"""
Double Inverted Pendulum Simulation
Windows-compatible version - saves files in the same folder as the script
"""

import sys
import os

# Check for required packages
required_packages = {
    'numpy': 'numpy',
    'matplotlib': 'matplotlib',
    'scipy': 'scipy'
}

missing_packages = []

for package_name, install_name in required_packages.items():
    try:
        __import__(package_name)
    except ImportError:
        missing_packages.append(install_name)

if missing_packages:
    print("=" * 60)
    print("MISSING REQUIRED PACKAGES!")
    print("=" * 60)
    print("\nThe following packages need to be installed:")
    for pkg in missing_packages:
        print(f"  - {pkg}")
    print("\nTo install them, open your command prompt and run:")
    print(f"\n  python -m pip install {' '.join(missing_packages)}")
    print("\n" + "=" * 60)
    sys.exit(1)

# Now import everything
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.integrate import odeint

print("✓ All packages loaded successfully!")

class DoublePendulum:
    def __init__(self, L1=1.0, L2=1.0, m1=1.0, m2=1.0, g=9.81):
        """
        Initialize the double pendulum system
        
        Parameters:
        L1, L2: lengths of the two pendulum arms (meters)
        m1, m2: masses of the two pendulum bobs (kg)
        g: gravitational acceleration (m/s²)
        """
        self.L1 = L1
        self.L2 = L2
        self.m1 = m1
        self.m2 = m2
        self.g = g
        
    def derivatives(self, state, t):
        """
        Calculate the derivatives for the double pendulum equations of motion
        state = [theta1, omega1, theta2, omega2]
        """
        theta1, omega1, theta2, omega2 = state
        
        # Calculate the differences
        delta = theta2 - theta1
        
        # Denominator terms
        den1 = (self.m1 + self.m2) * self.L1 - self.m2 * self.L1 * np.cos(delta) * np.cos(delta)
        den2 = (self.L2 / self.L1) * den1
        
        # Angular acceleration equations
        dtheta1_dt = omega1
        
        domega1_dt = ((self.m2 * self.L1 * omega1 * omega1 * np.sin(delta) * np.cos(delta)
                      + self.m2 * self.g * np.sin(theta2) * np.cos(delta)
                      + self.m2 * self.L2 * omega2 * omega2 * np.sin(delta)
                      - (self.m1 + self.m2) * self.g * np.sin(theta1))
                     / den1)
        
        dtheta2_dt = omega2
        
        domega2_dt = ((-self.m2 * self.L2 * omega2 * omega2 * np.sin(delta) * np.cos(delta)
                      + (self.m1 + self.m2) * self.g * np.sin(theta1) * np.cos(delta)
                      - (self.m1 + self.m2) * self.L1 * omega1 * omega1 * np.sin(delta)
                      - (self.m1 + self.m2) * self.g * np.sin(theta2))
                     / den2)
        
        return [dtheta1_dt, domega1_dt, dtheta2_dt, domega2_dt]
    
    def solve(self, initial_state, t_span, dt=0.01):
        """
        Solve the equations of motion
        initial_state = [theta1_0, omega1_0, theta2_0, omega2_0]
        """
        t = np.arange(0, t_span, dt)
        solution = odeint(self.derivatives, initial_state, t)
        return t, solution

def create_animation(save_gif=True, output_filename='double_pendulum.gif'):
    """
    Create an animated visualization of the double pendulum
    Saves to the current directory (same folder as the script)
    """
    # Initialize the pendulum
    pendulum = DoublePendulum(L1=1.0, L2=1.0, m1=1.0, m2=1.0)
    
    # Initial conditions: [theta1, omega1, theta2, omega2]
    # Starting with both pendulums at interesting angles
    initial_state = [np.pi/2, 0, np.pi/2 + 0.1, 0]
    
    # Solve the system
    t_span = 20  # seconds
    dt = 0.02
    t, solution = pendulum.solve(initial_state, t_span, dt)
    
    # Extract angles
    theta1 = solution[:, 0]
    theta2 = solution[:, 2]
    
    # Calculate positions
    x1 = pendulum.L1 * np.sin(theta1)
    y1 = -pendulum.L1 * np.cos(theta1)
    
    x2 = x1 + pendulum.L2 * np.sin(theta2)
    y2 = y1 - pendulum.L2 * np.cos(theta2)
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    # Create plot elements
    line, = ax.plot([], [], 'o-', lw=3, color='#2196F3', markersize=12, 
                    markerfacecolor='#1976D2', markeredgewidth=2, markeredgecolor='white')
    trace, = ax.plot([], [], '-', lw=1, color='#FF6B6B', alpha=0.6)
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, 
                        fontsize=14, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Store trace data
    trace_x, trace_y = [], []
    max_trace_length = 200
    
    def init():
        line.set_data([], [])
        trace.set_data([], [])
        time_text.set_text('')
        return line, trace, time_text
    
    def animate(i):
        # Update pendulum positions
        x_data = [0, x1[i], x2[i]]
        y_data = [0, y1[i], y2[i]]
        line.set_data(x_data, y_data)
        
        # Update trace
        trace_x.append(x2[i])
        trace_y.append(y2[i])
        
        # Limit trace length
        if len(trace_x) > max_trace_length:
            trace_x.pop(0)
            trace_y.pop(0)
        
        trace.set_data(trace_x, trace_y)
        
        # Update time
        time_text.set_text(f'Time: {t[i]:.2f}s')
        
        return line, trace, time_text
    
    # Create animation
    anim = FuncAnimation(fig, animate, init_func=init, frames=len(t),
                        interval=dt*1000, blit=True, repeat=True)
    
    # Add title and labels
    plt.title('Double Inverted Pendulum - Chaos in Motion', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('X Position (m)', fontsize=12)
    plt.ylabel('Y Position (m)', fontsize=12)
    
    # Save as GIF (in current directory)
    if save_gif:
        try:
            print(f"Saving animation to '{output_filename}'... This may take a minute.")
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
            output_path = os.path.join(script_dir, output_filename)
            
            anim.save(output_path, writer='pillow', fps=30, dpi=80)
            print(f"✓ Animation saved as '{output_path}'")
        except Exception as e:
            print(f"⚠ Could not save GIF: {e}")
            print("  Try: python -m pip install pillow")
    
    plt.tight_layout()
    return fig, anim

def plot_energy_and_phase(output_filename='pendulum_analysis.png'):
    """
    Create additional plots showing energy and phase space
    Saves to the current directory (same folder as the script)
    """
    pendulum = DoublePendulum(L1=1.0, L2=1.0, m1=1.0, m2=1.0)
    initial_state = [np.pi/2, 0, np.pi/2 + 0.1, 0]
    
    t, solution = pendulum.solve(initial_state, 20, 0.01)
    
    theta1 = solution[:, 0]
    omega1 = solution[:, 1]
    theta2 = solution[:, 2]
    omega2 = solution[:, 3]
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Double Pendulum Analysis', fontsize=16, fontweight='bold')
    
    # Angle vs Time
    axes[0, 0].plot(t, np.rad2deg(theta1), label='θ₁ (First Pendulum)', 
                    color='#2196F3', linewidth=2)
    axes[0, 0].plot(t, np.rad2deg(theta2), label='θ₂ (Second Pendulum)', 
                    color='#FF6B6B', linewidth=2)
    axes[0, 0].set_xlabel('Time (s)', fontsize=11)
    axes[0, 0].set_ylabel('Angle (degrees)', fontsize=11)
    axes[0, 0].set_title('Angular Position Over Time', fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Angular Velocity vs Time
    axes[0, 1].plot(t, omega1, label='ω₁ (First Pendulum)', 
                    color='#2196F3', linewidth=2)
    axes[0, 1].plot(t, omega2, label='ω₂ (Second Pendulum)', 
                    color='#FF6B6B', linewidth=2)
    axes[0, 1].set_xlabel('Time (s)', fontsize=11)
    axes[0, 1].set_ylabel('Angular Velocity (rad/s)', fontsize=11)
    axes[0, 1].set_title('Angular Velocity Over Time', fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Phase Space - Pendulum 1
    axes[1, 0].plot(theta1, omega1, color='#2196F3', linewidth=1.5, alpha=0.7)
    axes[1, 0].set_xlabel('θ₁ (rad)', fontsize=11)
    axes[1, 0].set_ylabel('ω₁ (rad/s)', fontsize=11)
    axes[1, 0].set_title('Phase Space - First Pendulum', fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Phase Space - Pendulum 2
    axes[1, 1].plot(theta2, omega2, color='#FF6B6B', linewidth=1.5, alpha=0.7)
    axes[1, 1].set_xlabel('θ₂ (rad)', fontsize=11)
    axes[1, 1].set_ylabel('ω₂ (rad/s)', fontsize=11)
    axes[1, 1].set_title('Phase Space - Second Pendulum', fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        output_path = os.path.join(script_dir, output_filename)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Analysis plots saved as '{output_path}'")
    except Exception as e:
        print(f"⚠ Could not save PNG: {e}")
    
    return fig

if __name__ == "__main__":
    print("=" * 60)
    print("DOUBLE INVERTED PENDULUM SIMULATION")
    print("=" * 60)
    print("\nThis simulation demonstrates chaotic motion - tiny changes")
    print("in starting conditions lead to completely different outcomes!")
    print("\nGenerating animation and analysis plots...")
    print("-" * 60)
    
    # Create the animation
    fig_anim, anim = create_animation(save_gif=True)
    
    # Create analysis plots
    fig_analysis = plot_energy_and_phase()
    
    print("-" * 60)
    print("\n✓ All visualizations created successfully!")
    print("\nFiles saved in the same folder as this script:")
    print("  1. double_pendulum.gif - Animated simulation")
    print("  2. pendulum_analysis.png - Analysis plots")
    print("\nYou can now use these for your LinkedIn post!")
    print("=" * 60)
    
    plt.show()
