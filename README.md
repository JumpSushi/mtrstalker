# Mtracker


What is MTRacker? It is just a simple PCB design inspired by the ones on traintrackr.io for the Hong Kong MTR metro system.

You can find more information on the site:
https://jumpsushi.github.io/mtrstalker/

This design uses 66 addressable LEDS (WS2812E), to avoid the uneeded complexity of LED controllers, + you can change the color! I chose WS2812Es instead of the commonly seen and used WS2812B because of it's small form factor, while it still keeps all the benifits of the redesigned WS2812B.

This design also uses a ESP32-WROOM-32E, with an onboard antenna with 8MB of flash storage. It should be plenty, if not excessive. 

The full BOM (Bill of materials) can be found at: https://github.com/JumpSushi/mtrstalker/raw/refs/heads/main/pcb/bomtrackr.xlsx

The Schematic can be found at https://github.com/JumpSushi/mtrstalker/blob/main/pcb/SCH_Schematic1_2025-01-29.pdf

Thank you for reading this.

Lightbox for the images from https://cdnjs.com/libraries/lightbox2/2.11.3

gui.py was made with assistance from Artifical Stupidity (Intelligence)