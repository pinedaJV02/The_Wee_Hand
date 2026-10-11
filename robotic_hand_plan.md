# Camera Controlled Robotic Hand: Rough Plan

## Programs and Tools Needed

### Core (start here)
1. **Python 3.10 or newer** (main language for everything in phases 1 to 5)
2. **VS Code** (editor, with the Python extension)
3. **Git and GitHub** (version control and your public proof of work)
4. **Python libraries** (install with pip):
   * `mediapipe` (hand tracking, 21 landmarks per hand)
   * `opencv-python` (camera capture and drawing overlays)
   * `numpy` and `scipy` (vector maths, filtering, curve fitting)
   * `pyserial` (serial communication, used by the servo SDK)
   * `pandas` and `matplotlib` (logging, plotting and analysis)
5. **Feetech scservo_sdk** (Python driver for the SCS0009 bus servos)
6. **Feetech debug software** (the manufacturer tool to set servo IDs, baud rate and test movement from a GUI)

### Hardware to go with the software
1. Bus servo adapter board (Feetech URT-1 or Waveshare equivalent) for USB to servo bus
2. Regulated power supply sized for stall current of all SCS0009 servos together
3. Webcam (30 to 60 fps), good lighting and a plain background

### Later phases
1. **Ubuntu 24.04 with ROS 2 Jazzy** (native, dual boot, or WSL2 if USB passthrough works for you)
2. **rosbag2** and **PlotJuggler or Foxglove** (recording and visualising data)
3. **Arduino IDE or PlatformIO** for an ESP32 or Teensy (strain gauge readout)
4. **HX711 or ADS1256 amplifier boards** (strain gauge signal conditioning)
5. **PyTorch** (small models mapping sensor data to servo targets)
6. **Hugging Face LeRobot** (teleoperation and imitation learning tooling, used widely in the field)
7. **MuJoCo or Gazebo** (simulation of the hand, requires a URDF or MJCF model)
8. **CAD software** (Fusion 360, Onshape or SolidWorks) for the hand model and any redesigns

---

## Software Architecture (keep it ROS 2 ready)

Split the code into three modules with clear inputs and outputs. Each becomes one ROS 2 node later.

1. **hand_tracker:** camera frame in, 21 landmarks out
2. **retargeter:** landmarks in, finger curl values (0 to 1) and servo targets out, including calibration and filtering
3. **servo_driver:** servo targets in, bus commands out, position, load and temperature readings back

Timestamp every piece of data from day one.

---

## Phases

### Phase 1: Bench test one servo
1. Set a unique ID and baud rate with the Feetech debug tool
2. Command position from Python with scservo_sdk
3. Read back position, load and temperature
4. Add torque limit and temperature cutoff before anything else

### Phase 2: Camera only
1. Get live landmarks from MediaPipe on screen
2. Compute finger curl (0 to 1) from the angles between bone vectors
3. Plot curl values over time and check how noisy they are

### Phase 3: Open loop mirroring
1. Calibrate with an open hand and a closed fist
2. Apply a filter (One Euro filter or low pass) to remove jitter
3. Map curl to servo position per finger
4. Because the tendons are rigid, build a calibration curve per finger from measured data rather than assuming linear motion

### Phase 4: Closed loop and safety
1. Use load readings to detect a blocked finger
2. Log commanded versus measured position to measure backlash and dead zone
3. Add torque, temperature and range limits
4. Use sync write so all servos update together

### Phase 5: Data logging
1. Record human curl, commanded targets and measured positions with timestamps
2. Save to CSV, then to rosbag once on ROS 2
3. Keep sessions organised and named so they are reusable as a dataset

### Phase 6: Wrap in ROS 2
1. Turn the three modules into rclpy nodes
2. Define topics for landmarks, curl values, servo targets and servo state
3. Add a launch file and parameters file
4. Record and replay with rosbag2

### Phase 7: Strain gauges
1. Read gauges with an ESP32 or Teensy and an amplifier board
2. Stream timestamped values to the laptop over serial or USB
3. Calibrate against known angles or forces
4. Compare strain gauge control against camera control, then blend or replace

### Phase 8: Learning and simulation
1. Build a model of the hand in simulation (URDF or MJCF)
2. Train a small model, for example sensor values to servo targets
3. Explore LeRobot style teleoperation and imitation learning

---

## Common Pitfalls
1. A single camera has depth ambiguity. Wrist rotation and curled fingers can be noisy. A second camera is an easy upgrade.
2. Servo bus latency grows with the number of servos and baud rate. Use sync write.
3. Small servos overheat when held against a stall. Set torque limits early.
4. Tendon stretch and backlash change over time. Recalibrate and log it.
5. Power supply voltage drops under load can cause servo resets. Size the supply generously.

---

## Goals to Show and Record Robotics Skills

Each goal below has a measurable result that works as a CV line, a README section or a video.

### Measurable performance goals
1. **End to end latency:** measure camera frame to finger motion in milliseconds, then reduce it and document how
2. **Tracking error:** compare commanded versus measured finger position (mean and maximum error in degrees or percent)
3. **Repeatability:** run 100 open and close cycles and report the drift
4. **Calibration quality:** show before and after plots of the per finger calibration curve
5. **Thermal and load limits:** document safe continuous operation time and temperature

### Skills demonstration goals
1. **Control:** implement a closed loop with load feedback and compare to open loop
2. **Sensing:** fuse camera data with strain gauge data and show the difference
3. **Data:** produce a clean, timestamped dataset and publish it with a description
4. **Machine learning:** train a small model and report accuracy against the baseline mapping
5. **Simulation:** build a simulated hand and show the sim and real hand matching
6. **ROS 2:** publish a package with nodes, launch files and documentation
7. **Embedded:** write firmware for the strain gauge board with a documented data protocol

### Task level demonstrations
1. Pick up and place a set of objects (cup, ball, small box) and report success rate over many trials
2. Hand signs or counting from 1 to 5 mirrored live
3. Grip force control that holds an object without crushing it (needs strain gauges)
4. Teleoperation demo recorded as a video and a dataset

### Portfolio and career goals (humanoid companies)
1. Public GitHub repository with a clear README, architecture diagram and setup guide
2. A 2 to 3 minute demo video showing the pipeline and the numbers
3. A short write up of design decisions and failures, with plots (shows engineering judgment)
4. Add the project to your portfolio website with the key metrics at the top
5. CV bullets that state results, for example: "Built camera teleoperated robotic hand at X ms latency with Y degree tracking error"
6. Be ready to explain: retargeting, calibration, filtering, closed loop control, latency sources and what you would change in a second version

### Stretch goals
1. Add a second camera or depth camera for better 3D tracking
2. Add a wrist or arm so the hand can reach as well as grip
3. Try a data glove with bend sensors as a third input to compare
4. Compare your approach against the open source hand designs and tooling used in the field
5. Contribute a fix or improvement to an open source robotics repo you used

---

## Quick Checklist
- [ ] One servo moving from Python
- [ ] Live finger curl on screen
- [ ] Calibrated open loop mirroring
- [ ] Torque and temperature protection
- [ ] First logged dataset
- [ ] ROS 2 nodes running
- [ ] Strain gauge readout working
- [ ] Demo video and GitHub README published
