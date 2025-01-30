# Mtracker


What is MTRacker? It is just a simple PCB design inspired by the ones on traintrackr.io for the Hong Kong MTR metro system.

You can find more information on the site:
https://jumpsushi.github.io/mtrstalker/

This design uses 66 addressable LEDS (WS2812E), to avoid the uneeded complexity of LED controllers, + you can change the color! I chose WS2812Es instead of the commonly seen and used WS2812B because of it's small form factor, while it still keeps all the benifits of the redesigned WS2812B.

This design also uses a ESP32-WROOM-32E, with an onboard antenna with 8MB of flash storage. It should be plenty, if not excessive. 

I've also built a python script that tracks the location, as the physical version won't arrive before High Seas ends. A web version is now avalible here!

https://jumpsushi.github.io/mtrstalker/tracker.html



The python script can be found under the folder "script". Downlaod both, and run "gui.py".

The full BOM (Bill of materials) can be found at: https://github.com/JumpSushi/mtrstalker/raw/refs/heads/main/pcb/bomtrackr.xlsx

The Schematic can be found at https://github.com/JumpSushi/mtrstalker/blob/main/pcb/SCH_Schematic1_2025-01-29.pdf

Thank you for reading this.

You might of noticed a folder named server. Well.... long story short, I was having some issues with the MTR API, and I thoght it was a cors error. So then I dedicated 3 hours of my life trying to build a backend on nest to prase the data and make my own mtr next train api. Turns out, I'm an idiot, and I put station in the URL instead of "sta" as stated in the documentaition. Anyways, the server should work (in theory), but I haven't tested it.

Lightbox for the images from https://cdnjs.com/libraries/lightbox2/2.11.5 (updated from 2.11.3, didn't realise a new one exsisted.)
moment.js for dispalying dates on tracker.html from https://cdnjs.com/libraries/moment.js 
Tracker.html was worked on another editor, so unfortunatley, some of the hours didn't count 

gui.py was made with assistance from Artifical Stupidity (Intelligence)