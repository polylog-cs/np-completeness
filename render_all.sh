#!/bin/bash

# exit on error
set -eo pipefail

# cd to script dir
cd "$(dirname "$0")"
cd manim/

filenames="anims.py prng.py statistical_test.py"

for filename in $filenames; do
	manim -qk $filename --write_all
done
