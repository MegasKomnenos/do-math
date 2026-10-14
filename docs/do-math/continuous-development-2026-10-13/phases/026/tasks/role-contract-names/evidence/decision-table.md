# N03 역할 계약의 현재 이름 판정

행마다 이름과 occurrence 좌표는 decisions.json에 있다. source-profiles.json은 실제 정의·소비·시험 본문과 SHA를 보존한다. 제품 코드/시험은 실행하지 않았다.

| 절 | 현재 문서·행 | 판정 | 이름 수 | 정의·소비 프로필 |
|---|---|---|---:|---|
| N03-001 | 독립-운영.md:[1, 6] | keep | 2 | operator |
| N03-002 | 독립-운영.md:[7, 16] | correct-wording | 6 | operator |
| N03-003 | 독립-운영.md:[17, 22] | keep | 7 | operator, input |
| N03-004 | 독립-운영.md:[23, 39] | keep | 11 | operator |
| N03-005 | 독립-운영.md:[40, 49] | keep | 2 | operator |
| N03-006 | 독립-운영.md:[50, 59] | keep | 13 | operator |
| N03-007 | 독립-운영.md:[60, 62] | noncode-section | 0 | operator |
| N03-008 | 동일성-검토.md:[1, 4] | noncode-section | 0 | review |
| N03-009 | 동일성-검토.md:[5, 10] | keep | 10 | review, input |
| N03-010 | 동일성-검토.md:[11, 20] | keep | 25 | review-scope, review, input |
| N03-011 | 동일성-검토.md:[21, 28] | keep | 6 | review, input |
| N03-012 | 동일성-검토.md:[29, 42] | keep | 7 | review, input, extensions |
| N03-013 | 동일성-검토.md:[43, 52] | keep | 8 | review, input |
| N03-014 | 동일성-검토.md:[53, 60] | keep | 8 | review |
| N03-015 | 동일성-검토.md:[61, 68] | keep | 5 | review, input |
| N03-016 | 동일성-검토.md:[69, 76] | keep | 10 | review |
| N03-017 | 동일성-검토.md:[77, 84] | keep | 9 | review |
| N03-018 | 동일성-검토.md:[85, 92] | keep | 9 | research, review, extensions |
| N03-019 | 동일성-검토.md:[93, 107] | keep | 7 | review, input |
| N03-020 | 목표-감사.md:[1, 4] | noncode-section | 0 | goal |
| N03-021 | 목표-감사.md:[5, 14] | keep | 9 | goal, input |
| N03-022 | 목표-감사.md:[15, 24] | keep | 10 | goal, input |
| N03-023 | 목표-감사.md:[25, 34] | keep | 1 | goal |
| N03-024 | 목표-감사.md:[35, 42] | keep | 17 | goal, input |
| N03-025 | 목표-감사.md:[43, 49] | keep | 2 | goal |
| N03-026 | 보충-조사.md:[1, 4] | noncode-section | 0 | research |
| N03-027 | 보충-조사.md:[5, 14] | keep | 5 | research, work, input |
| N03-028 | 보충-조사.md:[15, 24] | keep | 6 | research, input |
| N03-029 | 보충-조사.md:[25, 32] | keep | 3 | research, extensions |
| N03-030 | 보충-조사.md:[33, 42] | keep | 10 | research, input |
| N03-031 | 보충-조사.md:[43, 52] | keep | 11 | work, input |
| N03-032 | 보충-조사.md:[53, 61] | keep | 3 | research, work |
| N03-033 | 연구-계획.md:[1, 2] | noncode-section | 0 | plan |
| N03-034 | 연구-계획.md:[3, 12] | noncode-section | 0 | plan |
| N03-035 | 연구-계획.md:[13, 36] | keep | 29 | input, plan, task, extensions |
| N03-036 | 연구-계획.md:[37, 66] | keep | 40 | plan, task, input |
| N03-037 | 연구-계획.md:[67, 94] | keep | 28 | plan, input, extensions, assessment |
| N03-038 | 연구-계획.md:[95, 102] | keep | 12 | extensions, input |
| N03-039 | 연구-계획.md:[103, 110] | keep | 19 | plan, extensions, input |
| N03-040 | 연구-계획.md:[111, 124] | keep | 11 | plan |
| N03-041 | 연구-계획.md:[125, 136] | keep | 19 | plan, input |
| N03-042 | 연구-계획.md:[137, 138] | noncode-section | 0 | plan |
| N03-043 | 연구-계획.md:[139, 142] | keep | 3 | plan |
| N03-044 | 연구-계획.md:[143, 146] | keep | 1 | plan |
| N03-045 | 연구-계획.md:[147, 150] | keep | 6 | plan |
| N03-046 | 연구-계획.md:[151, 155] | keep | 8 | plan, goal, input |
| N03-047 | 연구-수행.md:[1, 2] | noncode-section | 0 | work |
| N03-048 | 연구-수행.md:[3, 8] | noncode-section | 0 | work |
| N03-049 | 연구-수행.md:[9, 20] | keep | 9 | task, input, work |
| N03-050 | 연구-수행.md:[21, 35] | keep | 5 | task, work, input |
| N03-051 | 연구-수행.md:[36, 63] | keep | 4 | work, extensions, input |
| N03-052 | 연구-수행.md:[64, 81] | keep | 11 | input, extensions, operational |
| N03-053 | 연구-수행.md:[82, 93] | keep | 13 | work, input, declaration |
| N03-054 | 연구-수행.md:[94, 97] | keep | 7 | extensions, task, input |
| N03-055 | 연구-수행.md:[98, 103] | keep | 11 | extensions, task |
| N03-056 | 연구-수행.md:[104, 107] | noncode-section | 0 | work |
| N03-057 | 연구-수행.md:[108, 114] | keep | 5 | work |
| N03-058 | 연구-수행.md:[115, 120] | keep | 2 | work |
| N03-059 | 연구-수행.md:[121, 126] | keep | 11 | work, extensions, input |
| N03-060 | 연구-수행.md:[127, 130] | keep | 3 | work |
| N03-061 | 연구-수행.md:[131, 138] | keep | 7 | work, input |
| N03-062 | 연구-수행.md:[139, 150] | keep | 7 | work, input |
| N03-063 | 연구-수행.md:[151, 152] | noncode-section | 0 | work |
| N03-064 | 연구-수행.md:[153, 156] | keep | 3 | work |
| N03-065 | 연구-수행.md:[157, 160] | keep | 3 | work |
| N03-066 | 연구-수행.md:[161, 164] | keep | 5 | work, input |
| N03-067 | 연구-수행.md:[165, 167] | keep | 5 | work, input |
| N03-068 | 운영-점검.md:[1, 2] | noncode-section | 0 | operational |
| N03-069 | 운영-점검.md:[3, 8] | noncode-section | 0 | operational |
| N03-070 | 운영-점검.md:[9, 28] | keep | 33 | input, operational |
| N03-071 | 운영-점검.md:[29, 38] | keep | 6 | input, task, operational |
| N03-072 | 운영-점검.md:[39, 44] | keep | 11 | operational, input |
| N03-073 | 운영-점검.md:[45, 48] | keep | 4 | operational |
| N03-074 | 운영-점검.md:[49, 58] | keep | 12 | operational, operator |
| N03-075 | 운영-점검.md:[59, 62] | keep | 3 | operational |
| N03-076 | 운영-점검.md:[63, 70] | keep | 4 | operational |
| N03-077 | 운영-점검.md:[71, 74] | keep | 24 | operational, plan, task |
| N03-078 | 운영-점검.md:[75, 78] | keep | 3 | operational |
| N03-079 | 운영-점검.md:[79, 88] | keep | 13 | operational, input, extensions |
| N03-080 | 운영-점검.md:[89, 96] | keep | 7 | operational, extensions |
| N03-081 | 운영-점검.md:[97, 101] | keep | 3 | operational, input |
| N03-082 | 유지보수.md:[1, 2] | noncode-section | 0 | maintenance |
| N03-083 | 유지보수.md:[3, 10] | noncode-section | 0 | maintenance |
| N03-084 | 유지보수.md:[11, 27] | keep | 10 | maintenance, input, extensions |
| N03-085 | 유지보수.md:[28, 35] | noncode-section | 0 | maintenance |
| N03-086 | 유지보수.md:[36, 37] | noncode-section | 0 | maintenance |
| N03-087 | 유지보수.md:[38, 45] | keep | 7 | maintenance, input |
| N03-088 | 유지보수.md:[46, 49] | noncode-section | 0 | maintenance |
| N03-089 | 유지보수.md:[50, 55] | keep | 9 | maintenance, extensions |
| N03-090 | 유지보수.md:[56, 61] | noncode-section | 0 | maintenance |
| N03-091 | 유지보수.md:[62, 65] | noncode-section | 0 | maintenance |
| N03-092 | 유지보수.md:[66, 73] | keep | 3 | maintenance |
| N03-093 | 유지보수.md:[74, 81] | keep | 4 | maintenance, extensions, input |
| N03-094 | 유지보수.md:[82, 91] | keep | 2 | maintenance |
| N03-095 | 유지보수.md:[92, 111] | keep | 8 | maintenance, operator |
| N03-096 | 유지보수.md:[112, 121] | keep | 3 | maintenance |
| N03-097 | 유지보수.md:[122, 123] | noncode-section | 0 | maintenance |
| N03-098 | 유지보수.md:[124, 127] | keep | 1 | maintenance |
| N03-099 | 유지보수.md:[128, 131] | noncode-section | 0 | maintenance |
| N03-100 | 유지보수.md:[132, 135] | keep | 2 | maintenance |
| N03-101 | 유지보수.md:[136, 138] | keep | 4 | maintenance |
| N03-102 | 의도-해석.md:[1, 7] | keep | 2 | intent, input |
| N03-103 | 의도-해석.md:[8, 14] | keep | 15 | intent, input |
| N03-104 | 의도-해석.md:[15, 45] | keep | 34 | intent, input |
| N03-105 | 의도-해석.md:[46, 58] | keep | 12 | intent, input |
| N03-106 | 의도-해석.md:[59, 64] | keep | 5 | intent, input |
| N03-107 | 의도-해석.md:[65, 70] | keep | 8 | delegation |
| N03-108 | 의도-해석.md:[71, 75] | keep | 1 | intent |
| N03-109 | 작업-계약-검토.md:[1, 2] | noncode-section | 0 | contract-review |
| N03-110 | 작업-계약-검토.md:[3, 10] | noncode-section | 0 | contract-review |
| N03-111 | 작업-계약-검토.md:[11, 24] | keep | 12 | task, input, contract-review |
| N03-112 | 작업-계약-검토.md:[25, 30] | keep | 20 | task |
| N03-113 | 작업-계약-검토.md:[31, 40] | keep | 3 | task |
| N03-114 | 작업-계약-검토.md:[41, 48] | keep | 8 | task, input |
| N03-115 | 작업-계약-검토.md:[49, 60] | keep | 11 | task, plan |
| N03-116 | 작업-계약-검토.md:[61, 68] | keep | 5 | task, input |
| N03-117 | 작업-계약-검토.md:[69, 74] | keep | 2 | task, extensions |
| N03-118 | 작업-계약-검토.md:[75, 82] | keep | 4 | task, input |
| N03-119 | 작업-계약-검토.md:[83, 88] | keep | 6 | task, input |
| N03-120 | 작업-계약-검토.md:[89, 110] | keep | 20 | contract-review, input |
| N03-121 | 작업-계약-검토.md:[111, 120] | keep | 5 | contract-review |
| N03-122 | 작업-계약-검토.md:[121, 122] | noncode-section | 0 | contract-review |
| N03-123 | 작업-계약-검토.md:[123, 126] | keep | 2 | contract-review |
| N03-124 | 작업-계약-검토.md:[127, 130] | keep | 2 | contract-review |
| N03-125 | 작업-계약-검토.md:[131, 134] | keep | 4 | contract-review |
| N03-126 | 작업-계약-검토.md:[135, 138] | keep | 1 | contract-review |
| N03-127 | 작업-계약-검토.md:[139, 143] | keep | 2 | contract-review, assessment, task |
| N03-128 | 후보-준비.md:[1, 2] | noncode-section | 0 | task |
| N03-129 | 후보-준비.md:[3, 10] | noncode-section | 0 | task |
| N03-130 | 후보-준비.md:[11, 36] | keep | 15 | input, task |
| N03-131 | 후보-준비.md:[37, 38] | noncode-section | 0 | task |
| N03-132 | 후보-준비.md:[39, 56] | keep | 7 | task, work, input |
| N03-133 | 후보-준비.md:[57, 62] | noncode-section | 0 | task |
| N03-134 | 후보-준비.md:[63, 70] | keep | 3 | extensions, task |
| N03-135 | 후보-준비.md:[71, 119] | keep | 60 | task, extensions, input, assessment, condition |
| N03-136 | 후보-준비.md:[120, 161] | keep | 41 | checks, task, input |
| N03-137 | 후보-준비.md:[162, 177] | keep | 6 | task, extensions |
| N03-138 | 후보-준비.md:[178, 189] | keep | 8 | task, input |
| N03-139 | 후보-준비.md:[190, 191] | noncode-section | 0 | task |
| N03-140 | 후보-준비.md:[192, 195] | keep | 4 | task |
| N03-141 | 후보-준비.md:[196, 199] | keep | 1 | task |
| N03-142 | 후보-준비.md:[200, 203] | keep | 2 | task |
| N03-143 | 후보-준비.md:[204, 207] | keep | 1 | assessment, extensions |
| N03-144 | 후보-준비.md:[208, 241] | keep | 33 | assessment, extensions, input, condition |
