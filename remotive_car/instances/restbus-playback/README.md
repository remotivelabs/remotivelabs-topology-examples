## Summary

This is a very simple example with a single CAN channel that can optionally be connected to a hardware channel. The data that is sent on the CAN channel originates from a previously recorded drive cycle.

### CAN over UDP

If you run this on macOS or Linux with CAN over UDP you will not be able to interface with real hardware. However, you can look at the signals in the web UI to get an understanding of the setup.

1. Generate the topology for CAN over UDP

   ```
   remotive-topology generate \
   -f remotive_car/instances/restbus-playback/main.instance.yaml \
   -f remotive_car/instances/can_over_udp.instance.yaml \
   build
   ```

2. Run it
   ```
   docker compose \
   -f build/restbus-playback/docker-compose.yml \
   --profile ui \
   --profile playback \
   up
   ```
3. Now you can view data by going to the web UI at http://localhost:8080.

### CAN (dockercan) to hardware

If you run this example you will be able to interface with the hardware.

1. Update the example with the details of your setup. There are 3 places you might have to make changes to. Simply search for `# TODO: ` to find all occurrences:

   - In _remotive_car/platform/restbus-playback.platform.yaml_ make sure that the baud rate matches the hardware
   - In _remotive_car/instances/restbus-playback/playback/local/tcu.py_ make sure that the name of the location CAN frame matches your signal database
   - In _remotive_car/instances/restbus-playback/main.instance.yaml_ uncomment line 24-29 and make sure that the device name matches the name assigned to your CAN interface. For example, if your host interface is can0, set the device name to can. A "0" will be appended to the device name automatically.

2. Generate the topology for CAN
   ```
   remotive-topology generate \
   -f remotive_car/instances/restbus-playback/main.instance.yaml \
   build
   ```
3. Run it
   ```
   docker compose \
   -f build/restbus-playback/docker-compose.yml \
   --profile ui \
   --profile playback \
   up
   ```
4. Now you can run `candump any` to verify that CAN frames are being transmitted.

   If everything is set up correctly, your AAOS stack should also show location data.

   You can of course also view the data in the web UI at http://localhost:8080.
