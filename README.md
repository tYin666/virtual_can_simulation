# CAN Speed Lab

A small visual ECU simulator with an adjustable vehicle-speed signal, simulated bus animation, and local event monitor. The desktop app is written in Python with Tkinter; `index.html` is a browser-based prototype of the same interface.

## Run the Python app

Use Python 3 with Tkinter available:

```bash
python3 main.py
```

No third-party Python packages are required. Move the speed slider and select **Start stream** to add a local `VEH_SPEED` update every 500 ms. Select **Stop stream** to pause it.

## Run the console simulator

```bash
python3 console.py --speed 72 --interval-ms 500 --count 10
```

Use `--count 0` to stream until interrupted with Ctrl+C. Speed must be between 0 and 240 km/h.

## Run it in Docker inside Multipass

Run these commands in a host terminal from the project directory (`can-speed-sim`). The mount makes the current project files available to Docker inside the VM.

```bash
# Create the VM once. If it already exists, skip this command.
multipass launch 24.04 --name can-speed-vm --cpus 2 --memory 2G --disk 10G

# If the VM already exists but is stopped, start it instead.
# multipass start can-speed-vm

# Create the mount destination and share this project with the VM.
multipass exec can-speed-vm -- mkdir -p /home/ubuntu/can-speed-sim
multipass mount "$PWD" can-speed-vm:/home/ubuntu/can-speed-sim

# Install and start Docker inside the VM.
multipass exec can-speed-vm -- sudo apt-get update
multipass exec can-speed-vm -- sudo apt-get install -y docker.io
multipass exec can-speed-vm -- sudo systemctl enable --now docker
multipass exec can-speed-vm -- sudo docker --version

# Build the image from the mounted project directory.
multipass exec can-speed-vm -- bash -lc 'cd /home/ubuntu/can-speed-sim && sudo docker build -t can-speed-sim .'

# Run ten simulated speed messages; output appears in this host terminal.
multipass exec can-speed-vm -- sudo docker run --rm can-speed-sim --speed 72 --interval-ms 500 --count 10
```

If the VM is already running and the project is already mounted, skip the corresponding launch, start, and mount commands. Set `--count 0` for continuous output; press Ctrl+C to stop. The container runs `console.py` and does not require a desktop session.

## Run the browser prototype

Open `index.html` in a browser. No install or server is required.

## Scope

Both versions are visual simulators only. They do not create CAN frames, open a SocketCAN interface, or connect to a vehicle. The monitor entries are local UI events, not messages sent on a bus.