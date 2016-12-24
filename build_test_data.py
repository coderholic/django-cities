import mmap
import os
import re
import sys

from tqdm import tqdm

from cities.conf import files


def get_line_number(file_path):
    with open(file_path, 'r+') as fp:
        buf = mmap.mmap(fp.fileno(), 0)
        lines = 0
        while buf.readline():
            lines += 1
        return lines


try:
    original_file = sys.argv[1]
except IndexError:
    original_file = None

test_data_dir = os.path.join('test_project', 'data')

new_filename = '{}.new'.format(os.path.basename(original_file))
new_filepath = os.path.join(test_data_dir, new_filename)

# Luckily this regex applies to both hierarchy.txt and alternativeNames.txt
file_rgx = re.compile(r'^(?:[^\t]+\t){1}([^\t]+)\t(?:en|und|ru|adm|\t)',
                      re.IGNORECASE | re.UNICODE)

# Bail early if we haven't been given a file to read
if original_file is None:
    print("You must specify the full original file (usually hierarchy.txt or "
          "alternativeNames.txt) as the first argument.\n\nExiting.")

    exit(-1)

# Bail early if the file exists
if new_filepath and os.path.exists(new_filepath):
    print("This script writes {}, but that file already exists. Please move "
          "(or remove) that file and rerun this script.\n\nExiting.".format(
              new_filepath))

    exit(-1)

# Read all of the affected geonameids
geonameids = []
for _type in ('region', 'subregion', 'city'):
    filename = files[_type]['filename']
    filepath = os.path.join(test_data_dir, filename)

    column = files[_type]['fields'].index('geonameid')

    rgx = re.compile(r'^(?:[^\t]+\t){{{}}}([^\t\n]+)(?:[\t\n])'.format(column))

    num_lines = get_line_number(filepath)

    with open(filepath, 'r') as f:
        # Not using .read() here causes f to be read as an iterable, which is
        # exactly what we want because the file may be large
        for line in tqdm(f, total=num_lines,
                         desc="Collecting geonameids from {}".format(filename)):
            m = rgx.match(line)

            if m:
                geonameids.append(m.group(1))

# For all of the collected geonameids, write out matching lines from the
# original file
with open(original_file, 'r') as rf:
    # Check for file existence again, immediately before we write to it
    if os.path.exists(new_filepath):
        print("This script writes {}, but that file already exists. Please "
              "move (or remove) that file and rerun this script.".format(
                  new_filepath))

        exit(-1)

    num_lines = get_line_number(original_file)

    # Write out matching lines to the new file
    with open(new_filepath, 'a+') as wf:
        for line in tqdm(rf, total=num_lines,
                         desc="Writing geonameids"):
            m = file_rgx.match(line)

            if m and m.group(1) in geonameids:
                wf.write(line)
