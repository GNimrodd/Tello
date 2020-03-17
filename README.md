# Tello
a python controller for DJI-Tello Drone. Aimed to be used along with: https://github.com/GNimrodd/tello_slam

The drone is controlled with the keyboard (hit h for help after running the initial command).

In slam mode, the drone camera is displayed through the slam-app, and without slam, through the python script.

## Deployment

In the file lsd_slam/lsd_slam.py, change CALIBRATION_FILE, LSD_SLAM_LIVE_APP, LSD_SLAM_OFFLINE_APP to the path of your compiled slam app.

## Running Tello
(in square brackets: optional)
python main.py --ssid <tello wifi address> \[--with-camera] \[--lsd-slam]

to capture images automaticly, add to the command line:
capture_frame frame_dir=<dir path> frame_capture_rate=<capture frame every x seconds>

** the auto-connect to wifi sometimes has troubles. You can manualy connect to the drone and then run the script if it happens.
** the start might take up to 10-15 seconds, have patience

In this repository you can find an example of feeding the video stream to create a point cloud, which is the base for many other visual applications.
