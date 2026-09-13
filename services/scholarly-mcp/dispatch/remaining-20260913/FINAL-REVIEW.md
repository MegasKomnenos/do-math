# 조사 누락과 성급한 종료 판단의 최종 검토

사용자가 '더 있는지 최종 검토, 없으면 없다고' 지시한 범위에서24개 과제의 현재 반환·실험 원장·화면 판독 기록·성공 범위와 남은 조건을 대조했다. 이번 최종 검토는 추가 조사 없이 불가·소진·완료로 닫아도 되는지의 판단이다. 사본 코드 전체의 독립 검증·원본 통합 완료를 뜻하지 않는다.

**기존 재검토5개 외에 추가5개를 확인했다. 이 다섯 개 이외에 이번 자료에서 입증된 추가 재조사 항목은 없다.** 가능성을 상상할 수 있다는 이유만으로 항목을 늘리지 않았다. 추가5개는 모두 현재 원기록에 나타난 미검증 제어, 상충 관측, 미해명 결과를 근거로 한다. 해결책의 존재를 미리 확정한 것은 아니다.

| 추가 과제 | 직접 대조한 사실 | 종료 전에 필요한 검증 |
|---|---|---|
| ScienceDirect Preface PDF | 원화면에PDF영역의열기,Download full volume이있고원HTML의object가같은PII의pdfft를가리킴. 원장은별도View PDF링크만시험 | object/viewer와전권제어의실제요청·파일·범위. 단순HTML복귀를확정미제공으로분류할수있는지 |
| CORE output download | output과제는no-key성공불가로결론. work과제는같은output API의302를기록하며원헤더도Date03:16:24GMT·동일CORE파일Location·remaining4 | 같은요청의인증상태·문서fullText와PDF정책범위·원연쇄파일을대조해상충결론해소 |
| Figshare 과거구성원 |4046897 v8의metadata/currentREST21과UI/GraphQL20불일치. 이표본을제외하고다른2/3양성표본으로종료 | 정확누락ID와판본/색인/공개성/삭제/커서원인. 정상부분결과보존과count guard |
| Numdam 한쪽날짜 |until만은전체76,864·from만은92·같은연도양경계359. 의미미확정뒤한쪽입력을선제거부 | 실제입력·직렬화·공식문법으로의미와가능한표현을확정. 기존양경계성공과분리 |
| SIAM Author 조건 |없을것으로가정한Author조건이1,320건을반환해Title음성으로교체했으나Author현상미해명 | 정상저자·희귀알파벳·underscore·빈조건의원UI/요청/결과대조. 문법특성·조건무시·결속오류구별 |

ScienceDirect의View full text는원HTML에서ClinicalKey프록시를가리키므로이를같은자료원의HTML해법으로계산하지않았다. 전권PDF도개별Preface원PDF로바꾸어부르지않도록했다. Numdam Date NOT은숨은제어와음성문법대조가이미있으므로그것만으로새항목을만들지않았다. CORE302는목적지헤더가실재한다는것과무자격전체API기능이보장된다는것을구별해추가검증하도록했다.

## 나머지 판정

기존5개(AMS·SIAM기관·Oxford·DeGruyterZIP·SemanticScholar)는이미구체공백을지정해재검토중이므로중복집계하지않았다. CORE work는원래의계속진행과제로별도유지한다. 새수리결과가나와도다른CORE과제의상충된불가주장을자동수용하지않는다.

DBLP·EuDML NLM·CORE files01·DeGruyter citation·ScienceDirect export·DBLP KG·Crossmark는요청기능의실제양성과검증자료가있고,이번종료판단검토에서추가의구체누락을입증하지못했다. 각각의사본코드검토·공통파일병합·통합회귀는여전히남는다. EuDML의당시검색504/유지보수는보고가별도미해결외부상태로남겼으므로NLM성공에감춰진것으로지적하지않았다.

JSTOR video의확인표본native download disabled, Taylor두편집자글의초록부재, Springer한구형문헌의HTML부재는해당표본안에서원화면·응답·양성대조가결합됐다. 전체자료원이나미래자료의영구불가로확대하지않는조건으로추가재조사근거없음으로판정했다. SWH특정flat작업new는미완료로남고개별파일회수와다른양성작업은구별됐다. 현재원계약에없는강제재큐잉이나다른원본으로대체할것을새해법으로간주하지않았다. IEEE의falseMediaflag반례는55표본에서없었고별도MP4parser수리는양성이어서둘을혼합하지않았다.

## 후속 실행

추가5개의정본지시는reviews/sciencedirect-pdf.md, core-output-download.md, figshare-historical-members.md, numdam-date-only.md, siam-last-condition.md다. 실행폴더20260913T021511Z의작업별review-01.md와review-requests.json에반영했다. 운영기는기존같은thread·사본을재사용하며최대8개·동일source순차제약을유지한다. 기존5개를합쳐재검토요청은10개다. 대기중인재검토를실행완료로표시하지않는다.
