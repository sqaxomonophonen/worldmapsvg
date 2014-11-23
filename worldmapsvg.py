#!/usr/bin/env python

import sys
import argparse
from svg.path import parse_path
from svg.path import Line
from svg.path import CubicBezier

def construct_argument_parser():
	parser = argparse.ArgumentParser(description = "generate svg world maps")
	dim_default = '1024x512'
	parser.add_argument('-d', '--dim', dest='dim', metavar='<WxH>', help='output dimensions (default: %s)' % dim_default, default=dim_default)

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-R', '--robinson', action="store_true", help='output robinson projection')
	group.add_argument('-E', '--equirectangular', action="store_true", help='output equirectangular projection')

	parser.add_argument('--land-color', dest='landcolor', metavar='<color>', help='color of land (default: white)', default = '#ffffff')
	parser.add_argument('--sea-color', dest='seacolor', metavar='<color>', help='color of sea (default: none)')

	parser.add_argument('-o', '--output', dest='output', metavar='<file.svg>', help='output file (default: stdout)')
	return parser

args = construct_argument_parser().parse_args()

width, height = map(int, args.dim.split("x"))

rproj = [ # robinson projection table
	# (latitude,PLEN,PDFE)
	(00, 1.0000, 0.0000),
	(05, 0.9986, 0.0620),
	(10, 0.9954, 0.1240),
	(15, 0.9900, 0.1860),
	(20, 0.9822, 0.2480),
	(25, 0.9730, 0.3100),
	(30, 0.9600, 0.3720),
	(35, 0.9427, 0.4340),
	(40, 0.9216, 0.4958),
	(45, 0.8962, 0.5571),
	(50, 0.8679, 0.6176),
	(55, 0.8350, 0.6769),
	(60, 0.7986, 0.7346),
	(65, 0.7597, 0.7903),
	(70, 0.7186, 0.8435),
	(75, 0.6732, 0.8936),
	(80, 0.6213, 0.9394),
	(85, 0.5722, 0.9761),
	(90, 0.5322, 1.0000)
]

lerp = lambda a,b,t: a + (b-a)*t

def robinson_unmap(c):
	x = c.real
	y = c.imag
	ya = min(1.0,abs(y))
	for i in range(len(rproj)-1):
		rp0 = rproj[i]
		rp1 = rproj[i+1]
		pdfe0 = rp0[2]
		pdfe1 = rp1[2]
		if pdfe0 <= ya <= pdfe1:
			t = (ya - pdfe0) / (pdfe1-pdfe0)
			lat = lerp(rp0[0], rp1[0], t)
			plen = lerp(rp0[1], rp1[1], t)
			break
	if y < 0:
		lat = -lat
	return complex(x/plen, lat/90.0)

def get_path():
	with open("path") as f:
		return parse_path(f.read())

path = get_path()

def map_path(path, fn):
	for cmd in path:
		fields = None
		if isinstance(cmd, Line):
			fields = ['start', 'end']
		elif isinstance(cmd, CubicBezier):
			fields = ['start', 'control1', 'control2', 'end']
		else:
			raise ValueError(type(cmd))
		for field in fields:
			setattr(cmd, field, fn(getattr(cmd, field)))
	return path

def mkdenorm(w,h):
	return lambda c: complex((c.real+1.0)*(float(w)/2.0), (c.imag+1.0)*(float(h)/2.0))

denorm = mkdenorm(width,height)
normalize = lambda c: complex((c.real / 2760.0)*2.0-1.0, (c.imag / 1398.3)*2.0-1.0)
if args.robinson:
	mapfn = lambda c: denorm(normalize(c))
elif args.equirectangular:
	mapfn = lambda c: denorm(robinson_unmap(normalize(c)))
else:
	raise RuntimeError("projection not set")

path = map_path(path, mapfn)

out = sys.stdout if not args.output else open(args.output, "w")

out.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
out.write('<svg id="svg2" xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" version="1.0">\n' % (width,height))
if args.seacolor:
	out.write('<rect x="0" y="0" width="%s" height="%s" fill="%s" />\n' % (width,height,args.seacolor))
out.write('<path fill="' + args.landcolor + '" d="' + path.d() + '"/>')
out.write('</svg>')

if args.output:
	out.close()
