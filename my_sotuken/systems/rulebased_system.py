from cocoa.systems.rulebased_system import RulebasedSystem as BaseRulebasedSystem
from sessions.rulebased_session import RulebasedSession

class RulebasedSystem(BaseRulebasedSystem):
    def _new_session(self, agent, kb, config=None):
        ### change parts
        # restrict rulebased to seller.
        #
        # if kb.role == "buyer" -> AttributeError is occurred.
        # AttributeError: 'NoneType' object has no attribute 'config'
        # -> cocoa/web/main/backend.py, line 320
        #
        # However, system continue to select a scenario
        #   until a scenario - rulebased:seller is selected.
        # -> AttributeError is temporary problem.
        if kb.role == "seller":
            return RulebasedSession.get_session(agent, kb, self.lexicon, config, self.generator, self.manager)
        ###
