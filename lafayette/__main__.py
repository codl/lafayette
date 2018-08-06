import argparse
import lafayette

parser = argparse.ArgumentParser(
    description='Generate a gallery for a set of photos')
parser.add_argument('path', help='Path to directory where photos are stored')

args = parser.parse_args()

lafayette.generate_gallery(args.path)
