# ed-scout
An Elite Dangerous companion app to simplify finding unexpored worlds.

I got sick of jumping into system after system trying to find unexplored worlds to put my name to only to be disappointed because someone had already explored it. This tool is intended to help improve your odds of finding new and interesting systems and worlds to explore.

Note that many systems out are discovered by commanders who weren't running EDDiscory / EDSM. Consequently it's not a foolproof guarantee that the system you're about to leap into is definitely new, but it certainly improves the chances. Conversely, if you're looking for guarantees that a system you're jumping to will make some money, this can quickly show you some profitable route options (along the lines of the road to riches).

## Running The Scout

### Usage
 
1. Call `python WebUI.py`
2. Connect to the new web service with your browser pointed at http://127.0.0.1:5000/
3. Plot a new route in Galaxy Map. Each time you do, you should be greeted with something along the following lines:

![Nav Route Example](Images/NavRouteDisplay.png)

### Key

* Grey rows indicate explored systems
* Coloured lines indicate systems that (according to EDSM) have not been mapped.
* Main star types for each system are listed in the first column.
* Mapped value of systems (for those that have already been discovered) are displayed in the right-most column. 
