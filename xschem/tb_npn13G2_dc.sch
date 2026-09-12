v {xschem version=3.4.8RC file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 100 -50 100 0 {lab=vc}
N 100 80 100 130 {lab=GND}
N 0 40 40 40 {lab=vb}
N -60 40 0 40 {lab=vb}
N 100 -120 100 -50 {lab=vc}
N 100 -50 200 -50 {lab=vc}
C {npn13G2.sym} 80 40 0 0 {name=Q1 w=0.07u l=0.9u nx=1 ny=1 model=npn13G2 spiceprefix=K}
C {devices/vsource.sym} -60 70 0 0 {name=Vbe value=0.75}
C {devices/vsource.sym} 200 -10 0 0 {name=Vce value=1.5}
C {devices/gnd.sym} -60 100 0 0 {name=g1}
C {devices/gnd.sym} 200 20 0 0 {name=g2}
C {devices/gnd.sym} 100 130 0 0 {name=g3}
C {devices/lab_pin.sym} 0 40 0 0 {name=p1 sig_type=std_logic lab=vb}
C {devices/lab_pin.sym} 200 -50 0 0 {name=p2 sig_type=std_logic lab=vc}
C {devices/code.sym} -200 -200 0 0 {name=SPICE_COMMANDS
value="
.param temp=27
.dc Vce 0 3.3 0.01 Vbe 0.65 0.85 0.05
.save i(Vce) i(Vbe)
"
}
