# Lab 1 - Monitoring Equipment via WiFi
### Task 1
8. 
9. It connects to Kasa's servers through the home WiFi network the devices are connected to. I assume it's fairly secure. Kasa does not allow for custom server input or self-hosting features. Which would be to either self-host on your home network and open some ports, cloudflare tunnel, or even use a VPS.

### Task 2
12. It searches the host network/pings 255.255.255.255 which is the broadcast address of a network, meaning it sends packets of information to everyone on the network
13. `kasa --host _ip_add_` will ping _ip_add_ instead of broadcast address
14. basically does what `kasa` does
18. add functionality to plug04.py:
- control-c handler
- add energy report
- add watt hour calculation
### Task 3
21. add control-c handler to stop loop in plug05, times cant be very accurate due to the wait between `dev.update()` and `sleep`
