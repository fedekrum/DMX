import argparse
import asyncio
from pyartnet import SacnNode
import sys

def read_single_keypress():
    """Read a single keypress from the user."""
    if sys.platform.startswith('win'):
        import msvcrt
        key = msvcrt.getch()
        return key in [b'\r', b'\n', b' ']
    else:
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            key = sys.stdin.read(1)
            return key in ['\r', '\n', ' ']
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

""" async def animate_channel(node, universe_number, channel_number, animation_speed):
    # Get the universe
    universe = node.get_universe(universe_number)

    # Create the channel name based on the channel number
    channel_name = f'channel_{channel_number}'
    channel = universe.add_channel(start=channel_number, width=1, channel_name=channel_name)

    # Create the sequence of values: from 0 to 254 and then back to 0, jumping by 4
    sequence = list(range(0, 255, 4)) + list(range(254, -1, -4))

    # Calculate the waiting time to distribute the values over the animation speed
    delay = animation_speed / 1000 / len(sequence)  # Convert ms to seconds

    # Send the values
    for value in sequence:
        channel.set_values([value])
        await asyncio.sleep(delay) """

async def animate_channel(node, universe_number, channel_number, animation_speed):
    # Get the universe
    universe = node.get_universe(universe_number)

    # Create the channel name based on the channel number
    channel_name = f'channel_{channel_number}'
    channel = universe.add_channel(start=channel_number, width=1, channel_name=channel_name)
    delay = animation_speed / 1000

    # Send value 255
    channel.set_values([255])

    # Pause for 2 seconds
    await asyncio.sleep(delay)

    # Send value 0
    channel.set_values([0])

    # Pause for 2 seconds
    await asyncio.sleep(delay)


async def main(args):
    # Create the sACN node
    node = SacnNode(args.address, 5568)

    # Create the specified universe
    universe = node.add_universe(args.universe)

    # Start the refresh task
    node.start_refresh()

    if args.channel is not None:
        # If a channel is specified, determine the end channel based on the range
        end_channel = args.channel + (args.range if args.range is not None else 1)
        for ch in range(args.channel, end_channel):
            if args.key_pause:
                print(f"Press key to start animation in Universe {args.universe}, Channel {ch}", end='', flush=True)
                while not read_single_keypress():
                    pass
                print()  # Move to the next line after key press
            else:
                print(f"Starting animation in Universe {args.universe}, Channel {ch}")
            await animate_channel(node, args.universe, ch, args.speed)
    else:
        # If no channel is specified, iterate over the channels up to the specified range or default to 512
        range_limit = args.range if args.range is not None else 512
        for ch in range(1, range_limit + 1):
            if args.key_pause:
                print(f"Press key to start animation in Universe {args.universe}, Channel {ch}", end='', flush=True)
                while not read_single_keypress():
                    pass
                print()  # Move to the next line after key press
            else:
                print(f"Starting animation in Universe {args.universe}, Channel {ch}")
            await animate_channel(node, args.universe, ch, args.speed)

    # Stop the refresh task
    node.stop_refresh()

def check_universe(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 63999:
        raise argparse.ArgumentTypeError(f"{value} is not a valid universe number. Must be between 1 and 63999.")
    return ivalue

def check_channel(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 512:
        raise argparse.ArgumentTypeError(f"{value} is not a valid channel number. Must be between 1 and 512.")
    return ivalue

def check_range(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 512:
        raise argparse.ArgumentTypeError(f"{value} is not a valid range number. Must be between 1 and 512.")
    return ivalue

# Parse command line arguments
parser = argparse.ArgumentParser(description='Scans DMX channels with PyArtNet.')
parser.add_argument('-a', '--address', type=str, required=True, help='IP address or hostname of the sACN node')
parser.add_argument('-u', '--universe', type=check_universe, required=True, help='DMX universe number (1-63999)')
parser.add_argument('-c', '--channel', type=check_channel, default=None, help='DMX channel number (1-512), optional')
parser.add_argument('-r', '--range', type=check_range, default=None, help='Range of channels to animate (1-512), optional')
parser.add_argument('-s', '--speed', type=int, default=500, help='Animation speed in milliseconds (default 500ms)')
parser.add_argument('-k', '--key-pause', action='store_true', help='Require key press to start animation for each channel')

try:
    # Get the arguments
    args = parser.parse_args()
except argparse.ArgumentError as e:
    parser.error(str(e))

try:
    # Run the main function in the asyncio event loop
    asyncio.run(main(args))
except KeyboardInterrupt:
    print("\nProgram interrupted by the user. Exiting...")
    # Here you can add any necessary cleanup or closing before exiting
