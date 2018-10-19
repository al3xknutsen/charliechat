# CharlieChat

**_WARNING: THIS SOFTWARE WAS CREATED PURELY AS A HOBBY PROJECT AND IS NOT INTENDED FOR PRODUCTION ENVIRONMENTS. USE AT YOUR OWN RISK._**

_NB: Voice and webcam are experimental features, and are to be considered non-functional!_

CharlieChat is an instant messaging software, building on the client-server networking principle. It was created as a hobby project, as a more lightweight alternative to most messaging software existing at the time.

# Prerequisites
This project requires Python 2 in order to run (tested with Python 2.7.15). In addition, the following packages need to be installed:
* wxPython 2.9 (tested with 2.9.5.0)
* pyCrypto (tested with version 2.6.1)
* pywin32 (tested with version 224)
* pyHook (tested with version 1.5.1)
* pyAudio (tested with version 0.2.11)
* openCV (tested with version 2.4.13.5)
* numpy (tested with version 1.15.1)

# Starting the program
First, you need to start the server program. You can either use a dedicated server for this, or start it from your local machine (note that nobody but yourself will be able to connect to your local machine unless you use port-forwarding or similar methods). To start the server, simply run the file `Server\server.py`.

To start the client, simply run the file `Client\CharlieChat.py`. By default, the client will try to connect to a server located on localhost. To change this, you need to go into the file `Client\core\global_vars.py` and change the `host` variable to the desired hostname.
