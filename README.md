This is a WIP repository and is still in active development. Check
out its parent repository [Respawn](https://github.com/ColinKennedy/tk-config-default2-respawn)
for more details.


# Logging
The central logger that rezzurect uses is located in utils/logger.py. 
`logger.init()` is run early on in the installation process and sets up all of
the loggers in the repository.

Any logger whose name is prefixed with "rezzurect." will automatically get the
settings of the parent logger.

Any project-wide changes to the logging system of rezzurect can be done from
logger.py.


# Configuration
REZZURECT_STRATEGY_ORDER
REZZURECT_LOG_PATH


# Checkout (TODO)
- Get it to work with Windows
- Make sure that Nuke depends upon (and installs) libGLU
 - Otherwise this happens: "Failed to load libstudio-11.2.3.so: libGLU.so.1: cannot open shared object file: No such file or directory"
- Right now the Nuke package gets a "install" folder built, even though it
  doesn't use it. Remove it
- The whole repo needs more logging, in general
- Add documentation about the environment variables
- add progress bar for unzipping!
