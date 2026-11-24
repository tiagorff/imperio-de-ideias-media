import sys, os; sys.argv=["x","none"]
import ep02 as E
from ep02 import *
surf = skia.Surface(W, H)
with surf as cv:
    cv.clear(C(BG0)); E.background(cv, 3.0)
    E.river(cv, 3.0, W/2, 420, 1500, 1.0, 230)
    E.factory_art(cv, W/4, 1180, .8, 1.0, GD, smoke_t=2.0)
    E.factory_art(cv, 3*W/4, 1180, .8, 1.0, GD, smoke_t=3.0)
    E.txt(cv, "PUMA", W/4, 1400, TF_B, 80, WH, 255, track=6); E.txt(cv, "ADIDAS", 3*W/4, 1400, TF_B, 80, WH, 255, track=6)
    cv.drawRect(skia.Rect.MakeXYWH(0, 560, W, 420), lin(0,560,0,980,[("#000000",0),("#000000",170),("#000000",0)]))
    E.kicker(cv, "OS IRMÃOS DASSLER", 620, 255)
    E.txt(cv, "A BRIGA QUE", W/2, 780, TF_B, 170, WH, 255, track=4)
    E.txt(cv, "DIVIDIU UMA CIDADE", W/2, 930, TF_B, 140, GD, 255, track=3)
    E.finish(cv, 3.0)
    E.txt(cv, "IMPÉRIO DE IDEIAS", W/2, 300, TF_SB, 28, WH, 170, track=6, shadow=False)
img = surf.makeImageSnapshot(); img.save("capa.png", skia.kPNG)
