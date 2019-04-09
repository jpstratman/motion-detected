# motion-detected
Python script to be run when motion is detected and image is captured

Run with command `python3 /home/pi/.motion/on-motion.py -f file_location` replacing file_location with absolute path of image file.

Environment variables must be defined for the following before running:
- DROPBOX_ACCESS_TOKEN
- SENDER_EMAIL
- SENDER_AUTH
- TWILIO_SID
- TWILIO_AUTH_TOKEN
- TWILIO_DESTINATION
- TWILIO_SOURCE
