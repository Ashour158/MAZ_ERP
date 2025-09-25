#!/usr/bin/env python3
"""
Integrated ERP System - Complete Working System
Run this file to start the full ERP system with all features
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing required packages...")
    
    requirements = [
        "flask>=2.0.0",
        "flask-cors>=3.0.0", 
        "flask-socketio>=5.0.0",
        "redis>=4.0.0",
        "PyJWT>=2.0.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "textblob>=0.17.0",
        "nltk>=3.6.0"
    ]
    
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("📚 Downloading NLTK data...")
    
    try:
        import nltk
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded")
        return True
    except Exception as e:
        print(f"⚠️ NLTK data download failed: {e}")
        return True  # Continue anyway

def check_redis():
    """Check if Redis is available"""
    print("🔍 Checking Redis connection...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception:
        print("⚠️ Redis not available - using in-memory storage")
        return False

def start_redis():
    """Start Redis server if available"""
    print("🚀 Starting Redis server...")
    
    try:
        # Try to start Redis (Windows)
        if os.name == 'nt':
            subprocess.Popen(['redis-server'], shell=True)
        else:
            subprocess.Popen(['redis-server'])
        
        time.sleep(2)
        return check_redis()
    except Exception:
        print("⚠️ Could not start Redis - continuing without it")
        return False

def run_system():
    """Run the complete ERP system"""
    print("🎬 Starting Integrated ERP System...")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Start the Flask application
    try:
        from app import app, socketio, initialize_sample_data, start_realtime_simulation
        
        # Initialize sample data
        initialize_sample_data()
        
        # Start real-time simulation
        start_realtime_simulation()
        
        print("🚀 Integrated ERP System is running!")
        print("=" * 50)
        print("📊 Dashboard: http://localhost:5000")
        print("🔧 API: http://localhost:5000/api")
        print("⚡ WebSocket: ws://localhost:5000")
        print("=" * 50)
        print("🎯 Features Available:")
        print("  • Enhanced Maintenance Module with AI")
        print("  • Intelligent Supply Chain Management")
        print("  • Advanced CRM with Analytics")
        print("  • AI Analytics Dashboard")
        print("  • Real-time Updates & Notifications")
        print("  • WebSocket Live Collaboration")
        print("=" * 50)
        print("🔑 Demo Credentials:")
        print("  Username: admin@erpnext.com")
        print("  Password: admin123")
        print("=" * 50)
        print("Press Ctrl+C to stop the system")
        print("=" * 50)
        
        # Open browser automatically
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
        
        # Run the application
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        return False
    
    return True

def main():
    """Main function to run the complete system"""
    print("🎬 Integrated ERP System - Complete Working System")
    print("=" * 60)
    print("This will start a fully functional ERP system with:")
    print("  ✅ AI-powered maintenance management")
    print("  ✅ Intelligent supply chain optimization")
    print("  ✅ Advanced CRM with predictive analytics")
    print("  ✅ Real-time collaboration features")
    print("  ✅ WebSocket live updates")
    print("  ✅ Complete API endpoints")
    print("=" * 60)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return
    
    # Download NLTK data
    download_nltk_data()
    
    # Check Redis
    if not check_redis():
        start_redis()
    
    # Run the system
    if run_system():
        print("✅ System completed successfully")
    else:
        print("❌ System failed to start")

if __name__ == "__main__":
    main()
