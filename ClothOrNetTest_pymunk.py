'''Cloth/Net simulation'''

from kivy.core.window import Window
from kivy.factory import Factory as F
from kivy.clock import Clock
from kivy.base import runTouchApp

from pymunk import *
from pymunk.constraints import *

Window.rotation = -90
space = Space()
space.gravity = 0, -900

xcount = ycount = 15 #increase this to increase the number of sections/cells in the cloth.

width, height = 200,200 #change this to increase the area of the cloth 
x,y = Window.center[0] - width/2, Window.center[1] - height/2 - 30

is_stretchy = True
#for stretchy clothes/nets
stiffness = 100000.0
damping = 300
###
Window.clearcolor = 1, .2, .3, 1.
	
def gen_points():
	#generates the default points in a grid fashion
	points = []
	dx = width/xcount
	dy = height/ycount
	for i in range(xcount+1):
		for j in range(ycount+1):
			xp = x+dx*i
			yp = y+dy*j
			points.append([xp,yp])
	return points

def add_segs_body(points, mass=3):
	#adds segments and bodies at each points generated
	bodies = []
	for i in range(len(points)-1):
		p = points[i]
		b = Body(mass, 100)
		b.position = p
		c = Circle(b, 1)
		c.friction = 1.
		c.elasticity = .1
		space.add(b,c)
		bodies.append(b)
		if i!=0:
			r = i % ycount
			if ycount*(r+1)+r == i:
				p1 = points[i+ycount+1]
				space.add(Segment(b, p, p1, 1))
		elif i in range((ycount+1)*(xcount), len(points)):
			p1 = points[i+1]
			space.add(Segment(b, p, p1, 1))
		else:
			p1 = points[i+ycount+1]
			p2 = points[i+1]
			space.add(Segment(b, p, p1, 1))
			space.add(Segment(b, p, p2, 1))
	b_last = Body(mass, 100)
	b_last.position = points[-1]
	space.add(b_last)
	bodies.append(b_last)
	return bodies
	
def add_joints(bodies):
	#adds a DampedSpring joint to each body at each point if flag `is_stretchy` is True, else adds a PinJoint which does not allow stretching between bodies.
	for i in range(len(bodies)-1):
		b = bodies[i]
		r = i%ycount
		if i!=0 and ycount*(r+1)+r== i:
			#if i is at the top of the net
			b1 = bodies[i+ycount+1]
			if not is_stretchy:
				space.add(PinJoint(b, b1))
			else:
				rl = (b.position - b1.position).length * .92
				space.add(DampedSpring(b,b1, (0, 0), (0, 0), rl, stiffness, damping))
		elif i in range((ycount+1)*xcount, len(points)-1):
			#if i is at the right side end of the net
			b1 = bodies[i+1]
			if not is_stretchy:
				space.add(PinJoint(b, b1))
			else:
				rl = (b.position - b1.position).length * .92
				space.add(DampedSpring(b,b1, (0, 0), (0, 0), rl, stiffness, damping))
		else:
			b1 = bodies[i+ycount+1]
			b2 = bodies[i+1]
			if not is_stretchy:
				space.add(PinJoint(b, b1))
				space.add(PinJoint(b, b2))
			else:
				rl = (b.position - b1.position).length * .92
				rl2 = (b.position - b2.position).length * .92
				space.add(DampedSpring(b,b1, (0, 0), (0, 0), rl, stiffness, damping))
				space.add(DampedSpring(b,b2, (0, 0), (0, 0), rl2, stiffness, damping))

def get_line_points(p):
	pointsy = []
	pointsx = []
	current = 0
	#Y zigzag pattern
	c = 0
	d = 1
	for i in range(len(p)):
		pointsy.extend(p[current])
		if c == ycount:
			current += ycount+1
			c*=0
			d *= -1
			continue
		c+=1
		current+=d
	curr = 0
	c = 0
	d = xcount+1
	for i in range(len(p)):
		pointsx.extend(p[curr])
		if c == xcount:
			curr += 1
			c*=0
			d *= -1
			continue
		c+=1
		curr+=d
	return pointsx, pointsy
	
points = gen_points()
bodies = add_segs_body(points)
#space.add(PinJoint(bodies[-1],bodies[1]))
add_joints(bodies)
#2087041723
lp = get_line_points(points)
sb1 = Body(body_type=Body.STATIC)
sb1.position = x - 50, y+height+50

sb2 = Body(body_type=Body.STATIC)
sb2.position = x +width+50, y+height+50

msb = Body(body_type=Body.STATIC)

space.add(PinJoint(bodies[ycount], sb1))
space.add(PinJoint(bodies[-1], sb2))

bc = space.static_body
bd = space.static_body
#bd = Body(body_type=Body.KINEMATIC)

seg = Segment(bd, (x+20,y-5), (x+width-20,y-5), 5)
seg.friction = 1
seg.elasticity = .1
#bc.position = Window.center[0], 100
circle = Circle(bc, 70)
circle.friction = 1
space.add(circle)
space.add(seg)
with Window.canvas:
	anch_l1 = F.Line(points=[*bodies[ycount].position,*sb1.position], width=2)
	anch_l2 = F.Line(points=[*bodies[-1].position,*sb2.position], width=2)
	F.Color(.9, .8, .1)
	line = F.Line(points=lp[0], width=1.05)
	line2 = F.Line(points=lp[1], width=1.05)
	F.Color(.5, .5, .5)
	F.Line(width=seg.radius, points=[*seg.a, *seg.b])
	F.Color(.5, .5, .1)
	moveable = F.Point(pointsize=4, points=[])
	moveable2 = F.Point(pointsize=4, points=[])
	title= F.Label(text="2d Net/Cloth Simulation With Python", font_size=29)
	title.center = Window.center[0], Window.height-20

lbl1 = F.Label(text="Anchor 1: ", size_hint=[None,None])
lbl2 = F.Label(text="Anchor 2: ", size_hint=[None,None])
lbl1.pos = 0, Window.height - 100
lbl2.pos = 0, Window.height - 140
Window.add_widget(lbl1)
Window.add_widget(lbl2)

def update(dt):
	points = list(map(lambda b: b.position, bodies))
	lp = get_line_points(points)
	line.points = lp[0]
	line2.points = lp[1]
	anch_l1.points = [*bodies[ycount].position,*sb1.position]
	anch_l2.points = [*bodies[-1].position,*sb2.position]
	lbl1.text = f"Anchor 1: {list(sb1.position)}"
	lbl2.text = f"Anchor 2: {list(sb2.position)}"
	lbl1.size = lbl1.texture_size
	lbl2.size = lbl2.texture_size
	#ell.pos = bc.position - Vec2d(20,20)
	[space.step(.009) for i in range(4)]

def move_anchor(touch):
	mov_anch = min(sb1, sb2, key=lambda sb: (sb.position - Vec2d(*touch.pos)).length)
	mov_anch.position = touch.pos
	m = [moveable, moveable2][mov_anch!=sb1]
	m.points = touch.pos
	
    
Window.on_touch_move = move_anchor

Clock.schedule_interval(update, 1/50)

runTouchApp()