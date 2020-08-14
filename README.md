# Elite Dangerous Scout


Greetings commander and welcome to EDScout; an Elite Dangerous companion app to simplify finding unexplored worlds.

I got sick of jumping into system after system trying to find unexplored worlds to put my name to only to be disappointed because someone had already explored it. This tool is intended to help improve your odds of finding new and interesting systems and worlds to explore.

Note that many systems out there have already been discovered by commanders who weren't running EDDiscovery / EDSM. Consequently there's no guarantee that the system you're about to leap into is _definitely_ new, but it certainly improves the chances. Conversely, if you're looking for guarantees that systems you're jumping to will make some money with a bit of scanning, this _will_ quickly show you some profitable route options (along the lines of the road to riches but with less typing).

Enjoy this tool? Consider [donating to EDSM](https://www.edsm.net/en_GB/donation) so the scout can keep flying :-) 

## Usage
 
1. If you don't already have it, install [Google Chrome browser](https://www.google.com/intl/en_uk/chrome/)
1. Download [the latest release of ED Scout](https://github.com/joncage/ed-scout/releases/download/v1.2.0/EDScout.exe)
1. Run `EDScout.exe`
1. Plot a new route in Galaxy Map and watch EDScout work it's magic; Scouting out which systems in your route have already been explored and how much mapping them is worth.

![Nav Route Example](Images/NavRouteDisplay.png)

## Key

* Grey rows indicate explored systems
* Coloured lines indicate systems that (according to EDSM) have not been mapped.
* Main star types for each system are listed in the first column.
* Mapped value of systems (for those that have already been discovered) are displayed in the right-most column.

## Command line options

If you want to make the web UI available to other devices on your network, you can specify a host (set this to [the IP address](https://www.google.com/search?q=how+to+find+the+ip+address+of+a+windows+computer) of the machine running EDSCout) and port as follows:

`EDScout.exe -port 12345 -host 192.168.1.31`

Assuming your computer's firewall allows it, you should then be able to access it from other devices on the local network. For example here it is displaying on my mobile:

![Connecting From Another Device On The Local Network](Images/RunningOnMobile.png)

## Troubleshooting

* No GUI appears.
  * Check you have Chrome installed.
  * Check the logs in `C:\Users\<YOUR USER NAME>\Documents\EDScout\EDScout.log` for clues.
* Multiple entries appear in task manager.
  * This is  normal (due to the architecture of the software) and is down to the fact we have a Python back end doing the hard work and a chrome instance displaying the results.
* When I launch multiple copies, the second one crashes.
  * This is due to the way a background watcher looks for changes in the navroute files and (via a local network link) hands over the data to the web service. Don't run more than one copy and it'll work fine :-)

## Version History

### 1.1.0 - More options

* Added commandline options to set port and host to enable external devices to connect to the UI.
* Fixed a crash when multiple instances are opened.

### 1.0.0 - Initial release

* Written in Python.
* Basic GUI  is operational using a combination of Flask, ZMQ and SocketIO.
* Watches `C:\Users\<USER>\Saved Games\Frontier Developments\Elite Dangerous\NavRoute.json` for changes then queries EDSM for all the systems in the route to check their value.
* Packaged up using PyInstaller. 
