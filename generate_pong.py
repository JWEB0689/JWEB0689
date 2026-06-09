import xml.etree.ElementTree as ET
import re

tree = ET.parse('/Users/jeremyweber/Documents/JWEB0689/chart_raw.svg')
root = tree.getroot()

for elem in root.iter():
    if '}' in elem.tag:
        elem.tag = elem.tag.split('}', 1)[1]

colliders = []
min_x, max_x = 9999, -9999
min_y, max_y = 9999, -9999

for rect in root.findall('rect'):
    style = rect.get('style', '')
    if 'fill:#EEEEEE' not in style and rect.get('x') is not None:
        # Filled rect
        x = float(rect.get('x'))
        y = float(rect.get('y'))
        w = float(rect.get('width'))
        h = float(rect.get('height'))
        colliders.append((x, y, w, h))
        
    x = float(rect.get('x')) if rect.get('x') else 0
    y = float(rect.get('y')) if rect.get('y') else 0
    if x < min_x: min_x = x
    if x > max_x: max_x = x
    if y < min_y: min_y = y
    if y > max_y: max_y = y

max_x += 10
max_y += 10

# Adjust SVG viewBox to fit paddles
orig_width = int(root.get('width', '674'))
orig_height = int(root.get('height', '124'))
root.set('width', str(orig_width + 40))
root.set('viewBox', f"-20 -10 {orig_width + 40} {orig_height + 20}")

# Add dark background
bg = ET.Element('rect', {'x': '-20', 'y': '-10', 'width': str(orig_width + 40), 'height': str(orig_height + 20), 'fill': '#0d1117'})
root.insert(0, bg)

fps = 30
duration = 15 # seconds
frames = fps * duration

ball_x = min_x + 50
ball_y = min_y + 10
vx = 250.0 / fps # faster!
vy = 180.0 / fps
r = 1

path_points = []
paddle_left_y = []
paddle_right_y = []

paddle_h = 16

for f in range(frames):
    prev_x, prev_y = ball_x, ball_y
    ball_x += vx
    ball_y += vy
    
    # Outer boundaries (Paddles handle X boundaries)
    if ball_y - r < min_y - 5:
        ball_y = min_y - 5 + r
        vy = -vy
    if ball_y + r > max_y + 5:
        ball_y = max_y + 5 - r
        vy = -vy
        
    # Paddle collision
    if ball_x - r < min_x - 15:
        ball_x = min_x - 15 + r
        vx = -vx
    if ball_x + r > max_x + 15:
        ball_x = max_x + 15 - r
        vx = -vx
        
    # Rect collisions
    for (cx, cy, cw, ch) in colliders:
        if (ball_x + r > cx and ball_x - r < cx + cw and
            ball_y + r > cy and ball_y - r < cy + ch):
            
            hit_x = False
            hit_y = False
            if prev_x + r <= cx or prev_x - r >= cx + cw:
                hit_x = True
            if prev_y + r <= cy or prev_y - r >= cy + ch:
                hit_y = True
                
            if hit_x:
                vx = -vx
                ball_x = prev_x
            if hit_y:
                vy = -vy
                ball_y = prev_y

    path_points.append(f"{ball_x:.1f},{ball_y:.1f}")
    
    # Paddle AI
    # Left paddle follows ball if ball is on left half
    target_ly = ball_y - paddle_h/2 if ball_x < (min_x+max_x)/2 else (max_y+min_y)/2 - paddle_h/2
    paddle_left_y.append(f"{target_ly:.1f}")
    
    target_ry = ball_y - paddle_h/2 if ball_x > (min_x+max_x)/2 else (max_y+min_y)/2 - paddle_h/2
    paddle_right_y.append(f"{target_ry:.1f}")

path_str = "M" + " L".join(path_points)

root.set('xmlns', 'http://www.w3.org/2000/svg')

ball = ET.SubElement(root, 'circle')
ball.set('r', str(r))
ball.set('fill', '#000000')
anim_ball = ET.SubElement(ball, 'animateMotion')
anim_ball.set('path', path_str)
anim_ball.set('dur', f"{duration}s")
anim_ball.set('repeatCount', 'indefinite')

lp = ET.SubElement(root, 'rect')
lp.set('x', str(min_x - 15))
lp.set('width', '4')
lp.set('height', str(paddle_h))
lp.set('fill', '#ffffff')
lp.set('rx', '2')
anim_lp = ET.SubElement(lp, 'animate')
anim_lp.set('attributeName', 'y')
anim_lp.set('values', ";".join(paddle_left_y))
anim_lp.set('dur', f"{duration}s")
anim_lp.set('repeatCount', 'indefinite')

rp = ET.SubElement(root, 'rect')
rp.set('x', str(max_x + 15))
rp.set('width', '4')
rp.set('height', str(paddle_h))
rp.set('fill', '#ffffff')
rp.set('rx', '2')
anim_rp = ET.SubElement(rp, 'animate')
anim_rp.set('attributeName', 'y')
anim_rp.set('values', ";".join(paddle_right_y))
anim_rp.set('dur', f"{duration}s")
anim_rp.set('repeatCount', 'indefinite')

ET.register_namespace('', 'http://www.w3.org/2000/svg')
tree.write('/Users/jeremyweber/Documents/JWEB0689/pong_chart.svg', xml_declaration=True, encoding='utf-8')
