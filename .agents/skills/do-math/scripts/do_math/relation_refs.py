"""Direct authored relation edges, separate from each consumer's traversal policy."""


def relation_evidence_references(relation):
    return {ref for key in ('evidence_refs', 'formal_result_refs', 'assessment_refs')
            if isinstance(relation.get(key), list) for ref in relation[key] if isinstance(ref, str)}


def relation_endpoints(relation):
    return {relation[key] for key in ('source', 'target') if isinstance(relation.get(key), str)}


def relation_references(relation):
    # A relation_claim uses the same endpoint representation. History, prose,
    # origin_refs and arbitrary nested objects never become current edges here.
    return relation_endpoints(relation) | relation_evidence_references(relation)
