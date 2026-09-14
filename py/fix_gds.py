#!/usr/bin/env python3

import struct
import sys

CELLS = [
	'dev_ctrl_b1',
	'dev_ctrl_e1',
	'dev_ctrl_b2',
	'dev_ctrl_m2',
	'dev_ctrl_e2',
]

PSDM_LY = 94
PSDM_DT = 20

OLD_PR_BOUNDARY_LY = 235
NEW_PR_BOUNDARY_LY = 189
PR_BOUNDARY_DT = 4

def fix_gds_file(fn_gds_in, fn_gds_out):
	with open(fn_gds_in, 'rb') as f:
		data = bytearray(f.read())

	idx = 0
	curr_layer_offset = None

	while idx < len(data):
		length, rectype = struct.unpack('>HH', data[idx:idx+4])

		if rectype == 0x0d02: # LAYER
			layer = struct.unpack('>h', data[idx+4:idx+6])[0]
			if layer == OLD_PR_BOUNDARY_LY:
				curr_layer_offset = idx + 4
		elif rectype == 0x0e02 or rectype == 0x1602: # DATATYPE or TEXTTYPE
			datatype = struct.unpack('>h', data[idx+4:idx+6])[0]
			if curr_layer_offset is not None and datatype == PR_BOUNDARY_DT:
				data[curr_layer_offset:curr_layer_offset+2] = struct.pack('>h', NEW_PR_BOUNDARY_LY)
			curr_layer_offset = None
		elif rectype == 0x1100: # ENDEL
			curr_layer_offset = None

		idx += length

	# Save binary layer remapping result first
	with open(fn_gds_out, 'wb') as f:
		f.write(data)

	# If gdstk is available, load updated GDS file and perform PSDM polygon removal
	try:
		import gdstk
		lib = gdstk.read_gds(fn_gds_out)
		for cell in lib.cells:
			if cell.name in CELLS:
				to_rem = [ p for p in cell.polygons if p.layer == PSDM_LY and p.datatype == PSDM_DT ]
				cell.remove(*to_rem)
		lib.write_gds(fn_gds_out)
	except ImportError:
		pass

def main(argv0, fn_gds_in, fn_gds_out=None):
	if fn_gds_out is None:
		fn_gds_out = fn_gds_in
	fix_gds_file(fn_gds_in, fn_gds_out)

if __name__ == '__main__':
	main(*sys.argv)
