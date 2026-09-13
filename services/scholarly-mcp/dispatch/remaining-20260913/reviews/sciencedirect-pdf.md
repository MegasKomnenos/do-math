# ScienceDirect Preface의 남은 원 제어와 미제공 판정 재검토

주 세션이 report/experiments/visual-review와 negative-S0065230X26000631-stable.png를 직접 대조했다. 화면에는 PDF object 안의 파란 '열기' 버튼, Download full volume 제어, View full text가 있다. 원 HTML의 object는 type=application/pdf이며 정확한PII의pdfft를data로가진다. View full text는ClinicalKey프록시로향하므로이를ScienceDirect내부HTML이라고추정하지않는다. 실험원장은별도View PDF링크클릭만기록하고object의열기·full-volume제어는실행하지않은채same-record HTML loop를not_offered로분류했다.

1. 새전용세션의현재화면을직접읽고object의열기제어와현재프레임/MIME처리를확인한다. viewer placeholder, disabled PDF plugin,실제PDF,오류HTML을구별한다. 좌표는새화면으로계산하며옛좌표를재사용하지않는다.
2. View PDF와object data의원주소·query·요청문맥이같은지비공개로대조한다. 각제어의정상동작전후 request/response/frame/download event를결속한다. MIME설정이나새탭처리문제를원파일부재로분류하지않는다.
3. 같은자료원의Download full volume이실제로제공하는형식·범위·해당Preface포함여부를정상제어로확인한다. 전권PDF를개별Preface원PDF로표시하지않는다. 컨테이너에해당문헌이있으면원컨테이너·정확페이지범위·출처를구별해보고한다. 예상밖결제나새자격이필요하면그경계에서멈추고독립실험을계속한다.
4. ClinicalKey연결은다른플랫폼경계로정확히기록하며생산ScienceDirect호출이자동으로다른자료원에넘어가게만들지않는다. 같은PII의HTML복귀만으로not_offered를확정한분류가타당한지도재검토한다. 단순해결실패이면error/unresolved와확정된미제공을구별한다.

기존양성31쪽PDF와비구독표본을보존한다. 해결되면최소수리·회귀·새SDK를검증한다. 실패하면남은제어별실제관측과source내제공범위를명시한다. 원파견의전용쓰기·자격·최대동시·직접이미지판독계약을유지한다.
