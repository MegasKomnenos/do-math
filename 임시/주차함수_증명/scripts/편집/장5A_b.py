# -*- coding: utf-8 -*-
"""장5A 편집 2묶음: 7.5절의 용어 「토막」을 다른 뜻으로 쓴 자리(정수 구간, 적분 경로의 선분과 호)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""그 모형에서는 정수 구간 $[1,d]$를 이어진 정수 토막들로 나누고(토막 하나가 타일이다) 토막마다 길이에 따른 무게를 준다.""",
 r"""그 모형에서는 정수 구간 $[1,d]$를 이어진 정수 구간들로 나누고(그 구간 하나가 타일이다) 타일마다 길이에 따른 무게를 준다."""),

(r"""바깥 적분을 단위원으로, 안쪽 적분을 실수 토막과 호 토막으로 나누어 계산한다.""",
 r"""바깥 적분은 단위원 위에서 적고, 안쪽 적분은 실수축 위의 선분과 호로 나누어 계산한다."""),

(r"""실수 토막 $\mathrm{pt}'=1-v$에서""",
 r"""선분 $\mathrm{pt}'=1-v$에서"""),

(r"""로 이 토막은 $\mathrm{Bor}(k)\mathrm{ku}^2\bigl[\hat{\mathrm{Wr}}_2""",
 r"""로 이 선분의 기여는 $\mathrm{Bor}(k)\mathrm{ku}^2\bigl[\hat{\mathrm{Wr}}_2"""),

(r"""호 토막에서는""",
 r"""호에서는"""),

(r"""그러므로 이 토막은 $\mathrm{Bor}(k)\mathrm{ku}^2\bigl[\frac{\mathrm{Ce}_2}4""",
 r"""그러므로 호의 기여는 $\mathrm{Bor}(k)\mathrm{ku}^2\bigl[\frac{\mathrm{Ce}_2}4"""),

(r"""두 토막을 더하면""",
 r"""둘을 더하면"""),

(r"""안쪽 적분을 같은 두 토막으로 나눈다. 실수 토막 $\mathrm{pt}_0=1-v$에서""",
 r"""안쪽 적분을 같은 선분과 호로 나눈다. 선분 $\mathrm{pt}_0=1-v$에서"""),

(r"""이므로 이 토막은 $e^{-1}e^{-3(k-1)/2}\mathfrak J_k$다. 호 토막 $\mathrm{pt}_0=e^{\mathrm i\mathrm{ag}'}$에서""",
 r"""이므로 선분의 기여는 $e^{-1}e^{-3(k-1)/2}\mathfrak J_k$다. 호 $\mathrm{pt}_0=e^{\mathrm i\mathrm{ag}'}$에서"""),

(r"""이므로 이 토막은 $e^{-1}e^{-3(k-1)/2}\mathrm{ku}^2\mathrm{Cb}(\hat{\mathrm{ag}})$다.""",
 r"""이므로 호의 기여는 $e^{-1}e^{-3(k-1)/2}\mathrm{ku}^2\mathrm{Cb}(\hat{\mathrm{ag}})$다."""),
]

if __name__ == "__main__":
    apply("장5A.md", PAIRS, dry="--dry" in sys.argv)
