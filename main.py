import os
import matplotlib as plt
import matplotlib.font_manager as fm
import patchworklib as pw
from QUEEN.queen import *
from QUEEN import cutsite #Import a restriction enzyme library 
import Bio
from sangerseq_viewer import sangerseq_viewer

fig = sangerseq_viewer.view_sanger(gbkpath='data/inputs/Bartonella bacilliformis testing.gb', 
                                   abipath='data/inputs/B_bacilliformis_CSH1f.ab1', 
                                   output='B_bacilliformis_CSH1f.png')

fig.savefig('data/outputs/B_bacilliformis_CSH1f.png')

plt.cla()
plt.clf()
plt.close()