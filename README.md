# AQUAS ROS AprilTag Detection for Dock Alignment

A ROS 2 system for detecting AprilTags using an RGB camera to help an autonomous boat center itself on a dock.

---

## Table of Contents

1. [What is This Project?](#what-is-this-project)
2. [Quick Start Guide](#quick-start-guide)
3. [What is ROS 2?](#what-is-ros-2)
4. [System Requirements](#system-requirements)
5. [Installing ROS 2 from Scratch](#installing-ros-2-from-scratch)
6. [ROS 2 Basics for Beginners](#ros-2-basics-for-beginners)
7. [Setting Up This Project](#setting-up-this-project)
8. [Detecting Your First AprilTag](#detecting-your-first-apriltag)
9. [Understanding Camera Intrinsics & Calibration](#understanding-camera-intrinsics--calibration)
10. [Project Architecture](#project-architecture)
11. [Advanced: Dock Alignment System](#advanced-dock-alignment-system)
12. [Troubleshooting](#troubleshooting)
13. [Project Roadmap](#project-roadmap)

---

## What is This Project?

This project enables a robot (boat) to:

-   Detect **AprilTags** (square fiducial markers like QR codes) using a USB RGB camera
-   Estimate the 3D position and orientation (6-DoF pose) of each tag
-   Use two tags mounted on a dock to calculate a midline target
-   Provide alignment errors (lateral offset, heading) to help the boat center itself for docking

**Goal:** Detect tags at 1-3 meters with lateral error < 0.20m and heading error < 8°.

---

## Quick Start Guide

**Want to see AprilTag detection working in 10 minutes?** Follow this fast track:

1. **Install ROS 2 Humble** on Ubuntu 22.04 (see [Installing ROS 2](#installing-ros-2-from-scratch))
2. **Install camera and AprilTag packages:**
    ```bash
    sudo apt install -y ros-humble-v4l2-camera ros-humble-rqt-image-view
    sudo apt install -y ros-humble-apriltag ros-humble-apriltag-msgs ros-humble-apriltag-ros
    ```
3. **Print an AprilTag:** Download and print a tag36h11 ID 0 from [apriltag-imgs](https://github.com/AprilRobotics/apriltag-imgs/tree/master/tag36h11) at 16cm size
4. **Plug in your USB camera** and run:

    ```bash
    # Terminal 1: Start camera
    ros2 run v4l2_camera v4l2_camera_node --ros-args -p device:="/dev/video0"

    # Terminal 2: Start detector
    ros2 run apriltag_ros apriltag_node --ros-args \
      -p family:=36h11 -p size:=0.16 \
      --remap /image_rect:=/image_raw \
      --remap /camera_info:=/camera_info

    # Terminal 3: View detections
    ros2 topic echo /detections
    ```

5. **Hold the printed tag in front of the camera** - you should see detection messages!

✅ **Got detections?** Awesome! Now read on to understand what's happening and improve accuracy with calibration.

🚨 **No detections?** Jump to [Troubleshooting](#troubleshooting).

---

## What is ROS 2?

**ROS** (Robot Operating System) is a framework for writing robot software. Think of it as a middleware that helps different parts of your robot communicate.

### Key Concepts:

-   **Node**: A single program/process that does one thing (e.g., read camera, detect tags, control motors)
-   **Topic**: A named channel where nodes publish/subscribe to messages (like a radio station)
-   **Message**: Data structure sent over topics (e.g., Image, PoseArray)
-   **Launch File**: Python/XML script to start multiple nodes at once
-   **Package**: A folder containing nodes, configs, and launch files
-   **Workspace**: Root folder containing all your ROS packages

### ROS 2 vs ROS 1:

-   **ROS 2** (Humble, Iron, Jazzy) is the modern version with better real-time support, security, and multi-robot capabilities
-   We use **ROS 2 Humble** (LTS release, supported until 2027)

---

## System Requirements

### Hardware:

-   **Computer:** Raspberry Pi 4 (4GB+ RAM recommended) or Ubuntu laptop
-   **Camera:** WowRobo 2MP USB RGB camera (UVC-compatible)
-   **AprilTags:** Two printed tags from the `tag36h11` family (16.2 cm side length recommended)

### Software:

-   **OS:** Ubuntu 22.04 LTS (Jammy Jellyfish)
-   **ROS 2:** Humble Hawksbill
-   **Python:** 3.10+ (comes with Ubuntu 22.04)

---

## Installing ROS 2 from Scratch

### Step 1: Set Up Ubuntu 22.04

If using a **Raspberry Pi**:

1. Download Ubuntu 22.04 Server/Desktop for Raspberry Pi from [ubuntu.com/download/raspberry-pi](https://ubuntu.com/download/raspberry-pi)
2. Flash to SD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
3. Boot and complete initial setup

If using a **laptop**, install Ubuntu 22.04 LTS from [ubuntu.com](https://ubuntu.com/download/desktop).

### Step 2: Install ROS 2 Humble

Open a terminal and run these commands:

```bash
# Set locale
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS 2 apt repository
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 Humble Desktop (includes RViz, demos, tutorials)
sudo apt update
sudo apt upgrade -y
sudo apt install ros-humble-desktop -y

# Install development tools
sudo apt install python3-colcon-common-extensions python3-rosdep -y

# Initialize rosdep (manages dependencies)
sudo rosdep init
rosdep update
```

### Step 3: Source ROS 2 (Add to Shell)

Every time you open a new terminal, you need to "source" ROS 2 to access its commands:

```bash
source /opt/ros/humble/setup.bash
```

To do this automatically, add it to your `~/.bashrc`:

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Test ROS 2 Installation

```bash
# Terminal 1: Start a demo talker node
ros2 run demo_nodes_cpp talker

# Terminal 2 (new terminal): Start a demo listener node
ros2 run demo_nodes_cpp listener
```

You should see the talker publishing messages and the listener receiving them. Press `Ctrl+C` to stop.

---

## ROS 2 Basics for Beginners

### Essential Commands

```bash
# List all running nodes
ros2 node list

# List all active topics
ros2 topic list

# See messages on a topic in real-time
ros2 topic echo /camera/image_raw

# Get info about a topic (message type, publishers, subscribers)
ros2 topic info /camera/image_raw

# Run a single node from a package
ros2 run <package_name> <executable_name>

# Launch multiple nodes from a launch file
ros2 launch <package_name> <launch_file>

# Record data to a bag file for replay
ros2 bag record -a  # record all topics
ros2 bag play <bag_file>  # replay
```

### Workspace Structure

A typical ROS 2 workspace looks like this:

```
~/aquas_ws/                    # Workspace root
├── src/                       # Source code
│   ├── aquas_camera_bringup/  # Package 1
│   ├── aquas_apriltag_bringup/# Package 2
│   └── aquas_dock_align/      # Package 3
├── build/                     # Build artifacts (auto-generated)
├── install/                   # Installed files (auto-generated)
└── log/                       # Build logs (auto-generated)
```

### Build Workflow

```bash
cd ~/aquas_ws
colcon build                   # Build all packages
colcon build --packages-select aquas_dock_align  # Build one package
source install/setup.bash      # Source your workspace
```

**Important:** After building, always `source install/setup.bash` before running nodes.

---

## Project Architecture

```
┌─────────────┐
│ USB Camera  │ (WowRobo 2MP)
└──────┬──────┘
       │ /image_raw (sensor_msgs/Image)
       │ /camera_info (sensor_msgs/CameraInfo)
       v
┌─────────────────┐
│ v4l2_camera     │ (Camera driver node)
│ or usb_cam      │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ apriltag_ros    │ (AprilTag detector)
└──────┬──────────┘
       │ /detections (apriltag_msgs/AprilTagDetectionArray)
       │ /tf (tag poses in 3D)
       v
┌─────────────────┐
│ dock_align_node │ (Custom node)
└──────┬──────────┘
       │ /dock_align_error (lateral_m, heading_rad, distance_m)
       v
┌─────────────────┐
│ Controller      │ (P controller for alignment)
└─────────────────┘
```

### Packages:

1. **aquas_camera_bringup**: Launch files for camera and intrinsics
2. **aquas_apriltag_bringup**: AprilTag detection configuration
3. **aquas_dock_align**: Computes dock midline and alignment errors

---

## Setting Up This Project

### Step 1: Install Additional Dependencies

```bash
sudo apt update
sudo apt install -y \
  ros-humble-image-tools \
  ros-humble-v4l2-camera \
  ros-humble-usb-cam \
  ros-humble-rqt-image-view \
  ros-humble-tf-transformations \
  ros-humble-rviz2 \
  ros-humble-camera-info-manager \
  ros-humble-image-transport \
  python3-opencv \
  libopencv-dev
```

### Step 2: Create Workspace and Clone Dependencies

```bash
# Create workspace
mkdir -p ~/aquas_ws/src
cd ~/aquas_ws/src

# Clone AprilTag library and ROS wrapper
git clone https://github.com/AprilRobotics/apriltag.git
git clone https://github.com/christianrauch/apriltag_ros.git -b ros2

# Clone image_common (camera_info_manager, etc.)
git clone https://github.com/ros-perception/image_common.git -b humble

# Clone this project (if it's in a git repo)
# git clone <your-repo-url>
```

### Step 3: Create Project Packages

```bash
cd ~/aquas_ws/src

# Create three packages
ros2 pkg create aquas_camera_bringup --build-type ament_cmake --dependencies rclcpp sensor_msgs
ros2 pkg create aquas_apriltag_bringup --build-type ament_cmake --dependencies rclcpp
ros2 pkg create aquas_dock_align --build-type ament_cmake --dependencies rclcpp rclpy geometry_msgs tf2_ros
```

### Step 4: Install Dependencies with rosdep

```bash
cd ~/aquas_ws
rosdep install --from-paths src --ignore-src -r -y
```

### Step 5: Build Workspace

```bash
cd ~/aquas_ws
colcon build --symlink-install
source install/setup.bash
```

**Note:** `--symlink-install` creates symlinks to Python scripts so you don't need to rebuild after editing them.

### Step 6: Add Workspace to .bashrc

```bash
echo "source ~/aquas_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## Detecting Your First AprilTag

This section walks you through getting AprilTag detection working. We'll start simple and build up.

### Why Start Here?

**Philosophy:** Get something working first, then optimize. You can detect AprilTags without calibration, but the 3D pose won't be very accurate. That's okay for learning! Once you see detections working, you'll understand why calibration matters.

### Step 1: Verify Your Camera

**Plug in your USB camera** and identify the device:

```bash
ls /dev/video*
# Should show /dev/video0 or similar

# Check camera details
v4l2-ctl --list-devices
```

**Test the camera feed:**

```bash
# Terminal 1: Start camera node
ros2 run v4l2_camera v4l2_camera_node --ros-args \
  -p device:="/dev/video0" \
  -p image_size:="[640,480]" \
  -p time_per_frame:="[1,30]"

# Terminal 2: View the image
ros2 run rqt_image_view rqt_image_view
```

In `rqt_image_view`, select `/image_raw` from the dropdown. You should see your camera feed.

✅ **Checkpoint:** Can you see the camera image? If yes, proceed. If no, see [Troubleshooting](#troubleshooting).

### Step 2: Print AprilTags

AprilTags are like QR codes but designed for robotics. You need to print physical tags to detect.

**Where to get tags:**

1. Go to [AprilTag Images Repository](https://github.com/AprilRobotics/apriltag-imgs/tree/master/tag36h11)
2. Download `tag36_11_00000.png` (ID 0) and `tag36_11_00001.png` (ID 1)
3. Print each at **16.2 cm** side length (measure the outer black square)

**Printing tips:**

-   Use thick matte paper or cardboard
-   Print in black and white, high quality
-   Measure the final size with a ruler
-   Avoid glossy paper (causes glare)
-   Keep the white border around the tag

**Quick test:** Print just one tag (ID 0) first to verify everything works.

### Step 3: Run the AprilTag Detector

**Basic detection (no config file needed):**

```bash
# Terminal 1: Camera (if not already running)
ros2 run v4l2_camera v4l2_camera_node --ros-args -p device:="/dev/video0"

# Terminal 2: AprilTag detector
ros2 run apriltag_ros apriltag_node --ros-args \
  -p family:=36h11 \
  -p size:=0.162 \
  --remap /image_rect:=/image_raw \
  --remap /camera_info:=/camera_info
```

**What these parameters mean:**

-   `family:=36h11` - The tag family (36h11 is most common, has 587 unique IDs)
-   `size:=0.162` - Tag size in meters (16.2 cm)
-   Remaps connect the detector to the camera topics

### Step 4: See Your First Detection!

**Hold the printed tag in front of the camera** (about 1-2 meters away, well-lit, facing camera).

**View detections in a new terminal:**

```bash
ros2 topic echo /detections
```

You should see output like:

```yaml
detections:
    - family: "36h11"
      id: 0
      hamming: 0
      centre:
          x: 320.5
          y: 240.3
      pose:
          pose:
              pose:
                  position:
                      x: 0.0
                      y: 0.0
                      z: 1.5 # Distance in meters (approximate without calibration)
```

🎉 **Success!** You're detecting AprilTags!

### Step 5: Visualize in 3D (RViz)

See the tag's 3D pose in RViz:

```bash
# Terminal 3: Launch RViz
rviz2
```

**In RViz:**

1. Click **"Add"** (bottom left)
2. Select **"By topic"** tab
3. Find `/tf` → **TF** → Click "OK"
4. In the left panel, change **"Fixed Frame"** to `camera_optical_frame`
5. (Optional) Add → By topic → `/image_raw` → Image to see the camera feed

**Hold your tag in front of the camera** - you should see a 3D coordinate frame (red/green/blue axes) appear in RViz showing the tag's position and orientation!

### Step 6: Understanding What You See

**Without camera calibration:**

-   ✅ Tag **detection** works perfectly (ID recognition)
-   ✅ 2D position in the image is accurate
-   ⚠️ 3D position (x, y, z) is **approximate** (may be off by 10-30%)
-   ⚠️ Orientation (roll, pitch, yaw) is **rough**

**Why?** The detector assumes default camera parameters. Your camera's actual focal length, lens distortion, etc. differ from the defaults.

**Next step:** Camera calibration will fix the 3D pose accuracy!

### Step 7: (Optional) Create a Config File

For easier reuse, create a config file:

```bash
mkdir -p ~/aquas_ws/src/aquas_apriltag_bringup/config
nano ~/aquas_ws/src/aquas_apriltag_bringup/config/tags.yaml
```

Paste:

```yaml
apriltag:
    ros__parameters:
        image_transport: raw
        family: 36h11
        size: 0.162 # 16.2 cm in meters
        max_hamming: 0 # Require perfect detection (no errors)
        z_aligned: true # Align tag z-axis with camera z-axis
```

**Run with config file:**

```bash
ros2 run apriltag_ros apriltag_node --ros-args \
  --params-file ~/aquas_ws/src/aquas_apriltag_bringup/config/tags.yaml \
  --remap /image_rect:=/image_raw \
  --remap /camera_info:=/camera_info
```

---

## Understanding Camera Intrinsics & Calibration

Now that you've seen AprilTag detection working, let's understand **why calibration matters** and how to do it.

### What Are Camera Intrinsics?

Every camera has unique internal properties:

1. **Focal length (fx, fy):** How much the lens "zooms" (in pixels)
2. **Principal point (cx, cy):** Where the optical axis hits the sensor (usually near image center)
3. **Distortion coefficients (k1, k2, p1, p2, k3):** How the lens warps straight lines (barrel/pincushion distortion)

These parameters form the **intrinsic matrix K**:

```
K = [ fx  0  cx ]
    [  0 fy  cy ]
    [  0  0   1 ]
```

### Why Does This Matter for AprilTags?

AprilTag pose estimation works like this:

1. **Detect corners** in the image (pixel coordinates)
2. **Undistort** using intrinsics (correct lens distortion)
3. **Solve PnP** (Perspective-n-Point) to find 3D pose from 2D corners + known tag size

**Without calibration:** The detector uses default values (like fx = 500, cx = 320). If your camera has fx = 620, your depth estimates will be wrong by 20%+!

**With calibration:** Accurate intrinsics → accurate 3D pose (errors drop from 30% to <3%).

### When Do You Need Calibration?

-   ✅ **Need calibration** if you care about:
    -   Accurate distance measurements
    -   Precise dock alignment (<20cm error)
    -   Multiple tag fusion
    -   Real-world metric positioning
-   🤷 **Skip calibration** if you only need:
    -   Tag ID recognition
    -   Rough "tag on left vs right"
    -   Quick prototyping/demos

**For this dock alignment project:** Calibration is **highly recommended** to achieve <20cm lateral error.

### How to Calibrate Your Camera

#### Step 1: Print a Checkerboard

Download and print an **8x6 checkerboard** (8 corners wide, 6 corners tall) with 25mm squares from [OpenCV Patterns](https://docs.opencv.org/4.x/da/d0d/tutorial_camera_calibration_pattern.html).

**Alternatively:** Use any checkerboard pattern, just note the dimensions (e.g., 7x9 with 30mm squares).

**Mounting tip:** Glue the printed pattern to a flat, rigid board (foamcore, cardboard) so it stays perfectly flat during capture.

#### Step 2: Capture Calibration Images

You need 20-30 images of the checkerboard at **different positions, angles, and distances**.

```bash
# Terminal 1: Camera (if not running)
ros2 run v4l2_camera v4l2_camera_node --ros-args -p device:="/dev/video0"

# Terminal 2: Image viewer (to see what you're capturing)
ros2 run rqt_image_view rqt_image_view
```

**Capture strategy:**

-   Hold checkerboard at different positions: center, top-left, top-right, bottom-left, bottom-right
-   Different angles: straight on, tilted left/right, tilted up/down
-   Different distances: close (0.5m), medium (1m), far (2m)
-   Ensure checkerboard fills ~30-50% of the image
-   Keep good lighting (avoid shadows on board)

**Save images using ros2 bag:**

```bash
# Terminal 3: Record images
mkdir ~/calibration_images && cd ~/calibration_images
ros2 bag record -o calib_bag /image_raw
```

Move the checkerboard around, then press `Ctrl+C` when you have ~20-30 different poses (takes 1-2 minutes).

#### Step 3: Run Camera Calibration

Install the calibration package:

```bash
sudo apt install ros-humble-camera-calibration
```

**Run the calibration tool:**

```bash
ros2 run camera_calibration cameracalibrator \
  --size 8x6 \
  --square 0.025 \
  image:=/image_raw \
  camera:=/camera
```

**Or from your recorded bag:**

```bash
# Terminal 1: Play the bag
ros2 bag play ~/calibration_images/calib_bag

# Terminal 2: Run calibrator
ros2 run camera_calibration cameracalibrator \
  --size 8x6 \
  --square 0.025 \
  image:=/image_raw
```

**In the calibration window:**

-   You'll see the checkerboard detected with colored lines
-   The **X, Y, Size, Skew** bars fill up as you show different poses
-   When all bars are green, click **"CALIBRATE"** (takes 10-30 seconds)
-   After calibration completes, click **"COMMIT"** to see results
-   Click **"SAVE"** to write the calibration file

The calibration data is saved to `/tmp/calibrationdata.tar.gz`.

#### Step 4: Extract and Use Calibration

```bash
# Extract the calibration
mkdir -p ~/aquas_ws/src/aquas_camera_bringup/config
cd ~/aquas_ws/src/aquas_camera_bringup/config
tar -xzf /tmp/calibrationdata.tar.gz
# This creates ost.yaml

# Rename for clarity
mv ost.yaml camera.yaml

# The file contains something like:
# image_width: 640
# image_height: 480
# camera_matrix:
#   rows: 3
#   cols: 3
#   data: [615.123, 0.0, 320.456, 0.0, 614.789, 240.123, 0.0, 0.0, 1.0]
# distortion_coefficients:
#   data: [-0.123, 0.045, 0.001, -0.002, 0.0]
```

#### Step 5: Run Camera with Calibration

**Method 1: Direct camera_info_url parameter:**

```bash
ros2 run v4l2_camera v4l2_camera_node --ros-args \
  -p device:="/dev/video0" \
  -p camera_info_url:="file:///home/<yourusername>/aquas_ws/src/aquas_camera_bringup/config/camera.yaml"
```

**Method 2: Create a launch file** (recommended for reuse):

```bash
nano ~/aquas_ws/src/aquas_camera_bringup/launch/camera_calib.launch.py
```

```python
from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('aquas_camera_bringup'),
        'config',
        'camera.yaml'
    )

    return LaunchDescription([
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            parameters=[{
                'device': '/dev/video0',
                'camera_info_url': 'file://' + config
            }]
        )
    ])
```

**Launch:**

```bash
ros2 launch aquas_camera_bringup camera_calib.launch.py
```

#### Step 6: Verify Calibration Improved Accuracy

**Test 1: Place tag at known distance (e.g., exactly 1.50 meters):**

```bash
# Run calibrated camera + detector
ros2 topic echo /detections
```

Compare the reported z-distance before/after calibration - it should be much closer to 1.50m!

**Test 2: Static stability test:**

Place tag on a stable mount, record 100 pose samples:

```bash
ros2 topic echo /detections | head -n 100 > calibrated_poses.txt
```

Calculate standard deviation of x, y, z - should be <3cm at 2m with good calibration.

---

## Project Architecture

Now that you can detect AprilTags with accurate poses, let's understand how the full dock alignment system works.

### System Overview

```
┌─────────────┐
│ USB Camera  │ (WowRobo 2MP @ 640x480, 30fps)
└──────┬──────┘
       │ /image_raw (sensor_msgs/Image)
       │ /camera_info (sensor_msgs/CameraInfo)
       v
┌─────────────────┐
│ v4l2_camera     │ (Camera driver node)
│ or usb_cam      │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ apriltag_ros    │ (AprilTag detector)
└──────┬──────────┘
       │ /detections (apriltag_msgs/AprilTagDetectionArray)
       │ /tf (tag poses: camera_optical_frame → tag_<ID>)
       v
┌─────────────────┐
│ dock_align_node │ (Custom Python/C++ node)
└──────┬──────────┘
       │ /dock_align_error (custom msg)
       │   - lateral_m: float (sideways offset from midline)
       │   - heading_rad: float (yaw angle error)
       │   - distance_m: float (distance to dock)
       v
┌─────────────────┐
│ Controller      │ (Simple P controller for MVP)
└──────┬──────────┘
       │ /cmd_vel (geometry_msgs/Twist)
       v
┌─────────────────┐
│ Robot Base      │ (Thrusters/motors)
└─────────────────┘
```

### Package Structure

```
~/aquas_ws/src/
├── aquas_camera_bringup/      # Camera launch files and configs
│   ├── launch/
│   │   ├── camera.launch.py          # Basic camera
│   │   └── camera_calib.launch.py    # With calibration
│   ├── config/
│   │   └── camera.yaml               # Calibration params
│   └── CMakeLists.txt
│
├── aquas_apriltag_bringup/    # AprilTag detection configs
│   ├── launch/
│   │   └── tags_detect.launch.py     # Camera + detector
│   ├── config/
│   │   └── tags.yaml                 # Detector params (family, size)
│   └── CMakeLists.txt
│
└── aquas_dock_align/          # Dock alignment logic
    ├── launch/
    │   └── dock_align.launch.py      # Full pipeline + controller
    ├── src/
    │   ├── dock_align_node.py        # Midline computation
    │   └── simple_controller.py      # P controller
    ├── msg/
    │   └── DockAlignError.msg        # Custom message type
    └── CMakeLists.txt
```

---

## Advanced: Dock Alignment System

Once you have accurate AprilTag detection, you can build the dock alignment system.

### Goal

Use **two AprilTags** mounted on a dock to:

1. Compute the **midline** between them (the target line to center on)
2. Calculate **lateral error** (how far left/right the robot is from the midline)
3. Calculate **heading error** (robot's yaw angle relative to midline direction)
4. Control the robot to drive toward and center on the midline

### Tag Mounting Plan

**Physical setup:**

-   Two AprilTags (tag36h11, IDs 0 and 1)
-   Each tag: 16.2 cm side length
-   Spacing: 1.0 meter apart (center to center), horizontally level
-   Mounted on dock structure, facing outward toward approaching robot

**Frame definitions:**

-   `camera_optical_frame`: Camera's coordinate frame (z forward, x right, y down)
-   `base_link`: Robot's coordinate frame (x forward, y left, z up)
-   `tag_0`, `tag_1`: Each tag's coordinate frame (published by apriltag_ros via /tf)
-   `dock_frame`: Midpoint between the two tags, x-axis along dock edge

### Midline Computation Logic

**Inputs:**

-   Tag A pose: `T_cam_tagA` (x, y, z position of tag 0)
-   Tag B pose: `T_cam_tagB` (x, y, z position of tag 1)

**Steps:**

1. **Get tag centers in camera frame:**

    ```python
    pA = [xA, yA, zA]  # From /tf transform camera → tag_0
    pB = [xB, yB, zB]  # From /tf transform camera → tag_1
    ```

2. **Compute midpoint (dock center):**

    ```python
    midpoint = [(xA + xB)/2, (yA + yB)/2, (zA + zB)/2]
    ```

3. **Compute dock direction (line between tags):**

    ```python
    dock_direction = normalize(pB - pA)  # Unit vector from tag A to B
    ```

4. **Project robot position onto midline:**

    - Assume robot is at camera position (or apply known transform `base_link → camera`)
    - Robot position in camera frame: `[0, 0, 0]` (camera is origin)
    - Vector from midpoint to robot: `v_robot = [0, 0, 0] - midpoint`

5. **Calculate lateral error (cross-track distance):**

    ```python
    # Distance from robot to the line (perpendicular offset)
    lateral_error = dot(v_robot, perpendicular_to_dock_direction)
    # Or simpler: project robot onto line, measure perpendicular distance
    ```

6. **Calculate heading error:**

    ```python
    # Desired heading: point toward dock (or along dock line)
    desired_yaw = atan2(dock_direction.y, dock_direction.x)
    robot_yaw = get_robot_yaw_from_imu_or_tf()
    heading_error = desired_yaw - robot_yaw
    ```

7. **Calculate distance to dock:**
    ```python
    distance = norm(midpoint)  # Euclidean distance to midpoint
    ```

**Output:** Publish `DockAlignError` message:

```
lateral_m: 0.15      # Robot is 15cm to the right of midline
heading_rad: -0.08   # Robot should turn 4.6° left to align
distance_m: 2.3      # Robot is 2.3m from dock
```

### Custom Message Definition

Create `aquas_dock_align/msg/DockAlignError.msg`:

```
# DockAlignError.msg
float32 lateral_m      # Lateral offset from midline (+ = right, - = left)
float32 heading_rad    # Heading error (+ = turn right, - = turn left)
float32 distance_m     # Distance to dock center
bool tags_visible      # True if both tags detected
```

### Simple P Controller

**Goal:** Drive lateral and heading errors to zero.

**Control law:**

```python
# Proportional gains
K_lateral = 0.5   # m/s per meter of lateral error
K_heading = 1.0   # rad/s per radian of heading error
K_forward = 0.3   # m/s (slow constant forward speed)

# Control outputs
lateral_velocity = -K_lateral * lateral_error  # Negative to correct right offset
yaw_velocity = -K_heading * heading_error
forward_velocity = K_forward  # Slow approach

# Publish Twist message
cmd_vel.linear.x = forward_velocity
cmd_vel.linear.y = lateral_velocity  # If robot has lateral thrusters
cmd_vel.angular.z = yaw_velocity
```

**Safety limits:**

-   Max lateral speed: 0.5 m/s
-   Max yaw rate: 0.5 rad/s
-   Stop if distance < 0.5m (arrived)
-   Stop if tags not visible for >1 second

### Implementation Sketch

**dock_align_node.py** (Python example):

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from apriltag_msgs.msg import AprilTagDetectionArray
from geometry_msgs.msg import Twist
from aquas_dock_align.msg import DockAlignError
import tf2_ros
import numpy as np

class DockAlignNode(Node):
    def __init__(self):
        super().__init__('dock_align_node')
        self.sub = self.create_subscription(
            AprilTagDetectionArray, '/detections', self.detections_callback, 10)
        self.pub = self.create_publisher(DockAlignError, '/dock_align_error', 10)
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

    def detections_callback(self, msg):
        # Find tags 0 and 1
        tag_0 = next((d for d in msg.detections if d.id == 0), None)
        tag_1 = next((d for d in msg.detections if d.id == 1), None)

        if not (tag_0 and tag_1):
            self.get_logger().warn('Both tags not visible')
            return

        # Get poses from /tf
        try:
            t0 = self.tf_buffer.lookup_transform('camera_optical_frame', 'tag_0', rclpy.time.Time())
            t1 = self.tf_buffer.lookup_transform('camera_optical_frame', 'tag_1', rclpy.time.Time())
        except Exception as e:
            self.get_logger().error(f'TF lookup failed: {e}')
            return

        # Extract positions
        p0 = np.array([t0.transform.translation.x, t0.transform.translation.y, t0.transform.translation.z])
        p1 = np.array([t1.transform.translation.x, t1.transform.translation.y, t1.transform.translation.z])

        # Compute midpoint and dock direction
        midpoint = (p0 + p1) / 2
        dock_vec = p1 - p0
        dock_dir = dock_vec / np.linalg.norm(dock_vec)

        # Robot position (camera is at origin in camera frame)
        robot_pos = np.array([0, 0, 0])

        # Lateral error: perpendicular distance to line
        to_robot = robot_pos - midpoint
        lateral_error = np.dot(to_robot, np.array([-dock_dir[1], dock_dir[0], 0]))  # 2D perpendicular

        # Distance to dock
        distance = np.linalg.norm(midpoint)

        # Heading error (simplified: assume robot should point at midpoint)
        desired_yaw = np.arctan2(midpoint[1], midpoint[0])
        heading_error = desired_yaw  # Assuming robot yaw is 0 (looking straight ahead)

        # Publish error
        error_msg = DockAlignError()
        error_msg.lateral_m = float(lateral_error)
        error_msg.heading_rad = float(heading_error)
        error_msg.distance_m = float(distance)
        error_msg.tags_visible = True
        self.pub.publish(error_msg)

def main():
    rclpy.init()
    node = DockAlignNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Testing the Alignment System

**Bench test:**

1. Print two tags (IDs 0 and 1) at 16.2cm
2. Mount them 1m apart on a wall/board
3. Run the full pipeline:
    ```bash
    ros2 launch aquas_dock_align dock_align.launch.py
    ```
4. Walk the camera around in front of the tags
5. Echo the alignment error:
    ```bash
    ros2 topic echo /dock_align_error
    ```
6. Verify:
    - `lateral_m` changes as you move left/right
    - `heading_rad` changes as you rotate
    - `distance_m` changes as you move closer/farther

**Field test:**

1. Mount tags on actual dock structure
2. Mount camera on robot
3. Approach dock from 3-5m away
4. Record rosbag for analysis:
    ```bash
    ros2 bag record -a
    ```
5. Evaluate error convergence and stability

---

## Troubleshooting

### Camera Not Detected

```bash
# Check USB connection
lsusb  # Should show WowRobo camera

# Check video device
ls -l /dev/video*

# Give permissions (if needed)
sudo usermod -aG video $USER
# Log out and back in
```

### No AprilTag Detections

-   **Check tag size:** Ensure `size: 0.162` matches your printed tag in meters
-   **Check family:** Tag must be `tag36h11` if that's what you configured
-   **Lighting:** AprilTags need good contrast; avoid glare and shadows
-   **Focus:** Ensure camera is focused (some USB cameras have manual focus rings)
-   **Distance:** Start at 1-2 meters; very close/far ranges are harder

### ROS 2 Command Not Found

```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash
source ~/aquas_ws/install/setup.bash
```

### "Package not found" Error

```bash
# Rebuild workspace
cd ~/aquas_ws
colcon build --symlink-install
source install/setup.bash
```

### Pose is Unstable/Flickering

-   **Calibrate camera** (see Camera Calibration section)
-   **Lower `max_hamming`** to 0 (more strict detection)
-   **Increase tag size** (larger tags = more accurate)
-   **Add temporal filtering** in post-processing

---

## Project Roadmap

### Phase 0: Learning Path (Start Here!)

**Goal:** Get basic AprilTag detection working without worrying about perfect accuracy.

1. **Install ROS 2 and dependencies** ✓
2. **Camera bring-up:** Get camera streaming at 640x480, 30 fps
3. **Print one AprilTag:** Download and print tag36h11 ID 0 at 16.2cm
4. **Run detector:** Use apriltag_ros with basic settings
5. **See detections:** View in RViz and `/detections` topic
6. **Understand limitations:** Notice that 3D pose is approximate

**Success:** You see tag detections and rough 3D poses without calibration.

### Phase 1: Improve Accuracy with Calibration

**Goal:** Calibrate camera intrinsics to get accurate 3D poses.

1. **Print checkerboard:** 8x6 grid, 25mm squares
2. **Capture calibration images:** 20-30 images at various angles
3. **Run calibration tool:** `ros2 run camera_calibration cameracalibrator`
4. **Save calibration:** Extract `camera.yaml` from output
5. **Run camera with calibration:** Load `camera_info_url` parameter
6. **Verify improvement:** Test pose accuracy at known distances

**Success Criteria:**

-   3D position error < 5% at 1-3m range
-   Pose jitter < 3cm RMS at 2m with static tag

### Phase 2: Two-Tag Dock Alignment

**Goal:** Use two tags to compute dock midline and alignment errors.

1. **Print second tag:** tag36h11 ID 1 at 16.2cm
2. **Mount tags:** Space 1.0m apart, level, on dock/board
3. **Create custom message:** `DockAlignError.msg`
4. **Implement dock_align_node:** Compute midline, lateral error, heading error
5. **Test bench setup:** Walk camera around, verify error signals
6. **Record rosbag:** Save test data for analysis

**Success Criteria:**

-   Both tags detected simultaneously at 1-3m
-   Lateral error signal changes correctly when moving left/right
-   Heading error signal changes correctly when rotating
-   Loop rate ≥10 Hz

### Phase 3: Controller and Field Test

**Goal:** Close the loop with a simple controller and test on water.

1. **Implement P controller:** Simple proportional control for lateral and yaw
2. **Add safety limits:** Max velocities, timeout if tags lost
3. **Bench test controller:** Log-only mode or dummy robot base
4. **Mount on boat:** Install camera and tags on actual dock
5. **Field dry-run:** Approach dock from 3-5m, record results
6. **Tune parameters:** Adjust P gains, detector settings based on performance

**Success Criteria:**

-   Lateral error < 0.20m RMS at 2m range
-   Heading error < 8° RMS
-   Stable approach without oscillation
-   Safe stop if tags become occluded

### Phase 4: Future Enhancements

**Out of scope for MVP, but good ideas for later:**

-   [ ] Temporal filtering or EKF for smoother poses
-   [ ] Auto-exposure/gain control for varying lighting conditions
-   [ ] Higher resolution (1920x1080) for longer detection range
-   [ ] GPU acceleration (isaac_ros_apriltag) for higher framerate
-   [ ] Integration with full navigation stack (Nav2)
-   [ ] Multi-session on-water testing and data collection
-   [ ] PID or MPC controller for better tracking
-   [ ] Sensor fusion with IMU, GPS, depth camera

---

## Useful References

-   **AprilTag Library:** https://github.com/AprilRobotics/apriltag
-   **apriltag_ros:** https://github.com/christianrauch/apriltag_ros
-   **ROS 2 Humble Docs:** https://docs.ros.org/en/humble/
-   **ROS 2 Tutorials:** https://docs.ros.org/en/humble/Tutorials.html
-   **OpenCV Camera Calibration:** https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
-   **Print AprilTags:** https://github.com/AprilRobotics/apriltag-imgs

---

## Tag Configuration

-   **Family:** `tag36h11` (standard, 587 unique IDs)
-   **Size:** 16.2 cm (0.162 m) black square
-   **Dock Setup:** Two tags (IDs 0 and 1) spaced 1.0 m apart horizontally
-   **Material:** Print on matte paper/cardboard; laminate with matte finish to avoid glare

---

## Support and Contributing

For questions or issues:

1. Check the Troubleshooting section above
2. Search ROS 2 Answers: https://answers.ros.org/
3. Review AprilTag ROS issues: https://github.com/christianrauch/apriltag_ros/issues

---

## License

This project is intended for educational and research purposes. AprilTag library is BSD-licensed. ROS 2 packages follow their respective licenses.

---

**Happy coding and smooth docking! 🚤**
