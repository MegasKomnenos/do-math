"""Serialize this task's reviewed judgments and verify their concrete coordinates; no product imports."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
from analyze import REPO, RUN, OUT, NAMES, resolve, sha, save

P = 'repo:.claude/skills/do-math/'
S = P + 'scripts/'
D = S + 'do_math/'
T = S + 'tests/'
E = 'run:phases/026/tasks/policy-semantics/evidence/'

def loc(ref, first, last, symbol):
    return {'reference': ref, 'lines': [first, last], 'symbol': symbol}

EXCERPTS = [
    loc(P+'README.md',146,157,'N01-020 policy sentence'),
    loc(P+'references/CLI-실행-계약.md',150,154,'N01-218 defaults owner'),
    loc(P+'references/CLI-실행-계약.md',622,639,'N01-230 conversation input and example'),
    loc(P+'references/CLI-실행-계약.md',977,1000,'N01-268 model_policy failure row'),
    loc(P+'references/초기화-운전.md',162,198,'N01-273 probe/adopt sentence and example'),
    loc(D+'initialization_engine.py',9,18,'_require_current_config'),
    loc(D+'initialization_engine.py',21,145,'_initialization_control'),
    loc(D+'initialization.py',21,76,'capability_requirements/_capability_batch_requirements'),
    loc(D+'initialization.py',186,274,'activation_requirements/grant_current'),
    loc(D+'initialization.py',277,303,'initialize_state'),
    loc(D+'lifecycle_engine.py',27,34,'conversation_lease_live'),
    loc(D+'lifecycle_engine.py',126,177,'pause/conversation/resume'),
    loc(D+'lifecycle_engine.py',180,272,'activation and dispatch gate'),
    loc(D+'lifecycle_engine.py',367,525,'execution stop, preserved user control and conversation'),
    loc(D+'configuration.py',1,61,'DEFAULT_CONFIG/validate_config'),
    loc(D+'model_policy.py',1,21,'MODELS/LIMITS/ROLE_TIERS'),
    loc(D+'model_policy.py',110,174,'validate_policy/selection/work_profile_selection'),
    loc(D+'execution_profiles.py',205,277,'build_profiles/apply_editions'),
    loc(D+'execution_profiles.py',299,358,'select_profile/runtime_config/runner_tools'),
    loc(D+'model_call.py',143,170,'classify_run lock prefix'),
    loc(D+'provider_engine.py',8,13,'record_model_policy_violation'),
    loc(D+'call_engine.py',376,426,'_call_stop_requested'),
    loc(D+'call_engine.py',465,533,'_receive_call model violation recording and pause'),
    loc(D+'execution_window.py',1,28,'deadlines and non-revoking notice'),
    loc(D+'supervision.py',15,64,'supervision_facts/supervision_block'),
    loc(D+'scheduled_operator.py',98,134,'HOLD marker hold/release'),
    loc(D+'scheduled_operator.py',182,208,'engine_start_guard HOLD first'),
    loc(D+'scheduled_operator.py',230,253,'check HOLD first'),
    loc(D+'external_engine.py',10,50,'_external_control prepare'),
    loc(D+'external_engine.py',163,219,'_run_external_action send-time validation'),
    loc(D+'external.py',38,114,'validate_operation/execute_operation'),
    loc(D+'governance.py',384,469,'grant interval/scope/authorize/source approval'),
    loc(D+'review_policy.py',36,81,'build_review_policy'),
    loc(D+'control_contracts.py',122,130,'DECISION adoption payload'),
    loc(D+'control_contracts.py',182,187,'conversation payload'),
    loc(D+'record_schemas/schemas.py',562,568,'stored conversations schema'),
    loc(D+'record_schemas/schemas.py',624,647,'instance/lifecycle adoption schema'),
    loc(T+'support/doc_code.py',695,727,'lexical policy owner checker'),
    loc(T+'structure/test_doc_code.py',813,827,'lexical tests'),
    loc(T+'sim/test_lifecycle_engine_public.py',195,294,'delivery/expiry/new-generation boundary assertions'),
    loc(T+'sim/test_lifecycle_engine_controls.py',401,444,'attach policy, omission, loss, replay'),
    loc(T+'sim/test_engine_lifecycle_gates.py',41,68,'activation/pause initial phase'),
    loc(T+'sim/test_engine_lifecycle_gates.py',126,130,'continue_authorized with zero connections'),
    loc(T+'sim/test_initialization_controls.py',105,119,'probe configuration hash'),
    loc(T+'sim/test_initialization_controls.py',156,180,'user authority for public initialization control'),
    loc(T+'sim/test_initialization_controls.py',217,225,'review adoption digest currentness'),
    loc(T+'sim/test_initialization_controls.py',261,290,'valid policy values and stored decisions'),
    loc(T+'sim/test_initialization_controls.py',336,379,'stale adoption and current public configuration'),
    loc(T+'boundary/test_engine_cli_advanced.py',101,117,'stored explicit pause and external prepare'),
    loc(T+'flows/test_engine_cli_journey.py',87,101,'real CLI probe/adoption consumer'),
    loc(T+'flows/test_engine_cli_journey.py',141,162,'activation returns before research execution'),
    loc(T+'sim/test_call_stop_flags.py',165,186,'user pause and revocation stop propagation'),
    loc(T+'sim/test_call_stop_flags.py',231,261,'grant expiry/conversation loss stop propagation'),
    loc(T+'sim/test_operator_finish_recovery.py',252,292,'HOLD blocks recovery without repeated calls'),
    loc(T+'sim/test_academic_external_control_validation.py',33,56,'disabled/missing grant/actor mismatch no effects'),
    loc(T+'sim/test_lifecycle_engine_external.py',56,94,'success and revocation before send'),
    loc(T+'unit/test_academic_external_validation.py',43,58,'HTTP grant routing scope no effects'),
    loc(T+'unit/test_provider_profile_selection.py',89,137,'profile pinning and role floor/allowlist'),
    loc(T+'flows/test_scheduling_close_capability.py',39,104,'model mismatch through worker and stored result'),
    loc('repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md',1172,1201,'13-A/B/C and preserved limits'),
    loc('repo:docs/do-math/시험-재편-2026-09-29/설계.md',277,309,'meaningful assertions independent expectation'),
    loc('repo:docs/do-math/시험-재편-2026-09-29/설계.md',500,502,'soft time budget correction'),
    loc(T+'시험-지침.md',129,157,'source freeze/test authoring rules'),
]

METHODS = {
    'conversation_loss_policy': ['test_independent_operation_does_not_require_a_conversation_lease',
        'test_conversation_lease_boundary_agrees_for_resume_heartbeat_and_loss',
        'test_continue_policy_does_not_pause', 'test_pause_publishes_a_stop',
        'test_revoked_grant_publishes_a_stop', 'test_grant_expiry_is_a_clock_comparison',
        'test_conversation_lease_expiry_stops_under_the_pause_policy',
        'test_probe_routes_published_diagnosis_and_hold_blocks_recovery',
        'test_activation_requires_recorded_evidence_then_opens_the_correct_first_action'],
    'disconnect_policy': ['test_heartbeat_is_judged_at_delivery_and_cannot_revive_an_expired_generation',
        'test_resume_requires_a_live_generation_newer_than_the_lost_generation',
        'test_conversation_requires_new_live_generation', 'test_continue_alias_is_rejected_without_changing_conversation',
        'test_control_replay_and_atomic_rejection', 'test_external_prepare_is_model_free_and_conversation_lifecycle'],
    'model_policy': ['test_selection_is_pinned_and_contract_allowlist_is_enforced',
        'test_explicit_old_edition_uses_its_model_but_preserves_floor_and_allowlist',
        'test_ai_selection_uses_adopted_editions_without_building_or_reading_lean',
        'test_wrong_reported_model_pauses_after_the_real_bound_worker_returns'],
    'external_policy': ['test_prepare_rejects_policy_that_disables_effects',
        'test_prepare_rejects_missing_or_non_http_grant', 'test_prepare_rejects_actor_kind_different_from_actual_profile',
        'test_grant_scope_rejections_do_not_send_or_persist', 'test_authority_revoked_at_send_gate_prevents_transport'],
    'adopt_default_review_policy': ['test_a_changed_intent_receipt_or_unadopted_review_policy_is_missing',
        'test_a_repeated_adoption_names_its_source_once_and_records_each_decision',
        'test_probe_without_named_editions_must_name_the_current_configuration',
        'test_adoption_of_a_configuration_other_than_the_current_one_is_rejected',
        'test_user_refreshes_exact_active_profile_and_other_authority_is_rejected',
        'test_public_default_init_rejects_unready_adoption_then_adopts_the_configured_one'],
}

def test_coordinates():
    wanted = {name for values in METHODS.values() for name in values}
    found = {}
    for path in (REPO/'.claude/skills/do-math/scripts/tests').rglob('test_*.py'):
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name in wanted:
                        ref = 'repo:' + path.relative_to(REPO).as_posix()
                        identifier = path.relative_to(REPO/'.claude/skills/do-math/scripts/tests').with_suffix('').as_posix().replace('/', '.') + '.' + node.name + '.' + method.name
                        found.setdefault(method.name, []).append({'id': identifier, 'reference': ref,
                            'lines': [method.lineno, method.end_lineno], 'sha256_current': sha(path)})
    assert set(found) == wanted, sorted(wanted-set(found))
    return {policy: [row for method in values for row in found[method]] for policy,values in METHODS.items()}

def historical_rows(bindings):
    refs = ['repo:docs/do-math/시험-재편-2026-09-29/검증/2026-10-06-일반통합-B129/report.json',
        'run:phases/007/tasks/provider-consumers/evidence/consumers-final/report.json',
        'run:phases/018/tasks/job-cleanup/evidence/c4/report.json',
        'run:phases/025/tasks/document-trust/evidence/c2/report.json']
    wanted = {row['id']: row for values in bindings.values() for row in values}
    selected = []
    source_comparisons = []
    for ref in refs:
        report = json.loads(resolve(ref).read_text(encoding='utf-8-sig'))
        sources = report['source_sha256']
        rows = [row for group in report['reports'] for row in group['rows']]
        for row in rows:
            if row['id'] not in wanted:
                continue
            test = wanted[row['id']]
            key = test['reference'].split('/scripts/',1)[1]
            assert row['id'] in report['selected']
            selected.append({'report': ref, 'report_sha256': sha(resolve(ref)), 'row': row,
                'test_sha256_report': sources.get(key), 'test_sha256_current': test['sha256_current'],
                'same_test_bytes': sources.get(key) == test['sha256_current'],
                'scope': 'Historical execution of this exact row; changed transitive support/runtime prevents whole-edition reuse.'})
        relevant = ['do_math/initialization_engine.py','do_math/initialization.py','do_math/lifecycle_engine.py',
            'do_math/model_policy.py','do_math/execution_profiles.py','do_math/model_call.py',
            'do_math/provider_engine.py','do_math/call_engine.py','do_math/external.py','do_math/external_engine.py',
            'do_math/governance.py','do_math/review_policy.py','do_math/configuration.py','do_math/supervision.py',
            'do_math/scheduled_operator.py','tests/support/sim.py','tests/support/model.py',
            'tests/support/engine_lifecycle.py','tests/support/provider_runs.py','tests/support/engine_context.py',
            'tests/support/operator_finish_scene.py','tests/support/port_contracts/jobs.py']
        source_comparisons.append({'report': ref, 'complete': report['complete'], 'successful': report['successful'],
            'counts': report['counts'], 'sources': {key: {'historical_sha256': sources.get(key),
                'current_sha256': sha(REPO/'.claude/skills/do-math/scripts'/key),
                'same_bytes': sources.get(key)==sha(REPO/'.claude/skills/do-math/scripts'/key)} for key in relevant}})
    observed = {row['row']['id'] for row in selected}
    assert set(wanted) <= observed, sorted(set(wanted)-observed)
    return {'rows': selected, 'relevant_source_comparisons': source_comparisons,
            'new_execution': False, 'whole_edition_reuse': False}

def history_review():
    commits = [('B57','cd2f7fe4',[P+'scripts/tests/support/doc_code.py',P+'scripts/tests/structure/test_doc_code.py',P+'references/CLI-실행-계약.md']),
               ('B64','d8e25c55',[P+'references/CLI-실행-계약.md'])]
    review = []
    for label, commit, refs in commits:
        args = ['git','show',commit,'--']+[r.split(':',1)[1] for r in refs]
        result = subprocess.run(args, cwd=REPO, capture_output=True, check=True)
        (OUT/('history-'+label+'.diff')).write_bytes(result.stdout)
        review.append({'history':label,'commit':commit,'argv':args,'exit_code':result.returncode,
                       'diff_sha256':hashlib.sha256(result.stdout).hexdigest()})
    board = json.loads(resolve('repo:docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json').read_text(encoding='utf-8-sig'))
    for label, key in [('B57','document_contract_integration'),('B64','operation_document_integration')]:
        entry = board['current_work'][key]
        reports = []
        for subkey in ['changed_area','structure','initial_document_failures']:
            if subkey in entry:
                path = Path(entry[subkey]['path'])
                reports.append({'selector':f'current_work/{key}/{subkey}/path',
                    'path':str(path),'exists':path.is_file(),
                    'sha256':sha(path) if path.is_file() else None,
                    'claim':entry[subkey]})
        next(r for r in review if r['history']==label)['original_reports']=reports
    old = subprocess.run(['git','show','cd2f7fe4:.claude/skills/do-math/scripts/tests/support/doc_code.py'],cwd=REPO,capture_output=True,check=True).stdout.decode('utf-8')
    current = resolve(T+'support/doc_code.py').read_text(encoding='utf-8-sig')
    def functions(text):
        tree=ast.parse(text)
        return {n.name:ast.get_source_segment(text,n) for n in tree.body if isinstance(n,ast.FunctionDef)}
    a,b=functions(old),functions(current)
    review[0]['policy_functions_text_unchanged']={name:a[name]==b[name] for name in ['declared_policy_names','policy_issues','documented_policies']}
    review[0]['disposition']='유지: 미정의 이름 반려와 소유 존재 검사는 그대로 필요하다. 의미 인증으로 승격하지 않으며 이번 특정 문구는 별도 교정 후보다. B57 전체/PR24 전체 종료 아님.'
    review[1]['disposition']='이번 다섯 이름의 의미를 변경하는 hunk 없음. B64 counts를 재사용하거나 대기/복구/학술 hunk를 새로 종결하지 않는다.'
    save('history-review.json',review)

DECISIONS = [
    {'name':'conversation_loss_policy','classification':'유지',
     'meaning':'인스턴스의 현행 대화 소실 정책. pause와 continue_authorized만 채택·attach에서 유효하다. continue_authorized는 대화 임대를 연구 권한으로 바꾸지 않고 대화 연결 선행조건만 제거한다.',
     'production_storage_authority':'사용자 초기화 decision은 _apply_extended_control의 origin 검사 및 원문 보존을 거쳐 instance.conversation_loss_policy에 적용된다. 이후 attach의 명시/생략 선택이 현행 값을 갱신한다. 사용자 source와 decisions.change 및 runtime.extended_controls에 요청 근거를 남긴다. initialization adoption은 활성 계약을 대체할 수 없다.',
     'consumption':'_conversation_live는 pause에서만 connected, lease_expires_at>now 및 lost generation보다 새 generation을 요구한다. _lose_conversation은 연결 행의 옛 정책보다 instance 현행 정책을 먼저 읽는다. pause는 lost 행/세대와 lifecycle/runtime/모든 미종결 실행의 stop 요청을 기록하며 attach 자체는 resume하지 않는다. continue_authorized는 zero-connection이나 임대 소실로 일시 정지하지 않는다.',
     'limits':'활성화 관문은 두 정책 모두 허용한다. 초기화 satisfied/active는 독립 운전의 continue_authorized 승인을 뜻하지 않는다. 사용자 pause, HOLD 감독 경계, grant [valid_from,expires_at)와 철회/현재성·종료 장벽은 각각 남는다. HOLD는 감독의 시작/복구를 막는 marker이며 직접 연구 정지인 user pause와 구별한다. 제한 복구의 기존 별도 허가는 바꾸지 않는다.',
     'judgment':'README152와 초기화182의 독립 운전·승인·정지 문장은 유지 후보다. 실행을 관측한 근거는 historical-execution의 정확 row이고 현 consumer/시험의 소스 대조는 source-excerpts다. 모든 전이/제품 운전을 새로 인증한 결과가 아니다.',
     'next_action':'이 한정 의미 질문을 종결 후보로 처리하고 유효한 기존 단언을 후속 통합·최종 판본 실행에 포함한다. 현행 정책을 자동 변경하지 않는다.'},
    {'name':'disconnect_policy','classification':'시험 공백',
     'meaning':'conversation attach 요청의 선택 필드이며 저장 연결 행의 선택된 정책이다. instance config의 설정 키가 아니다. generation 양의 정수/엄격 증가, 공개 lease 양의 정수 계약을 따르며 null/continue 별칭은 유효하지 않다.',
     'production_storage_authority':'_conversation_control attach는 config.get(disconnect_policy,instance.conversation_loss_policy)로 고르고 runtime.conversations[id].disconnect_policy와 instance.conversation_loss_policy 양쪽에 같은 값을 저장한다. 생략은 현재값 재사용이며 명시 값은 현행 정책을 바꾼다. schema/control/records와 저장 요청 원문은 source-excerpts에 있다.',
     'consumption':'heartbeat는 현재 connected 세대와 전달 시점의 live lease를 요구하고 기존 lease_seconds로 갱신한다. expired/detached 세대의 heartbeat와 같은 generation 재attach는 반려된다. 소실은 현행 인스턴스 정책을 읽으며 이전 연결 행의 정책을 무조건 우선하지 않는다.',
     'limits':'기존 boundary explicit pause는 저장 instance policy/lost를 직접 단언한다. sim의 재attach 생략 사례와 경계 시각 시험은 live/resume/loss를 단언하지만 생략 뒤 연결 행의 disconnect_policy와 instance policy가 각각 현행 값을 그대로 저장했다는 독립 기대 및 restart 후 전건 일치 단언은 없다. 비교 전후 self-derived dict만으로 저장 필드의 오염을 검출할 수 없다. 현재 코드의 결과는 문장과 같고 실제 제품 반례는 관측하지 않았다.',
     'judgment':'CLI625/628 문장·예제는 유지. 저장 의미를 보호하는 작은 시험 보강 후보를 반환한다. 정의 존재 검사에 일반 정책 evaluator를 더하지 않는다.',
     'next_action':'기존 PublicLifecycleTests의 test_resume_requires_a_live_generation_newer_than_the_lost_generation 또는 test_conversation_lease_boundary_agrees_for_resume_heartbeat_and_loss를 보강한다. 기존 활성 Sim의 instance continue_authorized에서 attach pause, 새 세대로 정책 생략, 필요하면 반대 방향 continue_authorized를 수행하고 각 단계의 양쪽 정책 및 source_ref/generation을 독립 기대와 restart 후 저장값으로 확인한다. 실제 함수·저장은 유지하며 신규 제품 분기를 만들지 않는다.'},
    {'name':'model_policy','classification':'유지',
     'meaning':'CLI152에서는 do_math.model_policy 모듈이 MODELS/ROLE_TIERS/LIMITS 기본값을 소유한다는 이름. CLI993에서는 잠금 불일치의 error_kind=model_policy 분류다. tier_models/role_tiers/session_limits와 claude_only_assigned_model이 실제 설정 필드이고 model_policy 단독 config 키는 없다. 개발 서비스 세션 모델 정책과 제품 기본값은 별개다.',
     'production_storage_authority':'configuration.DEFAULT_CONFIG가 모듈 정의를 deepcopy한다. 승인 config는 프로필 ai.model/tier/provider/lock 및 용량 제약을 seal하고 role_profile_refs에 현행 판본을 둔다. 기존 등록 판본은 고정 실행/과제에 남으며 selection은 default 현행 역할 참조, explicit profile의 역할 하한, 작업 allowlist를 사용한다. 이는 새 사용자 모델 선택을 자의 승인하는 경로가 아니다.',
     'consumption':'selection은 난이도/중요도와 역할 하한의 큰 tier를 사용하며 미평가 연구 생산자는 high로 올린다. explicit old profile은 그 모델을 유지하되 tier 하한/작업 allowlist를 지킨다. classify_run은 profile에서 동결된 claude_only_assigned_model이 true이고 reported_models 중 cli_model과 다른 이름이 있는 경우에만 model_policy로 반환한다. _receive_call/record_model_policy_violation은 assigned/reported/eid와 원결과를 보존하고 후속을 pause한다.',
     'limits':'공급자가 모델을 보고하지 않은 경우 다른 모델 사용을 입증하거나 거부하지 않는다. true가 아닌 lock에서 불일치를 일괄 반려하는 약속도 없다. 이 분류를 모델 기본값 키나 성공한 제출의 수학적 수락으로 해석하지 않는다. 007의 real worker+외부 CLI 대역 경로와 정확 저장/추가 호출0 단언이 한정 근거이고 현재 모델 실제 공급자 실호출 증거는 아니다.',
     'judgment':'두 문장을 구별해 유지한다. 역할 기본값, snapshot 소유와 불일치 분류의 뜻은 현재 consumer와 일치한다. model_call 판본 변화와 fixture 변화 때문에 B129/007 전판본 green은 재사용하지 않는다.',
     'next_action':'기존 profile selection과 worker mismatch의 정확 test ID/단언을 보존하여 최종 통합 판본에 연결한다. module 이름을 schema 설정 필드로 추가하지 않는다.'},
    {'name':'external_policy','classification':'유지',
     'meaning':'사용자 초기화 채택의 disabled/explicit_grants 정책이며 lifecycle.adoption.external_policy에 저장된다. explicit_grants는 전역 HTTP 허가가 아니라 실제 효과별 현재 HTTP grant를 검사할 수 있게 하는 상위 선택이다.',
     'production_storage_authority':'initialization decision의 사용자 출처 검사, 허용값 검사, adoption/source_refs/decisions.change 저장을 거친다. 예제188 disabled는 HTTP 요청을 만들거나 외부 grant를 발급하지 않는다. local 초기화/연구 grant를 HTTP 권한으로 바꾸지 않는다.',
     'consumption':'_external_control.prepare와 active dispatch gate가 explicit_grants를 요구한다. 준비에서 실제 HTTP grant/actor/profile/요청 지문을 검사하고 송신 시 다시 현재 grant/만료·철회·origin/method/path/exclusion·target/purpose/subject/actor 및 학술 조건을 확인한다. should_stop와 송신 직전 ledger publication/inbox 처리도 유지한다. unknown의 원격 결과를 재송신 허가로 바꾸지 않는다.',
     'limits':'현재 문장 external_policy는 실제 허가에 맞춘다는 설명과 예제의 disabled는 일치한다. 실제 transport/외부 공급자 호출은 이번에 실행하지 않았다. 기존 unit/sim의 외부 HTTP 포트 대역 단언과 과거 exact row의 관측을 구별한다. 정책 값만 있으면 activation의 외부 조건은 채워져도 실제 HTTP grant/효과 성공은 별도다.',
     'judgment':'초기화182/188의 지정 의미는 유지 후보다. 사용자 권한/실제 송신/학술 전체 완료로 확대하지 않는다.',
     'next_action':'disabled 반려/HTTP grant 없음·다른 actor 반려/라우팅 범위·송신 직전 철회의 기존 정확 단언을 후속에 유지한다. 새 외부 정책 설계는 불필요하다.'},
    {'name':'adopt_default_review_policy','classification':'문구 교정',
     'meaning':'사용자 initialization adopt 요청의 Boolean 동작 선택이며 저장 정책 필드 이름이 아니다. true(명시 review_policy 없음)는 현재 config.reviewers/review_rounds로 configured default를 새로 만들고 instance.review_policy와 adoption.review_policy_sha256을 저장한다. 명시 review_policy가 함께 있으면 그 객체를 검사·채택하는 분기가 우선한다.',
     'production_storage_authority':'control_contracts.DECISION의 Boolean, _apply_extended_control의 사용자 origin, _initialization_control의 active 계약 교체 반려를 거친다. build_review_policy는 review-policy-v5-default, required_perspectives=[],minimum_initial_slots=reviewers,judges3,round_limit=review_rounds,limit=reviewers+review_rounds*(reviewers+4),overflow=unresolved를 만든다. 현재 결과를 exact_content_hash로 결박하며 사용자 source/change를 저장한다.',
     'consumption':'activation_requirements는 instance.review_policy를 검사하고 현재 객체의 hash가 adoption.review_policy_sha256와 같은지 비교한다. config hash의 currentness, profile evidence와 초기/연구 grant, 독립 intent/trust/recovery는 별도 필수 조건이다. probe는 역할별 능력 관측이지 기본 review policy 생성/채택 허가가 아니다.',
     'limits':'초기화182의 이미 채택한 기본 검토 방침을 정확한 현재 판본으로 결박한다는 말은 기존 객체 재사용이나 사전 채택이 선행조건인 것으로 읽힌다. 실제 initialize_state에는 review_policy가 없고 true 분기는 기존 객체를 읽지 않고 생성한다. 본 code path는 소스 확인이며 이번 실행 반례가 아니다. 현행 config로 기본값을 생성해 채택하는 동작을 유지하고 문구를 고친다.',
     'judgment':'문구 교정 후보. proposed text: adopt_default_review_policy=true는 현재 설정의 reviewers·review_rounds로 기본 검토 방침을 생성·채택하고, 그 실제 정책의 내용 해시를 결박한다. 이미 별도 방침을 승인했다면 review_policy에 그 원문을 지정한다. 현재 예제189와 사용자 승인 범위는 그대로다.',
     'next_action':'references/초기화-운전.md182의 해당 한 문장과 공식 미러만 통합 work에서 교정한다. InitialAdoptionTests에 reviewers=3/review_rounds=2인 현재 config와 기존 review_policy absent/다른 객체 조건으로 true 채택을 실행하여 독립 기대 minimum3/round2/limit17·3judge/empty perspectives/unresolved 및 저장 hash를 확인한다. 설정 변경 후 옛 config_sha256 반려와 hash 교란 활성화 missing은 기존 검사를 유지한다. 제품 동작이나 권한을 변경하지 않는다.'},
]

def main():
    save('excerpt-requests.json',EXCERPTS)
    bindings=test_coordinates()
    save('test-bindings.json',bindings)
    save('historical-execution.json',historical_rows(bindings))
    history_review()
    population=json.loads((OUT/'population.json').read_text(encoding='utf-8'))
    for decision in DECISIONS:
        decision['occurrences']=[r for r in population['current_name_line_pairs_in_documents'] if r['name']==decision['name']]
        decision['test_bindings']=bindings[decision['name']]
        decision['source_edition']='run:phases/026/tasks/policy-semantics/evidence/source-start.json'
        decision['evidence']=[E+'source-excerpts.json',E+'historical-execution.json',E+'population.json']
    save('policy-decisions.json',DECISIONS)
    req=json.loads(resolve('run:phases/001/tasks/closure-map/evidence/requirement-state.json').read_text(encoding='utf-8-sig'))
    selected=[r for r in req['rows'] if r['id'] in ['13-C','6-A','K-19','K-51','K-65','C-20']]
    save('requirement-slices.json',{'rows':selected,'scope':'Traceability input only; these whole requirements are not closed by this task.'})
    print(json.dumps({'decisions':len(DECISIONS),'test_ids':len({r['id'] for rs in bindings.values() for r in rs}),
                      'occurrences':population['current_name_line_pair_count'],'product_imports':0,'product_writes':0},ensure_ascii=False))

if __name__=='__main__':
    main()
