# CORE output download의 무자격 불가 판단 교차 검토

주 세션이 네보고와다른COREwork세션의원응답을대조했다. 네보고는no-key output PDF API는성공할수없다고결론냈지만, core-work-download/api-live-summary.json은2026-09-13T03:15:58Z–03:21:27Z실험에서output213561553의동일download연산이302를반환했다고기록한다. 원private api-live/positive-output-download.headers.json도Date03:16:24GMT,Location https://core.ac.uk/download/213561553.pdf,remaining4를제공한다. 이어같은파일URL의PDF양성과work파일회수도있다. 이엇갈림을해소하기전무자격API download불가결론은수용하지않는다.

읽을동료보고는같은실행폴더core-work-download/report.md·experiments.json·api-live-summary.json,원근거는그과제private_dir/api-live/다. 읽기전용으로사용하며원자료를수정하지않는다.

1. 302요청의정확URL·method·Accept·클라이언트인증헤더유무·cookie유무를실제명령/원로그에서확인한다. 토큰/인증값은출력하지않고존재여부만보고한다. key없음이확인되면그실제양성을문서요약의절대적불가주장보다우선해설명한다.
2. 공식문서의full-text제한이Work.fullText색인문자열,PDF download연산,등록사용자의사용정책중어디에적용되는지문언과현재응답으로분리한다. 일반소개·구체스키마·정책과관측의불일치를숨기지않는다.302만으로최종PDF를얻었다고세지말고동일원연쇄의최종파일을검증한다.
3. 현재request rate헤더와동일source순차실행을지켜필요한최소양성/음성대조만한다. 기존429후미래시각보다빠른재요청을반복하지않는다. day/minute/operationcost중모르는것은모른다고남긴다.
4. 원metadata downloadUrl과API download가공개무자격범위에서어떻게사용가능한지확정하고필요한설명/코드를사본에서수리한다. 기존custom retry헤더수리와공개PDF회수는보존한다. 브라우저자동fallback·새APIkey·다른source는추가하지않는다.

이새검토의목표는대조되는원증거를일관되게해석하고검증하는것이다. 과거정책문장만반복하거나현재429한번을모든무자격호출의불가증거로확대하지않는다. 새화면판독과API결속은기존계약대로수행한다.
