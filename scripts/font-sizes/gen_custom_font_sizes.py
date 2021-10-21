#!/usr/bin/env python3

# Note, the following script must be used with Python 3.7+

comment_old = '''  # Font sizes depend on the device's screen density. Unpatched, the sizes
  # increase in steps of 1 from the smallest size up to size {}, then in steps
  # of 2 up to size {}, then in steps of 4 up to the largest size:'''

comment_new = '''  # The example replacement values in this patch result in the following ranges,
  # with increases in steps of 1 from the smallest size up to size {}, then
  # steps of 2 up to size {}, then steps of 4 up to the largest size:'''

# Important device codenames for this script
models = {
    'Touch': ['trilogy'],
    'Mini': ['trilogy'],
    'AuraHD': ['dragon'],
    'AuraH2O': ['dragon'],
    'GloHD': ['alyssum', 'dragon'],
    'ClaraHD': ['nova', 'dragon'],
    'LibraH2O': ['storm', 'dragon'],
    'AuraOne': ['daylight'],
    'Forma': ['daylight'],
    'Aura': ['phoenix'],
    'Glo': ['phoenix'],
    'Nia': ['phoenix'],
    'Elipsa': ['daylight'],
    'Sage': ['daylight'],
    'Libra2': ['dragon']
}

def calc_steps(min: int, max: int, limits: list):
    num_steps = 0
    size = min
    while size <= limits[0]:
        num_steps += 1
        size += 1
    size = limits[1]
    while size <= limits[2]:
        num_steps += 1
        size += 2
    size = limits[3]
    while size <= max:
        num_steps += 1
        size += 4
    return num_steps

def get_values(vals: "dict[str: list]", add_to_offset=True):
    for k in vals:
        inp = input(f'({k}) <offset> [new_size ({vals[k][1]})] [orig_size ({vals[k][0]})]: ').split()
        if len(inp) == 0:
            raise ValueError
        i = 2
        for val in inp:
            val = int(val, 0)
            if i == 2 and add_to_offset:
                val += 2
            vals[k][i] = val
            i -= 1

def main():
    min_values = {
        'other': [8, 8, int('0x01', 16) + 2],
        'storm': [11, 11, int('0x02', 16) + 2],
        'alyssum nova': [10, 10, int('0x03', 16) + 2],
        'daylight': [14, 14, int('0x04', 16) + 2]
    }
    max_values = {
        'other': [90, 80, int('0x05', 16) + 2],
        'phoenix': [122, 88, int('0x06', 16) + 2],
        'dragon': [150, 108, int('0x07', 16) + 2],
        'daylight': [195, 132, int('0x08', 16) + 2]
    }

    limits = {
        1: [21, 43, int('0x09', 16), 'Add font sizes in increments of 1 until this size exceeded'],
        2: [22, 44, int('0x0a', 16), 'Continue from this font size'],
        3: [49, 67, int('0x0b', 16), 'Add font sizes in increments of 2 until this size exceeded'],
        4: [50, 68, int('0x0c', 16), 'Continue from this font size']
    }
    try:
        print("\nEnter values and offsets for device specific min font sizes. \nNote, +2 will be automatically added to offset when required\n")
        get_values(min_values)

        print("\nEnter values and offsets for device specific max font sizes. \nNote, +2 will be automatically added to offset when required\n")
        get_values(max_values)
            
        print("\nEnter values and offsets for the following limits\n")
        get_values(limits, add_to_offset=False)

    except ValueError as ve:
        print("Using Test values!")

    # Print the patch values

    print('The following lines should be added to the "Custom font sizes" patch')
    print('')
    print('  # Initial font size:')
    for val in min_values.values():
        print(f'  - ReplaceInt: {{Offset: {val[2]}, Find: {val[0]}, Replace: {val[1]}}}')
    print('  # Increment:')
    for val in limits.values():
        print(f'  - ReplaceInt: {{Offset: {val[2]}, Find: {val[0]}, Replace: {val[1]}}} # {val[3]}')
    print('  # Now increment by +4 until final font size:')
    for val in max_values.values():
        print(f'  - ReplaceInt: {{Offset: {val[2]}, Find: {val[0]}, Replace: {val[1]}}}')

    # Calculate and print the help string
    orig_ranges: dict[tuple: list] = {}
    new_ranges: dict[tuple: list] = {}
    for device, code_names in models.items():
        orig_min = 0
        new_min = 0
        orig_max = 0
        new_max = 0

        for code in code_names:
            c = code
            if code in ['alyssum', 'nova']:
                c = 'alyssum nova'
            if c in min_values:
                orig_min = min_values[c][0]
                new_min = min_values[c][1]
                break
        if orig_min == 0 or new_min == 0:
            orig_min = min_values['other'][0]
            new_min = min_values['other'][1]
        
        for code in code_names:
            if code in max_values:
                orig_max = max_values[code][0]
                new_max = max_values[code][1]
                break
        if orig_max == 0 or new_max == 0:
            orig_max = max_values['other'][0]
            new_max = max_values['other'][1]
        
        orig_range = (orig_min, orig_max)
        new_range = (new_min, new_max)
        if orig_range not in orig_ranges:
            orig_ranges[orig_range] = []
        if new_range not in new_ranges:
            new_ranges[new_range] = []
        orig_ranges[orig_range].append(device)
        new_ranges[new_range].append(device)

    print('\nThe following lines should be added to the "Custom font sizes" comments\n')
    limits_orig = [limits[1][0], limits[2][0], limits[3][0], limits[4][0]]
    limits_new = [limits[1][1], limits[2][1], limits[3][1], limits[4][1]]
    print(comment_old.format(limits_new[1], limits_new[3]))
    print('  #')

    for range, devices in orig_ranges.items():
        dev = '/'.join(devices)
        steps = calc_steps(range[0], range[1], limits_orig)
        print(f'  # {dev:>30}:  {range[0]:3}px - {range[1]:3}px  ({steps} steps)')
    print('  #')
    print(comment_new.format(limits_new[1], limits_new[3]))
    print('  #')

    for range, devices in new_ranges.items():
        dev = '/'.join(devices)
        steps = calc_steps(range[0], range[1], limits_new)
        print(f'  # {dev:>30}:  {range[0]:3}px - {range[1]:3}px  ({steps} steps)')

if __name__ == '__main__':
    main()