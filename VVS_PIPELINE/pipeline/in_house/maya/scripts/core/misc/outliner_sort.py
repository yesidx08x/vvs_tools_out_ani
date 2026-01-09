from itertools import groupby
import pymel.core as pm
def keyfunc(s):
    s = [str(x) for x in s]
    return [int(''.join(g)) if k else ''.join(g) for k, g in groupby(s, str.isdigit)]
def main():
    selected = pm.ls(sl = 1, fl = 1)
    maGroups = [x for x in selected if not x.getShape()]
    selected = list(set(selected)-set(maGroups))
    selected.sort(key=keyfunc);maGroups.sort(key=keyfunc)
    for sel in maGroups+selected:
        pm.reorder( sel, back=True )