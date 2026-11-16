# H12 검산 7: 부록 D 5A 항목 자료 줄 경로 존재 확인과 요약값 읽기
import glob, os, json, sys
R = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
rec_paths = """rc9aee43*/evidence/producer/code/positive_columns.py rc9aee43*/evidence/producer/output/certificates-121-160.json
rc9aee43*/evidence/peer/code/extend_columns.py rc9aee43*/evidence/peer/code/rowwise_left.py rc9aee43*/evidence/peer/code/indep_lastcar.py
rc9aee43*/evidence/peer/output/ext-161-360.json rc9aee43*/evidence/peer/output/ext-361-442.json rc9aee43*/evidence/peer/output/ext-443-500.json
rc9aee43*/evidence/peer/output/rw-10000-a.json rc9aee43*/evidence/peer/output/rw-10000-g.json rc9aee43*/evidence/peer/output/summary-all.json
rc9aee43*/review/evidence/rerun-k500.json rc9aee43*/review/evidence/rev-col-k150.json rc9aee43*/review/evidence/rev-col-k200.json
r15df76b*/evidence/producer/code/leftcert.c r15df76b*/evidence/producer/code/leftcert_build1.c r15df76b*/evidence/producer/code/leftcert_build2.c
r15df76b*/evidence/producer/run/left20000_k501-2875.tsv r15df76b*/evidence/producer/run/left20000_k2876-5250.tsv r15df76b*/evidence/producer/run/left20000_k5251-7625.tsv r15df76b*/evidence/producer/run/left20000_k7626-9999.tsv
r15df76b*/evidence/producer/run2/small20000_k2-250.tsv r15df76b*/evidence/producer/run2/small20000_k251-500.tsv r15df76b*/evidence/producer/run2/center20000_k5001-8000_center.tsv r15df76b*/evidence/producer/run2/center20000_k8001-10000_center.tsv
r15df76b*/evidence/peer/code/pcertv.c r15df76b*/evidence/peer/run/pv_k2-2501.tsv r15df76b*/evidence/peer/run/pv_k2502-5001.tsv r15df76b*/evidence/peer/run/pv_k5002-7501.tsv r15df76b*/evidence/peer/run/pv_k7502-10000.tsv
r15df76b*/evidence/peer/checks/compare_runs.json r15df76b*/evidence/peer/checks/coverage_producer.json
r19de912*/evidence/peer/cert/qr_cert2.c r19de912*/evidence/peer/cert/gen_s.py r19de912*/evidence/peer/cert/v2run20000-rows.tsv r19de912*/evidence/peer/cert/v2run20000-summary.json r19de912*/evidence/peer/cert/v2run20000.log r19de912*/evidence/peer/cert/class-hashes.txt
r19de912*/evidence/producer/certify_right_half.py r19de912*/evidence/producer/right-half-certificate-2000.json r19de912*/evidence/peer/checks/producer-rerun-summary.json r19de912*/review/evidence/peer-rerun
r19de912*/evidence/peer/checks/mode_offset.py r19de912*/evidence/peer/checks/mode_offset.json
r6373c70*/evidence/peer/code/exact_rows.py r6373c70*/evidence/peer/output/exact-rows-300.json r6373c70*/review/evidence/code/my_exact_rows.py
r59c82d7*/evidence/code/qrcert.c r59c82d7*/evidence/code/make_tables.py r59c82d7*/evidence/code/bor.bin r59c82d7*/evidence/code/h.bin r59c82d7*/evidence/code/tables_manifest.json r59c82d7*/evidence/code/postprocess_rows.py r59c82d7*/evidence/code/merge_chunks.py
r59c82d7*/evidence/runs/ext50000_summary.json r59c82d7*/evidence/runs/ext50000_rows.tsv r59c82d7*/evidence/runs/ext50000_post.json r59c82d7*/evidence/runs/e50_1_summary.json r59c82d7*/evidence/runs/e50_6_summary.json
r59c82d7*/evidence/runs/full20000_summary.json r59c82d7*/evidence/runs/full20000_rows.tsv r59c82d7*/evidence/runs/full20000_compare_published.txt r59c82d7*/evidence/runs/t60_validate.json r59c82d7*/evidence/exact_check.json
r708d99c*/evidence/peer/cert_newton_summary.json r708d99c*/evidence/peer/cert_newton.py r708d99c*/evidence/peer/peer_core.py r708d99c*/evidence/peer/recheck_certificate.py r708d99c*/evidence/peer/recheck_certificate_out.json
r708d99c*/evidence/peer/verify_P_poly.py r708d99c*/evidence/peer/verify_reduction.py r708d99c*/evidence/producer/work/renewal_poly_results.json
r708d99c*/review/checks/rv_cert.py r708d99c*/review/checks/rv_core.py r708d99c*/review/checks/rv_cert_newton_A.json r708d99c*/review/checks/rv_cert_newton_B.json
r0dc57fa*/evidence/peer/code/cert_tail_alpha1.py r0dc57fa*/evidence/peer/data/cert_tail_alpha1_171_9999.json r0dc57fa*/evidence/peer/code/tail_alpha_scan.py r0dc57fa*/evidence/peer/data/tail_alpha_scan.json
r0dc57fa*/evidence/peer/code/S_float.py r0dc57fa*/evidence/peer/code/core_exact.py r0dc57fa*/review/evidence/t1_check.py r0dc57fa*/review/evidence/t1_check_out.json
r690be93*/evidence/producer/certify_entry.py r690be93*/evidence/producer/certify_concavity.py r690be93*/evidence/producer/published_algebra.py r690be93*/evidence/producer/entry-slope-certificate.json
r690be93*/evidence/producer/check_certificates.py r690be93*/evidence/producer/direct_checks.py r690be93*/evidence/producer/certificate-check.json r690be93*/evidence/producer/direct-checks.json
r690be93*/evidence/peer/reproduction r690be93*/evidence/peer/kernel_sample.py r690be93*/evidence/peer/kernel_sample r690be93*/evidence/peer/tsv_crosscheck_output.txt r690be93*/evidence/peer/window_check.json
r13b0b8f*/evidence/producer/output/critical-strip-certificate.json r13b0b8f*/evidence/producer/code/cert_critical_strip.py r13b0b8f*/evidence/producer/certificate-run.log r13b0b8f*/evidence/producer/verification.json
r13b0b8f*/evidence/peer/code/indep_cert.py r13b0b8f*/evidence/peer/code/indep_cert2.py r13b0b8f*/evidence/peer/code/indep_cert3.py r13b0b8f*/evidence/peer/code/laurent_sympy.py r13b0b8f*/evidence/peer/code/laurent_fast.py
r13b0b8f*/evidence/peer/indep_cert_A.json r13b0b8f*/evidence/peer/cert2_12_15.json r13b0b8f*/evidence/peer/cert3_15_18.json r13b0b8f*/evidence/peer/cert3_18_21_r2164.json r13b0b8f*/evidence/peer/cert3_21_24_r10000.json
r13b0b8f*/evidence/peer/cert3_18_21.json r13b0b8f*/evidence/peer/cert3_21_24.json r13b0b8f*/evidence/peer/indep_cert_ext15.json r13b0b8f*/evidence/peer/laurent_series_check.json r13b0b8f*/evidence/peer/gf_identity_check.json
r13b0b8f*/evidence/peer/J_identity_check.json r13b0b8f*/evidence/peer/tsv_crosscheck.json r13b0b8f*/evidence/peer/strip_sample.json r13b0b8f*/evidence/peer/reproduction/critical-strip-certificate-rerun.json r13b0b8f*/review/reruns/rerun_summary.json
ra4c01fc*/evidence/producer-code ra4c01fc*/evidence/certificates/cert2 ra4c01fc*/evidence/certificates/cert3 ra4c01fc*/evidence/peer/coverage_check.py ra4c01fc*/evidence/peer/coverage_check.out
ra4c01fc*/evidence/peer/exact_en_B.py ra4c01fc*/evidence/peer/contain_check.py ra4c01fc*/evidence/peer/h_exact.py ra4c01fc*/evidence/peer/check_h_contain.py ra4c01fc*/evidence/peer/h_contain.jsonl ra4c01fc*/evidence/peer/check_constants.py ra4c01fc*/evidence/peer/check_xi.py""".split()
miss = [p for p in rec_paths if not glob.glob(os.path.join(R, p))]
print("record paths checked:", len(rec_paths), "missing:", miss)
art = r"원고_자료\세션_재계산"
art_paths = """left_columns_k2_120/code/left_columns.py left_columns_k2_120/code/positive_columns.py left_columns_k2_120/code/radii.json left_columns_k2_120/code/summarize.py left_columns_k2_120/code/exact_check.py
left_columns_k2_120/summary.json left_columns_k2_120/results_k2_70.jsonl left_columns_k2_120/results_k71_120.jsonl left_columns_k2_120/exact_check.json
left_columns_k2_120/indep/indep_lastcar.py left_columns_k2_120/indep/indep_margin.py left_columns_k2_120/indep/indep_lastcar_out.json left_columns_k2_120/indep/indep_margin.json left_columns_k2_120/logs
witness_offset_iv/code/witness_offset_iv.py witness_offset_iv/code/summarize.py witness_offset_iv/witness_offset_iv.json witness_offset_iv/logs witness_offset_iv/README_run.md
c50_iv/c50iv.c c50_iv/build.bat c50_iv/make_tables_iv.py c50_iv/tables_iv_manifest.json c50_iv/postprocess_iv.py c50_iv/exact_small.py c50_iv/probe_undercount.py c50_iv/run_commands.txt
c50_iv/runs/c50_summary.json c50_iv/runs/c50_post.json c50_iv/runs/c50_rows.tsv c50_iv/runs/c20_summary.json c50_iv/runs/c20_post.json c50_iv/runs/c20_rows.tsv c50_iv/runs/t300_exact_check.txt
newton_r61_169/newton_cert.py newton_r61_169/newton_cert_out.txt
critical_window_rerun/rig_common.py critical_window_rerun/rig_H.py critical_window_rerun/rig_ray2.py critical_window_rerun/rig_ray4.py critical_window_rerun/rig_pipeline.py critical_window_rerun/rig_pipeline2.py
critical_window_rerun/rig_cert.py critical_window_rerun/rig_W.py critical_window_rerun/ivio.py critical_window_rerun/orig critical_window_rerun/boxes.py critical_window_rerun/common.py critical_window_rerun/rerun_boxes.py critical_window_rerun/recert_first.py
critical_window_rerun/cert/A00.json critical_window_rerun/cert/G13.json critical_window_rerun/cache critical_window_rerun/logs critical_window_rerun/check_fixes.py critical_window_rerun/check_fixes_out.txt
critical_window_rerun/summarize.py critical_window_rerun/summary_out.txt critical_window_rerun/verify_exact_cover.py critical_window_rerun/verify_exact_cover_out.txt
critical_window_rerun/launch_rerun.py critical_window_rerun/rerun_launches.txt critical_window_rerun/rerun_pids.txt critical_window_rerun/rerun_stdout_w0.txt critical_window_rerun/rerun_stdout_w1.txt
critical_window_rerun/postrun.py critical_window_rerun/postrun_log.txt critical_window_rerun/postrun_stdout.txt critical_window_rerun/_test_exact_grid.py""".split()
miss2 = [p for p in art_paths if not os.path.exists(os.path.join(art, p))]
print("article paths checked:", len(art_paths), "missing:", miss2)
print("probe files:", len(glob.glob(os.path.join(art, "c50_iv/runs/*probe*"))), " recert_first files:", len(glob.glob(os.path.join(art, "critical_window_rerun/cert/*_recert_first.json"))),
      " r19de912 copy:", os.path.exists(r"원고_자료\r19de912\evidence__peer__cert__v2run20000-rows.tsv"))

def show(p, n=1500, tail=False):
    try:
        s = open(p, encoding="utf-8", errors="replace").read()
        print("=== ", p, "\n", s[-n:] if tail else s[:n])
    except Exception as e:
        print("=== ", p, "ERR", e)

show(os.path.join(art, "left_columns_k2_120/summary.json"), 1800)
show(os.path.join(art, "left_columns_k2_120/exact_check.json"), 700)
show(os.path.join(art, "left_columns_k2_120/indep/indep_margin.json"), 900)
show(os.path.join(art, "witness_offset_iv/witness_offset_iv.json"), 1500)
show(os.path.join(art, "c50_iv/runs/c50_summary.json"), 1500)
show(os.path.join(art, "c50_iv/runs/c50_post.json"), 1200)
show(os.path.join(art, "c50_iv/runs/c20_post.json"), 1200)
show(os.path.join(art, "c50_iv/runs/t300_exact_check.txt"), 500)
show(os.path.join(art, "newton_r61_169/newton_cert_out.txt"), 700, tail=True)
show(os.path.join(art, "critical_window_rerun/summary_out.txt"), 2500)
show(os.path.join(art, "critical_window_rerun/verify_exact_cover_out.txt"), 900, tail=True)
