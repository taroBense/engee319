import csv
import time

csv_file = open('power_consumption.csv', mode='w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Time', 'Current', 'Voltage', 'Power'])
# obtained from cli command or plug01.py
dev_ip = '192.168.1.69'

# Make a connection to the energy monitoring plug
async def main():
    dev = await Discover.discover_single(dev_ip)

    for count in range(0, 20):
        print(count)

    # Obtain an energy reading (current, voltage, power)
        e_module = dev.modules.get("Energy")
        await dev.update()
		
        csv_writer.writerow([int(time.time()),
                        e_module.current,
                        e_module.voltage,
                        e_module.current*e_module.voltage])
        time.sleep(5)

    csv_file.close()

if __name__ == "__main__":
    asyncio.run(main())