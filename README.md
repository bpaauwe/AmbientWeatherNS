
# AmbientWeather-polyglot

This is the Ambient Weather Poly for various [Ambient Weather stations] (https://www.ambientweather.com/) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)
(c) 2018 Robert Paauwe
MIT license.

This node server is intended to support the [Ambient Weather Station](http://www.ambientweather.com/). 

[EXPERIMENTAL]
I don't have an Ambient Weather station and am currently unable to do additional development or debug of this node server.

## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
   * After the install completes, Polyglot will reboot your ISY, you can watch the status in the main polyglot log.
4. Configure the node server. You will need to add your stations's mac address and your API key. You can also adjust the longpoll value. The minimum polling interval supported by the Ambient Weather API is 60 seconds.
5. Once your ISY is back up open the Admin Console.
6. There should be an Ambient controll node with various weather sensor related sub nodes.

### Node Settings
The settings for this node are:

#### Short Poll
   * Not used.
#### Long Poll
   * How often the node server will poll the Ambient Weather servers for data.
#### Mac Address (key = macAddress)
   * The mac address of the station you want to monitor.
#### API Key (key = APIKey)
   * Your Ambient Weather account API Key. This authorizes the node server to access your weather data.


## Requirements

1. Polyglot V2 itself should be run on Raspian Stretch.
  To check your version, ```cat /etc/os-release``` and the first line should look like
  ```PRETTY_NAME="Raspbian GNU/Linux 9 (stretch)"```. It is possible to upgrade from Jessie to
  Stretch, but I would recommend just re-imaging the SD card.  Some helpful links:
   * https://www.raspberrypi.org/blog/raspbian-stretch/
   * https://linuxconfig.org/raspbian-gnu-linux-upgrade-from-jessie-to-raspbian-stretch-9
2. This has only been tested with ISY 5.0.13 so it is not guaranteed to work with any other version.

# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "AmbientWeather".

For Polyglot 2.0.35, hit "Cancel" in the update window so the profile will not be updated and ISY rebooted.  The install procedure will properly handle this for you.  This will change with 2.0.36, for that version you will always say "No" and let the install procedure handle it for you as well.

Then restart the AmbientWeather nodeserver by selecting it in the Polyglot dashboard and select Control -> Restart, then watch the log to make sure everything goes well.

The AmbientWeather nodeserver keeps track of the version number and when a profile rebuild is necessary.  The profile/version.txt will contain the AmbientWeather profile_version which is updated in server.json when the profile should be rebuilt.

# Release Notes

- 0.1.11 9/05/2020
   - Trap error when server sends no data.
- 0.1.10 1/29/2020
   - Trap errors with connecting to Ambient servers.
- 0.1.9 12/27/2019
   - Enable solar radiation reporting if it exists in the data.
- 0.1.8 11/30/2019
   - Check for barometric pressure before trying to calculate trend.
   - Change missing entries from error to warning.
- 0.1.7 11/29/2019
   - Add configurable indoor sensor node
   - Stop forcing all values to be sent every time.
- 0.1.6 11/26/2019
   - Clean up profile files.
- 0.1.5 10/25/2019
   - Improve custom parameter handling for cloud.
- 0.1.4 10/24/2019
   - Improve notices and custom parameter handling.
- 0.1.3 10/21/2019
   - Use correct module import for polyglot cloud.
- 0.1.2 03/20/2019
   - Fix online status going false after query.
- 0.1.1 09/14/2018
   - Fix URL path
- 0.1.0 09/12/2018
   - Initial version published in the Polyglot node server store
