from typing import List, Optional

from transformers import PreTrainedTokenizer

from goodai.ltm.eval.qrecc import QreccMemEvaluator
from goodai.ltm.eval.strategy_qa import StrategyQAMemEvaluator


class AutoMemEvaluator:
    """
    Factory class for memory evaluators.
    """

    @staticmethod
    def create(name: str, tokenizer: PreTrainedTokenizer, top_ks: List[int], max_query_tokens: int,
               has_query_noise: bool, max_scenarios: Optional[int] = None):
        if max_scenarios is None:
            max_scenarios = 2000
        if name == 'qrecc':
            return QreccMemEvaluator(tokenizer, top_ks, max_query_tokens, has_query_noise,
                                     max_scenarios=max_scenarios)
        elif name == 'strategyqa':
            return StrategyQAMemEvaluator(tokenizer, top_ks, max_query_tokens, has_query_noise,
                                          max_scenarios=max_scenarios)
        else:
            raise ValueError(f'Dataset name "{name}" not recognized')