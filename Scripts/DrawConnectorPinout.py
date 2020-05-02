#execfile(r'C:\Users\Admin\Documents\KiCad\Scripts\DrawConnectorPinout.py')
#By Alan Samet

#This is hacked together and has some restrictions. Your connector needs to be placed vertically and I've only tested it with pin header connectors.
#It draws a pinout diagram on your PCB's silkscreen so you can reference your connector's pinout for testing. 

import pcbnew

#Connector must be vertically oriented for this to work. A max of two columns is expected. 

PlaceOnBack = True
if PlaceOnBack == True:
    layer = pcbnew.B_SilkS
    mirror = True
else:
    layer = pcbnew.F_SilkS
    mirror = False

def mm_to_nm(v):
    return int(v * 1000000)

column_width = None #Auto width#mm_to_nm(10)
offset_left = mm_to_nm(10)

pcb = pcbnew.GetBoard()

selected = [m for m in pcb.GetModules() if m.IsSelected()]
if len(selected) == 1:
    selected = selected[0]

    #bb = selected.GetBoundingBox()
    #height = bb.GetHeight() * 0.9
    #top = bb.GetTop()

    cp = [] #column positions
    rp = [] #row positions

    pads = [p for p in selected.PadsList()]
    tracknames = [t.GetNetname() for t in pcb.GetTracks()]

    #Build an X/Y list of coordinates to determine where pad positions are. 
    for p in pads:
        pos = p.GetPosition()
        if pos[0] not in cp:
            cp.append(pos[0])
        if pos[1] not in rp:
            rp.append(pos[1])

    cp.sort()
    rp.sort()

    height = abs(max(rp) - min(rp))
    height += height / len(rp)

    row_height = height / len(rp)
    top = min(rp) - row_height / 2

    if column_width == None: #Compute width
        t = pcbnew.TEXTE_PCB(pcb)
        for p in pads:
            if p.GetNetname() not in tracknames:
                continue
            else:
                t.SetText(p.GetNetname())
                column_width = max(column_width, t.GetBoundingBox().GetWidth())


    #We'll build the list to the right the width of one column away. The expectation is the user will place it where they want it. 
    for p in pads:
        #continue
        pos = p.GetPosition()
        column_number = cp.index(pos[0])
        x = offset_left + cp[0] + column_width + column_width * column_number
        pos[0] = x
        text = pcbnew.TEXTE_PCB(pcb)
        text.SetPosition (pos)
        text.SetLayer (layer)
        text.SetVisible (True)
        #text.SetTextSize (textsize)
        text.SetThickness (mm_to_nm(.1524))
        text.SetText (p.GetNetname())
        text.SetMirrored(mirror)
        if p.GetNetname() not in tracknames:
            print 'No track:%s' % p.GetNetname()
        else:
            pcb.Add (text) 

        #Draw rectangle around the text. 
        x1 = pos[0] - column_width / 2
        y1 = top + rp.index(pos[1]) * row_height
        x2 = x1 + column_width
        y2 = y1 + row_height
        print x1, y1, x2, y2

        seg = pcbnew.DRAWSEGMENT(pcb)
        seg.SetStart(pcbnew.wxPoint(x1,y1))
        seg.SetEnd(pcbnew.wxPoint(x2, y1))
        seg.SetLayer(layer)
        seg.SetWidth(mm_to_nm(0.1))
        pcb.Add(seg)

        seg = pcbnew.DRAWSEGMENT(pcb)
        seg.SetStart(pcbnew.wxPoint(x2,y1))
        seg.SetEnd(pcbnew.wxPoint(x2, y2))
        seg.SetLayer(layer)
        seg.SetWidth(mm_to_nm(0.1))
        pcb.Add(seg)

        seg = pcbnew.DRAWSEGMENT(pcb)
        seg.SetStart(pcbnew.wxPoint(x2,y2))
        seg.SetEnd(pcbnew.wxPoint(x1, y2))
        seg.SetLayer(layer)
        seg.SetWidth(mm_to_nm(0.1))
        pcb.Add(seg)

        seg = pcbnew.DRAWSEGMENT(pcb)
        seg.SetStart(pcbnew.wxPoint(x1,y2))
        seg.SetEnd(pcbnew.wxPoint(x1, y1))
        seg.SetLayer(layer)
        seg.SetWidth(mm_to_nm(0.1))
        pcb.Add(seg)
    
else:
    print 'Expected only one selection. Got %s components selected.' % len(selected)

pcbnew.Refresh()