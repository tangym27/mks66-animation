import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========
  Checks the commands array for any animation commands
  (frames, basename, vary)
  Should set num_frames and basename if the frames
  or basename commands are present
  If vary is found, but frames is not, the entire
  program should exit.
  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):
    frame = vary = name = False
    basename = "base"
    num_frames = 1
    for command in commands:
        if command["op"] == "frames":
            num_frames = int(command["args"][0])
            frame = True
        elif command["op"] == "vary":
            vary = True
        elif command["op"] == "basename":
            name = True
            basename = command["args"][0]
    if vary and not frame:
        print("vary and not frame")
        exit(1)
    if frame and not name:
        print("frame and not basename")

    #print num_frames
    return [basename, num_frames]

"""======== second_pass( commands ) ==========
  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).
  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.
  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    #print num_frames
    frames = [ {} for i in range(num_frames) ]
    for command in commands:
        if command["op"] == 'vary':
            knob = command["knob"]
            start_frame = command["args"][0]
            end_frame = command["args"][1]
            start_value = float(command["args"][2])
            end_value = float(command["args"][3])
            value = 0
            if (start_frame < 0 or end_frame >= num_frames or end_frame <= start_frame):
                print "Error: bad range"
                exit(1)
            increment = (end_value - start_value) / (end_frame - start_frame)
            for i in range(num_frames):
                if i >= start_frame and i <= end_frame:
                    frames[i][knob] = start_value + increment * (i - start_frame)
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
            0.75,
              1],
             [255,
              255,
            255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                        'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    [name, num_frames] = first_pass(commands)
    knobs = second_pass(commands, num_frames)


    for i in range(int(num_frames)):
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 20
        consts = ''
        coords = []
        coords1 = []

        if num_frames > 1:
            for knob in knobs[i]:
                symbols[knob][1] = knobs[i][knob]

        for command in commands:
            print command
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                if command["knob"]:
                    knob_value = symbols[command["knob"]][1]
                tmp = make_translate(args[0] * knob_value, args[1] * knob_value, args[2] * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if command["knob"]:
                    knob_value = symbols[command["knob"]][1]
                tmp = make_scale(args[0] * knob_value, args[1]* knob_value, args[2]* knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if command["knob"]:
                    knob_value = symbols[command["knob"]][1]
                theta = args[1] * (math.pi/180) * knob_value
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        if num_frames > 1:
            filename = 'anim/' + name + ('%03d' %int(i))
            print "file name: " + filename
            save_extension(screen,filename)

    if num_frames > 1:
        make_animation(name)
