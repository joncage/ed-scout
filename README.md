# Elite Dangerous Scout

![GitHub](https://img.shields.io/github/license/joncage/ed-scout)
![Downloads](https://img.shields.io/github/downloads/joncage/ed-scout/total)
![Build Status](https://github.com/joncage/ed-scout/workflows/Build%20&%20Test/badge.svg)

Greetings commander and welcome to EDScout; an Elite Dangerous companion app to simplify finding unexplored worlds.

I got sick of jumping into system after system trying to find unexplored worlds to put my name to only to be disappointed because someone had already explored it. This tool is intended to help improve your odds of finding new and interesting systems and worlds to uncover.

Note that many systems out there have already been discovered by commanders who weren't running EDDiscovery / EDSM. Consequently there's no guarantee that the system you're about to leap into is _definitely_ new, but it certainly improves the chances. Conversely, if you're looking for guarantees that systems you're jumping to will make some money with a bit of scanning, this _will_ quickly show you some profitable route options (along the lines of the road to riches but with less typing).

Enjoy this tool? Consider..

* [Donating to EDSM](https://www.edsm.net/en_GB/donation)
* [Buying me a coffee](https://ko-fi.com/S6S8424WV)

..to the scout can keep flying :-) 

## Usage
 
1. If you don't already have it, install [Google Chrome browser](https://www.google.com/intl/en_uk/chrome/)
1. Download [the latest release of ED Scout](https://github.com/joncage/ed-scout/releases/latest)
1. Run `EDScout.exe`
1. Plot a new route in Galaxy Map and watch EDScout work it's magic; Scouting out which systems in your route have already been explored and how much mapping them is worth.

![Nav Route Example](Images/UIExplained.png)

\* Note: This refers to whether EDSM knew about the system. There are plenty of systems out there which have been discoverd by console players and PC players not running EDDiscovery etc.

## Command line options

If you want to make the web UI available to other devices on your network, you can specify a host (set this to [the IP address](https://www.google.com/search?q=how+to+find+the+ip+address+of+a+windows+computer) of the machine running EDSCout) and port as follows:

`EDScout.exe -port 12345 -host 192.168.1.31`

Assuming your computer's firewall allows it, you should then be able to access it from other devices on the local network. For example here it is displaying on my mobile:

![Connecting From Another Device On The Local Network](Images/RunningOnMobile.png)

## Troubleshooting

* No GUI appears.
    * Check you have Chrome installed.
    * Check the logs in `C:\Users\<YOUR USER NAME>\AppData\Local\EDScout\Logs\EDScout-YYYY-MM-DD-HH-MM-SS.log` for clues.
* Multiple entries appear in task manager.
    * This is  normal (due to the architecture of the software) and is down to the fact we have a Python back end doing the hard work and a chrome instance displaying the results.
* When I launch multiple copies, the second one crashes.
    * This is due to the way a background watcher looks for changes in the navroute files and (via a local network link) hands over the data to the web service. Don't run more than one copy and it'll work fine :-)

## Version History

See https://github.com/joncage/ed-scout/releases
