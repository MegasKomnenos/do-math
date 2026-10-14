"""Check this fixed investigation's population, quoted coordinates, observed rows and preservation."""
import json
from analyze import OUT, NAMES, resolve, sha, save

def read(name):
    return json.loads((OUT/name).read_text(encoding='utf-8-sig'))

def main():
    population=read('population.json')
    decisions=read('policy-decisions.json')
    excerpts=read('source-excerpts.json')
    history=read('historical-execution.json')
    beginning,initial,end=read('source-start.json'),read('source-initial-probe.json'),read('source-end.json')
    assert beginning['sources']==initial['sources']==end['sources']
    assert beginning['inputs']==initial['inputs']==end['inputs']
    assert not beginning['mismatches_with_025'] and not end['mismatches_with_025']
    assert not end['changed_since_start'] and not end['changed_inputs_since_start']
    assert len(beginning['sources'])==2675
    assert sorted(row['name'] for row in decisions)==sorted(NAMES)
    assert population['001_policy_mentions_equal_024_historical']
    assert population['historical_count']==8 and population['current_name_line_pair_count']==12
    expected={(row['name'],row['document'],row['line']) for row in population['current_name_line_pairs_in_documents']}
    observed={(row['name'],r['document'],r['line']) for row in decisions for r in row['occurrences']}
    assert expected==observed
    assert {r['slice_id'] for row in decisions for r in row['occurrences']}=={'N01-020','N01-218','N01-230','N01-268','N01-273'}
    for row in decisions:
        assert row['classification'] in {'유지','문구 교정','시험 공백','제품 반례','외부 결정'}
        for key in ['meaning','production_storage_authority','consumption','limits','judgment','next_action']:
            assert row[key].strip()
        for occurrence in row['occurrences']:
            text=resolve(occurrence['document']).read_text(encoding='utf-8-sig').splitlines()
            assert text[occurrence['line']-1]==occurrence['text']
    for excerpt in excerpts:
        path=resolve(excerpt['reference'])
        assert sha(path)==excerpt['sha256']
        first,last=excerpt['lines']
        content=path.read_text(encoding='utf-8-sig').splitlines()
        assert '\n'.join(f'{i}: {content[i-1]}' for i in range(first,last+1))==excerpt['text']
    tests={r['id'] for decision in decisions for r in decision['test_bindings']}
    report_cache={}
    for row in history['rows']:
        ref=row['report']
        if ref not in report_cache:
            report_cache[ref]=json.loads(resolve(ref).read_text(encoding='utf-8-sig'))
        source=report_cache[ref]
        assert sha(resolve(ref))==row['report_sha256']
        assert row['row']['id'] in source['selected']
        found=[r for group in source['reports'] for r in group['rows'] if r['id']==row['row']['id']]
        assert found==[row['row']]
    assert tests=={r['row']['id'] for r in history['rows']}
    assert not history['new_execution'] and not history['whole_edition_reuse']
    review=read('history-review.json')
    assert all(review[0]['policy_functions_text_unchanged'].values())
    result={'source_count':len(beginning['sources']),'source_025_mismatches':end['mismatches_with_025'],
        'start_end_source_changes':end['changed_since_start'],'start_end_input_changes':end['changed_inputs_since_start'],
        'head_start':beginning['head'],'head_end':end['head'],
        'policies':len(decisions),'classifications':{r['name']:r['classification'] for r in decisions},
        'historical_occurrences':8,'current_name_line_pairs':12,'unique_current_document_lines':len({(r['document'],r['line']) for r in population['current_name_line_pairs_in_documents']}),
        'quoted_excerpts':len(excerpts),'exact_test_ids':len(tests),'historical_rows_checked':len(history['rows']),
        'changed_historical_test_rows':len([r for r in history['rows'] if not r['same_test_bytes']]),
        'whole_edition_reuse':False,'new_product_tests':0,'product_imports':0,'product_writes':0,
        'other_task_results_read':False,'remaining':'Other N01 names; L01 Q1/Q2 and original UTF-8 byte requirement/unmet status; symlink 1314; G4/G5/G6/G7 final-edition/G8 gates preserved.'}
    save('verification.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
