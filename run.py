import subprocess
import sys
import os
import time

def run():
    print("==================================================")
    print("   PERSONALIZED NETWORKING ASSISTANT STARTUP      ")
    print("==================================================")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    frontend_dir = os.path.join(base_dir, "frontend")
    
    # Ensure sys.path knows where to find app in backend
    os.environ["PYTHONPATH"] = backend_dir + os.pathsep + os.environ.get("PYTHONPATH", "")

    # Launch FastAPI Backend
    print("🚀 Launching FastAPI Backend (http://localhost:8000)...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "app.main:app", 
        "--host", "127.0.0.1", "--port", "8000"
    ]
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Allow backend a moment to bind to the port
    time.sleep(2)

    # Launch Streamlit Frontend
    print("🎨 Launching Streamlit Frontend (http://localhost:8501)...")
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py", 
        "--server.port", "8501", "--server.address", "127.0.0.1"
    ]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir
    )

    print("\nSystem running! Press Ctrl+C to terminate both servers.")
    print("--------------------------------------------------\n")

    # Monitor processes and stream backend logs to stdout
    try:
        while True:
            # Check if either process terminated
            backend_exit = backend_process.poll()
            frontend_exit = frontend_process.poll()
            
            if backend_exit is not None:
                print(f"❌ Backend process terminated with code {backend_exit}")
                break
            if frontend_exit is not None:
                print(f"❌ Frontend process terminated with code {frontend_exit}")
                break
                
            # Non-blocking check for stdout line from backend
            # Use readline with timeout or basic checking (in Windows, stdout.readline is blocking.
            # To prevent blocking, we can read in a separate thread, or simply rely on stdout.readline
            # because we run in an infinite loop anyway. Let's do simple reading.)
            line = backend_process.stdout.readline()
            if line:
                print(f"[API] {line.strip()}")
            else:
                time.sleep(0.05)
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down backend and frontend processes...")
    finally:
        backend_process.terminate()
        frontend_process.terminate()
        try:
            backend_process.wait(timeout=3)
            frontend_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            backend_process.kill()
            frontend_process.kill()
        print("✅ Shutdown complete.")

if __name__ == "__main__":
    run()
