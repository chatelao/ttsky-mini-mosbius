set layout [readnet spice $project.lvs.spice]
set schem  [readnet verilog /dev/null]
readnet spice $::env(PDK_ROOT)/ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice $schem
readnet spice   ../xschem/simulation/mosbius.spice $schem
readnet verilog ../src/ctrl_top.synth.v            $schem
readnet verilog ../src/project.v                   $schem
::netgen::format 60
lvs "$layout $project" "$schem $project" $::env(PDK_ROOT)/ihp-sg13g2/libs.tech/netgen/sg13g2_setup.tcl lvs.report -blackbox
