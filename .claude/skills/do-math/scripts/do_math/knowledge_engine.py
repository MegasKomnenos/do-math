"""Engine integration for user knowledge controls and the currentness of goal judgments that rely on knowledge."""
from __future__ import annotations

from .knowledge import revise_knowledge, invalidate_knowledge, validate_basis, assess_use
from .input_basis import sources_current
from .initialization import governance_working_view

class KnowledgeEngineMixin:
    def _invalidate_goal_currentness(self):
        view = governance_working_view(self.instance) if self.instance.get('governance') else self.instance
        judgments = self.instance.get('goal_judgments', [])
        basis = self.instance.get('goal_assessment_basis', judgments[-1].get('basis') if judgments else None)
        current = [j for j in judgments if j.get('basis') == basis] if basis is not None else judgments[-1:]
        for judgment in current:
            invalid_dependencies = [record_id for record_id in judgment.get('dependencies', [])
                if record_id in self.instance.get('knowledge', {}) and not assess_use(self.instance['knowledge'][record_id], self.instance)['valid']]
            if (judgment.get('record_basis') and not validate_basis(judgment['record_basis'], self.instance, self.runtime)['valid']) or (judgment.get('source_basis') and not sources_current(judgment['source_basis'], self.instance)) or (
                    judgment.get('goal_revision', view.get('goal_revision')) != view.get('goal_revision')) or (
                    judgment.get('policy_revision', view.get('policy_revision')) != view.get('policy_revision')) or invalid_dependencies:
                judgment['current'] = False
                judgment['invalidated_reason'] = ('A mathematical dependency is no longer usable: ' + ', '.join(invalid_dependencies)
                                                   if invalid_dependencies else 'The actual judgment basis changed')
        stale = [j for j in current if j.get('current') is False]
        if stale and self.instance.get('goal_status') == 'mathematically_solved':
            self.instance['goal_status'] = 'unsolved'
            if self.runtime.get('status') == 'completed': self.runtime['status'] = 'ready'
            self._lifecycle_event('goal_basis_invalidated', judgment_ids=[j.get('id', j.get('execution_id')) for j in stale])
            self._enqueue('research_plan', reason='Previously used goal evidence is no longer current')

    def _knowledge_control(self, config, source_ref):
        operation, knowledge_id = config.get('operation'), config.get('id')
        if operation not in {'revise', 'invalidate'}:
            raise ValueError('knowledge operation must be revise or invalidate')
        reason = config.get('reason', '')
        item = self.instance['knowledge'].get(knowledge_id)
        if item is None: raise ValueError('knowledge item does not exist')
        previous_cycle = item.get('review_cycle_id')
        if previous_cycle in self.runtime['review_cycles']:
            cycle = self.runtime['review_cycles'][previous_cycle]
            if cycle['status'] == 'working':
                cycle.update(status='unresolved', decision='unresolved', phase='ended')
                cycle.setdefault('history', []).append({'event': 'user_knowledge_change', 'source_ref': source_ref, 'reason': reason})
                for investigation in cycle.get('research', {}).values():
                    if investigation.get('status') == 'pending':
                        investigation.update(status='cancelled', cancellation={'source_ref': source_ref, 'reason': reason})
                cycle['deferred_actions'] = {}
        for execution in self.runtime['executions'].values():
            if execution.get('status') != 'ended' and execution.get('action', {}).get('target') == knowledge_id:
                execution['stop_requested'] = 'knowledge_' + str(operation)
        if operation == 'revise':
            self.instance, self.runtime = revise_knowledge(self.instance, self.runtime, knowledge_id,
                config.get('changes', {}), reason=reason, actor_ref=source_ref,
                declared_impact=config.get('declared_impact'), independent_confirmation=config.get('independent_confirmation'))
        else:
            self.instance, self.runtime = invalidate_knowledge(self.instance, self.runtime, knowledge_id,
                reason=reason, actor_ref=source_ref, declared_impact=config.get('declared_impact'),
                independent_confirmation=config.get('independent_confirmation'))
        self._lifecycle_event('knowledge_' + operation, target=knowledge_id, source_ref=source_ref, reason=reason)
        self._enqueue('research_plan', reason=reason, knowledge_id=knowledge_id, source_ref=source_ref)
