# AlexaBeagleBone
 
---
 
### Contributors
 
* Sam Machin
* Mike Erdahl
 
---
 
This is the code needed to Turn a BeagleBone into a client for Amazon's Alexa 
service.  This project is largely the work of Sam Machin, with minor changes to
support BeagleBone GPIO using the Adafruit-BBIO library and USB audio.  GPIO 
events are employed rather than polling so we do not tie up our only core :)

Tested and working on a BeagleBone Black running Debian Wheezy 7.9 (Linux kernel 
3.8) from Beagleboard.org, with Sabrent USB Audio.  Other versions of Linux 
kernel should be OK, provided comptible GPIO library is used.

Note: Kernel version 4.x changed the path to GPIO file desciptors.  As of this
writing, several GPIO libraries are broken.

Special thanks to Sam Machin for a great starting point for us Beagle
enthusists!

---
 
### Requirements

You will need:
* A BeagleBone (white, black, green, etc)
* An SD Card with Debian Wheezy 7.9 from Beagleboard.org
* An External Speaker with 3.5mm Jack
* A USB Sound Dongle and Microphone
* A push to make button connected between GPIO0_7 and GND
* (Optionally) A Dual colour LED (or 2 signle LEDs) Connected to 
  GPIO0_30 and GPIO1_28


Next you need to obtain a set of credentials from Amazon to use the Alexa Voice
Service, login at http://developer.amazon.com and Goto Alexa then Alexa Voice 
Service You need to create a new product type as a Device, for the ID use 
something like AlexaPi, create a new security profile and under the web settings
allowed origins put http://localhost:5000 and as a return URL put 
http://localhost:5000/code you can also create URLs replacing localhost with the
IP of your Pi  eg http://192.168.1.123:5000

Make a note of these credentials you will be asked for them during the install 
process

### Installation

Boot your fresh BeagleBone and login to a command prompt as root.

Make sure you are in /root

Clone this repo to the Pi
`git clone https://github.com/merdahl/AlexaPi.git`
Run the setup script
`./setup.sh`

Follow instructions....

Enjoy :)

### Changelog

Version 0.1

* Alexa volume commands adjust volume without interrupting stream
* iHeartRadio tested extensively - Alexa will properly add stations you request
* New audio stream requests will stop currently playing stream and start

Known Issues

* becoming clear several objects need to be created to clean up code
* CPU usage still seems too high - ranges from ~70-80% at 1GHz
* probably many more!


### Issues/Bugs etc.

If your alexa isn't running on startup you can check /var/log/alexa.log for
errrors.

If the error is complaining about alsaaudio you may need to check the name of
your soundcard input device, use 
`arecord -L` 
The device name can be set in the settings at the top of main.py 

You may need to adjust the volume and/or input gain for the microphone, you can
do this with 
`alsamixer`

### Advanced Install

For those of you that prefer to install the code manually or tweak things here's
a few pointers...

The Amazon AVS credentials are stored in a file called creds.py which is used by
auth_web.py and main.py, there is an example with blank values.

The auth_web.py is a simple web server to generate the refresh token via oAuth
to the amazon users account, it then appends this to creds.py and displays it on
the browser.

main.py is the 'main' alexa client it simply runs on a while True loop waiting
for the button to be pressed, it then records audio and when the button is
released it posts this to the AVS service using the requests library, When the
response comes back it is played back using vlc.

iHeartRadio streaming was tested and seems to work great, with the exception of 
voice commands, like "volume up".  Attempting to change volume via AVS will kill
the audio stream.

The LED's are a visual indictor of status, I used separate LEDS connected to 
GPIO1_28 and GPIO0_30.  When recording, GPIO1_28 will be asserted.  When the 
recording file is being posted and waiting for the response, both GPIOs are 
asserted.  When the response is played GPIO0_30 is asserted. If The client gets 
an error back from AVS then the GPIO0_30 will flash 3 times.

The internet_on() routine is testing the connection to the Amazon auth server as
I found that running the script on boot it was failing due to the network not 
being fully established so this will keep it retrying until it can make contact
before getting the auth token.

The auth token is generated from the request_token the auth_token is then stored
in a local memcache with and expiry of just under an hour to align with the 
validity at Amazon, if the function fails to get an access_token from memcache 
it will then request a new one from Amazon using the refresh token.








---
 

