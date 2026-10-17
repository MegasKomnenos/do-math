"""Revalidation of a native model execution's captured final against its published start and input (layer 2).

The engine accepts a native final only through ``verified_native_final``: the
collection must have passed the local termination barrier, and the stream must
select exactly the captured final.
"""
from __future__ import annotations

import base64

from .claude_stream import parse_response as _parse_claude
from .codex_stream import parse_response as _parse_codex
from .provider_final import final_mismatch, request_provider
from .session_slots import local_termination_confirmed
from .values import strict_json_loads

# Each provider's stream parse, the same function its collector uses.
PARSERS = {"codex": _parse_codex, "claude": _parse_claude}


def verified_native_final(result, execution, context):
    """Revalidate captured native evidence against the published start and input.

    This consumes adapter evidence after the real local termination barrier.
    A completed runner status or an arbitrary final file is not sufficient.
    """
    # Central reception can fail after a normal provider return. The original
    # status records that boundary; all provider evidence is still checked below.
    central_failure = (result.get('status') == 'failed'
        and result.get('error_kind') == 'execution_failure'
        and result.get('collection') == 'provider_evidence_only'
        and result.get('provider_result_status') == 'completed')
    if result.get('status') != 'completed' and not central_failure:
        raise ValueError('native execution did not complete normally')
    try:
        evidence = result['execution']; collected = evidence['collect']; started = evidence['started']
        barrier = collected['termination_barrier']
        if (collected['result'] != 'output_collected' or collected.get('reasons')
                or collected.get('stop_receipts') or barrier.get('confirmed') is not True
                or barrier.get('root_signaled') is not True or barrier.get('active_processes') != 0
                or barrier.get('process_ids') not in ([], ())
                or not local_termination_confirmed(execution)):
            raise ValueError('native collection or local termination is incomplete')
        def raw_artifact(name):
            # Collection hashed these bytes once; its recorded digests are compared, not recomputed.
            artifact = collected[name]; raw = artifact['raw']
            if isinstance(raw, dict):
                if raw['sha256'] != artifact['sha256']:
                    raise ValueError('serialized native artifact differs')
                raw = base64.b64decode(raw['base64'], validate=True)
            if (not isinstance(raw, bytes) or artifact.get('present') is not True
                    or not isinstance(artifact['sha256'], str) or artifact['bytes'] != len(raw)):
                raise ValueError('native artifact hash or size differs: ' + name)
            return raw
        request_raw = raw_artifact('source_request'); raw_artifact('source_prompt')
        stdout = raw_artifact('stdout'); final = raw_artifact('final')
        request = strict_json_loads(request_raw); status = collected['worker_status']
        request_hash = collected['source_request']['sha256']; prompt_hash = collected['source_prompt']['sha256']
        published = execution.get('capacity', {}).get('process') or {}
        if (started.get('request_sha256') != request_hash
                or published.get('request_sha256') != request_hash
                or prompt_hash != execution['input_manifest']['prompt']['sha256']
                or status.get('state') != 'exited' or status.get('cli_exit_code') != 0
                or status.get('request_sha256') != request_hash or status.get('stdin_sha256') != prompt_hash
                or status.get('schema_sha256') is not None or 'output_schema_path' in request):
            raise ValueError('native request, input, or worker completion differs from the published execution')
        for key, expected in [('execution_id', execution['id']), ('profile_ref', execution['execution_profile_ref'])]:
            if any(row.get(key) != expected for row in (request, status, collected, started)):
                raise ValueError('native execution/profile binding differs')
        binding = request['control_binding']
        if (context.get('execution_id') != execution['id'] or binding.get('execution_id') != execution['id']
                or binding.get('grant_id') != execution.get('grant_id')
                or context.get('action', {}).get('grant_id') != execution.get('grant_id')):
            raise ValueError('native input or authority binding differs')
        def exact_integer(value):
            if type(value) is int and value > 0:
                return value
            if isinstance(value, str) and value.isascii() and value.isdecimal() and int(value) > 0:
                return int(value)
            raise ValueError('native process identity requires an exact positive integer')
        for key in ('pid', 'creation_filetime'):
            expected = exact_integer(published.get(key))
            if any(exact_integer(row.get(key)) != expected for row in (started, collected['process_identity'])):
                raise ValueError('native collected/start identity differs from its published process')
        if not started.get('job_name') or published.get('job_name') != started['job_name']:
            raise ValueError('native Job identity differs from its published process')
        parsed = PARSERS[request_provider(request)](stdout, request)
        if (not parsed.get('parse_complete') or not parsed.get('turn_completed') or parsed.get('turn_failed')
                or final_mismatch(parsed, final)):
            raise ValueError('native stream does not establish this exact completed final')
        return final
    except (KeyError, TypeError, OSError, IndexError) as error:
        raise ValueError('native completion evidence is missing or malformed') from error
