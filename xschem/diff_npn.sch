v {xschem version=3.4.8RC file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 180 -160 340 -160 {
lab=outp}
N 280 -160 280 -100 {
lab=outp}
N 590 -160 690 -160 {
lab=outm}
N 590 -160 590 -100 {
lab=outm}
N 180 -60 220 -60 {
lab=inp}
N 650 -60 690 -60 {
lab=inm}
N 280 -20 280 40 {
lab=itail}
N 590 -20 590 40 {
lab=itail}
N 280 40 590 40 {
lab=itail}
N 440 40 440 100 {
lab=itail}
N 260 -120 260 -100 {
lab=GND}
N 610 -120 610 -100 {
lab=GND}
C {devices/iopin.sym} -670 -250 0 1 {name=p9 lab=VAPWR}
C {devices/iopin.sym} -670 -210 0 1 {name=p10 lab=VDPWR}
C {devices/ipin.sym} -670 -170 0 0 {name=p3 lab=inp}
C {devices/ipin.sym} -670 -130 0 0 {name=p5 lab=inm}
C {devices/opin.sym} -670 -90 0 1 {name=p19 lab=outp}
C {devices/opin.sym} -670 -50 0 1 {name=p34 lab=outm}
C {devices/iopin.sym} -670 -10 0 1 {name=p4 lab=itail}
C {devices/iopin.sym} -670 30 0 1 {name=p47 lab=GND}
C {devices/lab_pin.sym} 180 -60 0 0 {name=p11 sig_type=std_logic lab=inp}
C {devices/lab_pin.sym} 690 -60 0 1 {name=p12 sig_type=std_logic lab=inm}
C {devices/lab_pin.sym} 180 -160 0 0 {name=p13 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 690 -160 0 1 {name=p14 sig_type=std_logic lab=outm}
C {devices/lab_pin.sym} 260 -120 1 0 {name=p15 sig_type=std_logic lab=GND}
C {devices/lab_pin.sym} 610 -120 1 0 {name=p16 sig_type=std_logic lab=GND}
C {devices/lab_pin.sym} 440 100 1 1 {name=p48 sig_type=std_logic lab=itail}
C {npn13G2.sym} 260 -60 0 0 {name=Q1
w=0.07u
l=0.9u
nx=1
ny=1
model=npn13G2
spiceprefix=K
}
C {npn13G2.sym} 610 -60 0 1 {name=Q2
w=0.07u
l=0.9u
nx=1
ny=1
model=npn13G2
spiceprefix=K
}
