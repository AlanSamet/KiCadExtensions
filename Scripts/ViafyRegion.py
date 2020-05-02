#execfile(r'C:\Users\Admin\Documents\KiCad\Scripts\ViafyRegion.py')

#By Alan Samet
#
#This script could still use some refinement. It was one of my first scripts that I wrote. 
#If you hava a region on your PCB and want to put a bunch of vias in it, select the regions
#in pcbnew and then run this script. It will place vias defined within this script in a grid.

import pcbnew
import decimal

column_width_mm = 2

#tt = pcb.GetTracks() #Get vias

def mm_to_nm(v):
    return int(v * 1000000)

x_interval = mm_to_nm(column_width_mm)#0.05
y_interval = x_interval
v_diameter = mm_to_nm(0.3)

pcb = pcbnew.GetBoard()

def viafy_area(area):
    #all_vias = [t for t in pcb.GetTracks() if t.GetClass() == 'VIA']
    bb = area.GetBoundingBox()
    top = bb.GetTop()
    bottom = bb.GetBottom()
    left = bb.GetLeft()
    right = bb.GetRight()
    #netName = area.GetNetname()
    net = area.GetNet()
    #print net.GetNet()
    for x in range(left, right, x_interval):
        for y in range(top, bottom, y_interval):
            pt = pcbnew.wxPoint(x, y)
            if pcb.GetViaByPosition(pt):
                continue
            #print pt
            if area.HitTestFilledArea(pt):
                if not area.HitTestFilledArea(pcbnew.wxPoint(x - x_interval/2, y)):
                    continue 
                if not area.HitTestFilledArea(pcbnew.wxPoint(x + x_interval/2, y)):
                    continue 
                if not area.HitTestFilledArea(pcbnew.wxPoint(x, y - y_interval/2)):
                    continue 
                if not area.HitTestFilledArea(pcbnew.wxPoint(x, y + y_interval/2)):
                    continue 
                #print 'hittest yes'
                v = pcbnew.VIA(pcb)
                v.SetPosition(pt)
                v.SetDrill(v_diameter)
                v.SetWidth(v_diameter*2)
                #v.SetNetname(netName)
                v.SetNetCode(net.GetNet())
                pcb.Add(v)
                

for i in range(pcb.GetAreaCount()):
    a = pcb.GetArea(i)
    if a.IsSelected():
        print 'Selected'
        viafy_area(a)
    else:
        print 'not'

pcbnew.Refresh()