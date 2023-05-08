Welcome, this repo contains a radio scanner for rtl-sdr written in Python with a PyQt interface.
It is not finished yet... need to add hormanic identification of interferance signals... and fine tune it more to work with different gain levels, etc.

How to use: just run it.

Science:

Dependancies:

Fun stuff:

![Screenshot from 2023-05-05 00-11-26(1)](https://user-images.githubusercontent.com/102178068/236400169-979d01af-0014-40f0-8a7a-f11735689ebd.jpg)

Not sure who was broadcasting during time of test... but found it funny ;) 
...and yes I know the frequency capability is approximately 65MHz-2300MHz (more so, I found the Elonics E4000 tuner has a valid frequency range of approximately 52 MHz to 2200 MHz), with small frequency gap near 1100MHz. But I also have a Ham It Up Plus Upconverter.
Which reminds me I should make a list of items.

https://user-images.githubusercontent.com/102178068/236401163-5ef5e1e3-a66e-4481-bade-8b1ce7d79012.mp4

List of items used:
https://www.nooelec.com/store/nesdr-smartee-xtr-sdr.html
https://www.nooelec.com/store/ham-it-up-plus.html
https://www.nooelec.com/store/balun-one-nine.html
Aluminum or Copper wire... yes you can make an antenna out of tinfoil if you do not want to go buy one.

I REALLY DO NOT RECOMMEND DOING THIS UNLESS YOU KNOW WHAT YOU ARE DOING but...
You can also use your body as an antenna (if you touch the wire hanging out of the 9:1 balun), although not recommended... because it can radiate a bit.

Using the human body as an antenna with a software-defined radio (SDR) is an interesting concept,it's important to understand the science behind it to make it work effectively.

The human body is primarily composed of water, and water is an effective conductor of electricity due to the dissolved ions it contains. This conductivity property allows the human body to act as an antenna, albeit not a very efficient one.

When you use your body as an antenna, you essentially turn your body into a large, conductive surface that can pick up electromagnetic waves from the environment. Here's a brief explanation of how this works:

    Resonance: Your body can resonate at certain frequencies, depending on its size and shape. When an electromagnetic wave passes through your body, it induces a current that can resonate at the frequency of the incoming signal.

    Capacitive coupling: Your body can also act as a capacitor, storing and releasing electrical energy. As you move around, your body capacitively couples with nearby electrical fields and can pick up signals from the environment.

    Inductive coupling: Finally, your body can also act as an inductor, generating an electromagnetic field when current flows through it. This property allows your body to pick up signals through inductive coupling.

To use your body as an antenna with an SDR, you can simply connect the SDR's antenna input to a conductive point on your body, such as a metal bracelet or a conductive adhesive pad. Keep in mind that the performance of a human body as an antenna will likely be inferior to a purpose-built antenna designed for specific frequency ranges and applications.

However, it's worth noting that using your body as an antenna can potentially expose you to higher levels of electromagnetic radiation, which may not be safe in the long run. It's essential to exercise caution and adhere to safety guidelines when experimenting with this kind of setup.
