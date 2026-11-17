# 수리 전체24 ZL — 묶음 7: 1.2↔7절 대조의 「다른 양」 안내 열셋을 기록 원문으로 훑다가 찾은 한 자리.
# 1.2·부록 A의 n^sharp_k 행이 [r39ba7c1]의 N^#_k와 [rc9aee43]의 N_k를 한 덩어리로 n_*=⌈k²/4⌉에 맞세운다.
# 기록 [r39ba7c1]의 N^#_k는 min(N_k, Ñ_k)(N_k=k(q_k+1), Ñ_k=k(2t_k+1); exposition §8·peer-quadratic-prefix.md)로 ⌈k²/4⌉가 아니고,
# 7절의 t_k·n^sharp_k 행은 이미 「이 글이 쓰지 않는 다른 양」으로 적는다. ⌈k²/4⌉는 [rc9aee43]의 N_k뿐이다(exposition 236행).
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from 수리전체24_ZL_apply import apply
BASE = os.path.dirname(os.path.dirname(HERE))
J = os.path.join(BASE, '장부_v2.md')
A = os.path.join(BASE, '장v2', '부록A.md')
for dry in (True, False):
    apply(J, [(r'''[r39ba7c1]의 $N^\#_k$(기록의 경계)·[rc9aee43]의 $N_k=\lceil k^2/4\rceil$는 보조정리 `{{7:column-lemma}}`(다)의 정수 $n_\ast=\lceil k^2/4\rceil$(1.3 7.2 묶음; 2026-11-15 4차 J6 5절·9차 O6 5절) |''',
               r'''[r39ba7c1]의 $N^\#_k=\min(N_k,\tilde N_k)$는 이 글이 쓰지 않는 다른 양(7절 $\mathsf t_k$, $n^\sharp_k$ 행); [rc9aee43]의 $N_k=\lceil k^2/4\rceil$는 보조정리 `{{7:column-lemma}}`(다)의 정수 $n_\ast=\lceil k^2/4\rceil$(1.3 7.2 묶음; 2026-11-15 4차 J6 5절·9차 O6 5절; 두 기록의 글자를 한 덩어리로 $n_\ast$에 맞세운 꼴이던 것을 2026-11-18 24차 ZL이 두 기록 원문으로 확인해 가름) |''')], dry)
    apply(A, [(r'''[r39ba7c1]의 $N^\#_k$(기록의 경계)·[rc9aee43]의 $N_k=\lceil k^2/4\rceil$는 보조정리 {{7:column-lemma}}(다)의 정수 $n_\ast=\lceil k^2/4\rceil$ |''',
               r'''[r39ba7c1]의 $N^\#_k=\min(N_k,\tilde N_k)$는 이 글이 쓰지 않는 다른 양; [rc9aee43]의 $N_k=\lceil k^2/4\rceil$는 보조정리 {{7:column-lemma}}(다)의 정수 $n_\ast=\lceil k^2/4\rceil$ |''')], dry)
