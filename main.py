import uvicorn
import os
import sys
import socket
import argparse

# Ensure backend package can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def find_free_port(start_port=8050, max_attempts=50):
    """Finds the first available TCP port starting from start_port."""
    for p in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return start_port


def main():
    parser = argparse.ArgumentParser(description="FinGraph-AI Application Launcher")
    parser.add_argument("--port", "-p", type=int, default=None, help="Port to run server on")
    args, _ = parser.parse_known_args()

    # Determine port: CLI arg -> Environment -> Automatic free port
    if args.port:
        port = args.port
    elif "PORT" in os.environ:
        port = int(os.environ["PORT"])
    else:
        # Check if 8020 is free, otherwise find next open port starting from 8050
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", 8020))
                port = 8020
            except OSError:
                port = find_free_port(start_port=8050)

    print("=" * 70)
    print(" Starting FinGraph-AI Server...")
    print(" Platform: Multi-Account Graph Anomaly Detection & SHAP Explainability")
    print(f" Web Application URL: http://localhost:{port}")
    print(f" Local Loopback URL:  http://127.0.0.1:{port}")
    print("=" * 70)
    
    uvicorn.run("backend.app:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    main()

