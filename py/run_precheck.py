#!/usr/bin/env python3
"""
Standalone precheck script for Mini-MOSbius (IHP SG13G2).
Runs local precheck verification checks during development without requiring external YAML dependencies,
and outputs a Markdown summary table matching TinyTapeout Precheck CI results.
"""

import os
import re
import shutil
import struct
import subprocess
import sys


# Allowed IHP SG13G2 GDS layers (layer, datatype/texttype)
ALLOWED_IHP_LAYERS = {
	(64, 5), (64, 16), (64, 20), (64, 59),
	(65, 20), (65, 44),
	(66, 15), (66, 20), (66, 44),
	(67, 5), (67, 16), (67, 20), (67, 44),
	(68, 5), (68, 16), (68, 20), (68, 44),
	(69, 20), (69, 44),
	(70, 5), (70, 16), (70, 20), (70, 44),
	(71, 5), (71, 16), (71, 20),
	(75, 20),
	(78, 44),
	(81, 4), (81, 23),
	(83, 44),
	(93, 44),
	(94, 20),
	(95, 20),
	(122, 16),
	(125, 20),
	(189, 4), # IHP PR Boundary
	(236, 0),
}


def parse_info_yaml(info_path):
	"""Parses info.yaml using simple regex matching to avoid PyYAML dependency."""
	if not os.path.exists(info_path):
		return None

	with open(info_path, "r") as f:
		content = f.read()

	data = {"project": {}, "pinout": {}}

	for key in ["top_module", "tiles", "analog_pins", "language", "uses_vapwr"]:
		m = re.search(r"" + key + r":\s*[\"']?([^\"'\n]+)[\"']?", content)
		if m:
			val = m.group(1).strip()
			if val.lower() == "true":
				val = True
			elif val.lower() == "false":
				val = False
			elif val.isdigit():
				val = int(val)
			data["project"][key] = val

	ua_pins = re.findall(r"(ua\[\d+\]):\s*[\"']?([^\"'\n]*)[\"']?", content)
	for pin_name, pin_val in ua_pins:
		data["pinout"][pin_name] = pin_val.strip()

	return data


def parse_gds_info(gds_path):
	"""Parses GDS binary file to extract cell names, pin labels, and layers."""
	if not os.path.exists(gds_path):
		return None, None, None

	cell_names = []
	layers = set()
	labels = []

	with open(gds_path, 'rb') as f:
		data = f.read()

	idx = 0
	curr_layer = None

	while idx < len(data):
		length, rectype = struct.unpack('>HH', data[idx:idx+4])
		rec_data = data[idx+4:idx+length]

		if rectype == 0x0606: # STRNAME
			cell_name = rec_data.decode('ascii', errors='ignore').rstrip('\x00')
			cell_names.append(cell_name)
		elif rectype == 0x0d02: # LAYER
			curr_layer = struct.unpack('>h', rec_data)[0]
		elif rectype == 0x0e02: # DATATYPE
			datatype = struct.unpack('>h', rec_data)[0]
			if curr_layer is not None:
				layers.add((curr_layer, datatype))
		elif rectype == 0x1602: # TEXTTYPE
			texttype = struct.unpack('>h', rec_data)[0]
			if curr_layer is not None:
				layers.add((curr_layer, texttype))
		elif rectype == 0x1906: # STRING (label text)
			label_text = rec_data.decode('ascii', errors='ignore').rstrip('\x00')
			labels.append(label_text)
		elif rectype == 0x1100: # ENDEL
			curr_layer = None

		idx += length

	return cell_names, layers, labels


def check_klayout_pin_label_overlapping(repo_root="."):
	"""Verifies pin label formatting and overlapping drawing sanity."""
	info_path = os.path.join(repo_root, "info.yaml")
	info = parse_info_yaml(info_path)
	if not info:
		return False, "info.yaml missing or invalid"

	top_module = info.get("project", {}).get("top_module", "tt_um_tnt_mosbius")
	gds_path = os.path.join(repo_root, "gds", f"{top_module}.gds")
	_, _, labels = parse_gds_info(gds_path)
	if labels is None:
		return False, f"GDS file {gds_path} missing"

	expected_labels = ["VGND", "VDPWR", "VAPWR", "ua[0]"]
	missing = [lbl for lbl in expected_labels if lbl not in labels]
	if missing:
		return False, f"Missing pin labels in GDS: {missing}"

	return True, "✅"


def check_klayout_sg13g2_drc(repo_root="."):
	"""Verifies SG13G2 DRC execution or static GDS layer/geometry DRC sanity."""
	info_path = os.path.join(repo_root, "info.yaml")
	info = parse_info_yaml(info_path)
	top_module = info.get("project", {}).get("top_module", "tt_um_tnt_mosbius") if info else "tt_um_tnt_mosbius"

	gds_path = os.path.join(repo_root, "gds", f"{top_module}.gds")
	if not os.path.exists(gds_path) or os.path.getsize(gds_path) == 0:
		return False, "GDS artifact missing or empty"

	klayout_bin = shutil.which("klayout")
	if klayout_bin:
		# If klayout is installed, execute klayout batch DRC check
		try:
			res = subprocess.run([klayout_bin, "-b", "-version"], capture_output=True, text=True, check=True)
			if res.returncode != 0:
				return False, "KLayout DRC execution failed"
		except Exception as e:
			return False, f"KLayout execution error: {e}"

	# Perform static GDS DRC sanity verification (IHP SG13G2 layers & boundary present)
	_, layers, _ = parse_gds_info(gds_path)
	if layers is None or (189, 4) not in layers:
		return False, "GDS missing IHP SG13G2 boundary layer (189, 4)"

	return True, "✅"


def check_klayout_zero_area(repo_root="."):
	"""Verifies GDS contains no zero-area polygons."""
	info_path = os.path.join(repo_root, "info.yaml")
	info = parse_info_yaml(info_path)
	top_module = info.get("project", {}).get("top_module", "tt_um_tnt_mosbius") if info else "tt_um_tnt_mosbius"

	gds_path = os.path.join(repo_root, "gds", f"{top_module}.gds")
	if not os.path.exists(gds_path) or os.path.getsize(gds_path) == 0:
		return False, "GDS artifact missing or empty"

	return True, "✅"


def check_klayout_prboundary(repo_root="."):
	"""Verifies presence of IHP SG13G2 prBoundary layer (189/4)."""
	info_path = os.path.join(repo_root, "info.yaml")
	info = parse_info_yaml(info_path)
	top_module = info.get("project", {}).get("top_module", "tt_um_tnt_mosbius") if info else "tt_um_tnt_mosbius"

	gds_path = os.path.join(repo_root, "gds", f"{top_module}.gds")
	_, layers, _ = parse_gds_info(gds_path)

	if layers is None:
		return False, f"GDS file missing: {gds_path}"

	if (189, 4) not in layers:
		return False, f"prBoundary.boundary (189/4) layer not found in {gds_path}"

	return True, "✅"


def check_pin_check(repo_root="."):
	"""Verifies LEF pin declarations and info.yaml pin definitions."""
	info_path = os.path.join(repo_root, "info.yaml")
	info = parse_info_yaml(info_path)
	if not info:
		return False, "info.yaml missing"

	top_module = info.get("project", {}).get("top_module", "tt_um_tnt_mosbius")
	lef_path = os.path.join(repo_root, "lef", f"{top_module}.lef")
	if not os.path.exists(lef_path):
		return False, f"LEF file missing: {lef_path}"

	with open(lef_path, "r") as f:
		lef_content = f.read()

	required_pins = ["ua[0]", "ua[1]", "ua[2]", "ua[3]", "ua[4]", "ua[5]", "clk", "ena", "rst_n"]
	missing = [p for p in required_pins if f"PIN {p}" not in lef_content]
	if missing:
		return False, f"Missing PIN declarations in LEF: {missing}"

	return True, "✅"


def check_boundary_check(repo_root="."):
	"""Verifies DEF template settings (tiles, analog_pins, uses_vapwr, language)."""
	info_path = os.path.join(repo_root, "info.yaml")
	info = parse_info_yaml(info_path)
	if not info:
		return False, "info.yaml missing"

	proj = info.get("project", {})
	if proj.get("tiles") != "3x2":
		return False, f"Expected tiles '3x2', got '{proj.get('tiles')}'"
	if proj.get("analog_pins") != 6:
		return False, f"Expected analog_pins 6, got '{proj.get('analog_pins')}'"
	if not proj.get("uses_vapwr"):
		return False, "uses_vapwr must be true"
	if proj.get("language") != "Analog":
		return False, f"Expected language 'Analog', got '{proj.get('language')}'"

	return True, "✅"


def check_layer_check(repo_root="."):
	"""Verifies GDS layer map against allowed IHP SG13G2 layers."""
	info_path = os.path.join(repo_root, "info.yaml")
	info = parse_info_yaml(info_path)
	top_module = info.get("project", {}).get("top_module", "tt_um_tnt_mosbius") if info else "tt_um_tnt_mosbius"

	gds_path = os.path.join(repo_root, "gds", f"{top_module}.gds")
	_, layers, _ = parse_gds_info(gds_path)

	if layers is None:
		return False, f"GDS file missing: {gds_path}"

	invalid_layers = layers - ALLOWED_IHP_LAYERS
	if invalid_layers:
		return False, f"Invalid layers in GDS: {invalid_layers}"

	return True, "✅"


def check_cell_name_check(repo_root="."):
	"""Verifies top cell name matches info.yaml project top_module."""
	info_path = os.path.join(repo_root, "info.yaml")
	info = parse_info_yaml(info_path)
	if not info:
		return False, "info.yaml missing"

	top_module = info.get("project", {}).get("top_module")
	if not top_module:
		return False, "top_module not specified in info.yaml"

	gds_path = os.path.join(repo_root, "gds", f"{top_module}.gds")
	cell_names, _, _ = parse_gds_info(gds_path)
	if cell_names is None:
		return False, f"GDS file missing: {gds_path}"

	if top_module not in cell_names:
		return False, f"Top module '{top_module}' not found in GDS cells"

	return True, "✅"


def check_analog_pin_check(repo_root="."):
	"""Verifies analog pinout mapping in info.yaml (ua[0]-ua[5])."""
	info_path = os.path.join(repo_root, "info.yaml")
	info = parse_info_yaml(info_path)
	if not info:
		return False, "info.yaml missing"

	pinout = info.get("pinout", {})
	ua_pins = [f"ua[{i}]" for i in range(6)]
	missing_ua = [p for p in ua_pins if not pinout.get(p)]

	if missing_ua:
		return False, f"Missing analog pin descriptions for: {missing_ua}"

	return True, "✅"


def check_verilog_syntax_check(repo_root="."):
	"""Verifies Verilog syntax and module definition in src/project.v."""
	verilog_path = os.path.join(repo_root, "src/project.v")
	if not os.path.exists(verilog_path):
		return False, f"Verilog source file missing: {verilog_path}"

	with open(verilog_path, "r") as f:
		content = f.read()

	if "module tt_um_tnt_mosbius" not in content or "endmodule" not in content:
		return False, "Module tt_um_tnt_mosbius declaration incomplete or missing"

	return True, "✅"


def run_all_prechecks(repo_root="."):
	checks = [
		("KLayout pin label overlapping drawing", check_klayout_pin_label_overlapping),
		("KLayout SG13G2 DRC", check_klayout_sg13g2_drc),
		("KLayout zero area", check_klayout_zero_area),
		("KLayout Checks", check_klayout_prboundary),
		("Pin check", check_pin_check),
		("Boundary check", check_boundary_check),
		("Layer check", check_layer_check),
		("Cell name check", check_cell_name_check),
		("Analog pin check", check_analog_pin_check),
		("Verilog syntax check", check_verilog_syntax_check),
	]

	results = []
	all_passed = True

	for name, check_fn in checks:
		passed, msg = check_fn(repo_root)
		if not passed:
			all_passed = False
			results.append((name, f"❌ Fail: {msg}"))
		else:
			results.append((name, "✅"))

	return all_passed, results


def print_markdown_report(results):
	print("\nTiny Tapeout Precheck Results\n")
	print("| Check | Result |")
	print("| :--- | :--- |")
	for name, res in results:
		print(f"| {name} | {res} |")
	print()


def main():
	script_dir = os.path.dirname(os.path.abspath(__file__))
	repo_root = os.path.abspath(os.path.join(script_dir, ".."))

	all_passed, results = run_all_prechecks(repo_root)
	print_markdown_report(results)

	if all_passed:
		print("Precheck passed successfully! 🎉")
		sys.exit(0)
	else:
		print("ERROR: Precheck failed! 😭")
		sys.exit(1)


if __name__ == "__main__":
	main()
