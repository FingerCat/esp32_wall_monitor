#!/usr/bin/env python3
"""
ESP32 3D Signal Visualizer - SIMPLE WORKING VERSION
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import random
import threading
import time
from collections import deque
import math

app = Flask(name)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store data
position_data = deque(maxlen=50)
motion_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """Return current data as JSON"""
    return jsonify(list(position_data))

def generate_3d_data():
    """Generate continuous 3D data"""
    angle = 0
    while True:
        # Create a moving signal source
        angle += 0.1
        
        # Generate multiple points in 3D space
        points = []
        
        # Center signal (strong)
        for i in range(5):
            points.append({
                'x': 5 + random.uniform(-1, 1),
                'y': 5 + random.uniform(-1, 1),
                'z': random.uniform(-50, -40),
                'motion': random.choice([True, False]),
                'rssi': random.uniform(-50, -40),
                'size': 10
            })
        
        # Moving signal (walking person simulation)
        walk_x = 5 + math.sin(angle) * 3
        walk_y = 5 + math.cos(angle * 0.7) * 3
        points.append({
            'x': walk_x,
            'y': walk_y,
            'z': random.uniform(-60, -45),
            'motion': True,
            'rssi': random.uniform(-60, -45),
            'size': 15
        })
        
        # Background signals
        for i in range(10):
            points.append({
                'x': random.uniform(0, 10),
                'y': random.uniform(0, 10),
                'z': random.uniform(-75, -55),
                'motion': False,
                'rssi': random.uniform(-75, -55),
                'size': 5
            })
        
        # Clear old data
        position_data.clear()
        
        # Add new points
        for point in points:
            position_data.append(point)
        
        # Send update to all connected clients
        socketio.emit('3d_update', list(position_data))
        
        # Print debug info
        print(f"📡 Sent {len(points)} 3D points - Motion at: ({walk_x:.1f}, {walk_y:.1f})")
        
        time.sleep(0.5)

@socketio.on('connect')
def handle_connect():
    print('✅ Client connected')
    emit('connected', {'message': 'Connected to 3D visualizer'})
    # Send initial data
    emit('3d_update', list(position_data))

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')

if name == 'main':
    print("\n" + "="*60)
    print("🏠 ESP32 3D Signal Visualizer - WORKING VERSION")
    print("="*60)
    print("📊 Generating simulated 3D signal data")
    print("🌐 Open: http://localhost:5000")
    print("🔴 Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Start data generator in background
    thread = threading.Thread(target=generate_3d_data)
    thread.daemon = True
    thread.start()
    
    # Run Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)