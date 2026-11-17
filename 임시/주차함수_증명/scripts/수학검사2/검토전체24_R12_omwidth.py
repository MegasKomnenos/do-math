# R12: D.band-boxes 의 Omega 조각 계수 괄호 폭 (읽기 전용; 묶음의 ivbox_lib 를 읽기만 한다)
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, r"C:/math/임시/주차함수_증명/원고_자료/세션_재계산/band_boxes")
import numpy as np
import ivbox_lib as L
print('pieces', L.OM_lo.shape, 'max bracket width', float(np.max(L.OM_hi - L.OM_lo)), 'bad', len(L.OM_bad))
