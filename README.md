# CAN Speed Lab

A small visual ECU simulator with an adjustable vehicle-speed signal, simulated bus animation, and local event monitor. The desktop app is written in Python with Tkinter; `index.html` is a browser-based prototype of the same interface.

## Run the Python app

Use Python 3 with Tkinter available:

```bash
python3 main.py
```

No third-party Python packages are required. Move the speed slider and select **Start stream** to add a local `VEH_SPEED` update every 500 ms. Select **Stop stream** to pause it.

### Run the Tkinter app in a VM and display it on your Linux laptop

The app runs in the VM, while X11 forwarding displays its window on the laptop. Run the VM commands from its console (not from the laptop):

```bash
sudo apt-get update
sudo apt-get install -y python3-tk openssh-server xauth
sudo systemctl enable --now ssh
hostname -I
sudo sshd -T | grep x11forwarding
```

The SSH setting should report `x11forwarding yes`. If it reports `no`, enable `X11Forwarding yes` in `/etc/ssh/sshd_config` and restart SSH with `sudo systemctl restart ssh`. Use the VM address reachable from the laptop from the `hostname -I` output; ignore Docker bridge addresses such as `172.17.0.1`.

On the laptop, use a terminal in the graphical desktop session. Check that `echo "$DISPLAY"` is non-empty and that `xauth` is installed (`sudo apt-get install -y xauth` if needed). Create a laptop SSH key if needed, then print its public key:

```bash
test -f ~/.ssh/id_ed25519 || ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub
```

In the VM console, add that entire public-key line to `~/.ssh/authorized_keys` for `ubuntu` (create the `.ssh` directory first if needed), then set permissions:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

The key line starts with `ssh-ed25519`; a `SHA256:...` fingerprint is not the key. Keep the private key on the laptop.

Then, from the laptop terminal, replace `<VM_IP>` with the reachable address reported in the VM:

```bash
ssh -X -t ubuntu@<VM_IP> 'cd ~/can-speed-sim && python3 main.py'
```

Keep the SSH session open while using the app. If the app reports that no display is available, connect interactively with `ssh -X ubuntu@<VM_IP>` and check `echo "$DISPLAY"` in that same SSH session; it should show a value such as `localhost:10.0`.

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