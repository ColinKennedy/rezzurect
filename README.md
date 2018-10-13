REZZURECT_STRATEGY_ORDER
REZZURECT_LOG_PATH

TODO :
- Make the logger inheritable
- Get FTP downloading to work (on my local machine, to start)
 - Get a progress-bar working
 - Deal with authentication later
- Move "strategies" into the Nuke adapter, instead of keeping it global
 - Once done, delete the PassthroughAdapter for the Nuke package
 - Add env-vars which can be used to override the strategies - globally and per-package

- needs more logging, in general
- Add documentation about the environment variables
- Fix the issue where Nuke is being installed to the nuke/11.2v3 folder. It
  should go in the "install" folder instead
- Add the ability to "link" to a local install, instead of building from scratch

- create a SSH server on my laptop and make my main machine "clone" from it as part of installation(!)
 - If that works, that'd be sick

- add a “clean”attribute to force the install path to clean itself up
- add progress bar for unzipping!

- Get it to work with Windows

- Check out how to add tools as packages onto a Nuke installation, using Rez
- Check the code to make sure it's organized
- 
