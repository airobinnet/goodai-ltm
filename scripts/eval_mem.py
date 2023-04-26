from dataclasses import dataclass
from typing import Optional, List

import torch
from transformers import AutoTokenizer, AutoModel

from goodai.ltm.embeddings.auto import AutoTextEmbeddingModel
from goodai.ltm.embeddings.default import DefaultEmbeddingModel
from goodai.ltm.eval.auto import AutoMemEvaluator
from goodai.ltm.reranking.auto import AutoTextMatchingModel
from goodai.ltm.mem.config import TextMemoryConfig
from goodai.ltm.mem.default import DefaultTextMemory
from goodai.ltm.mem.simple_vector_db import SimpleVectorDb


@dataclass
class EvalSpec:
    id: str
    embModelName: str
    matchingModelName: Optional[str] = None
    maxQueryTokens: int = 40
    hasQueryNoise: bool = True
    chunkCapacity: int = 24


if __name__ == '__main__':
    device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
    torch.manual_seed(1001)
    top_ks = [1, 3, 10]
    vector_db = SimpleVectorDb()
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-distilroberta-v1')
    datasets = ["qp_squad_v2"]  # "['msmarco']  # ['qrecc', 'strategyqa']
    eval_specs: List[EvalSpec] = [
        # EvalSpec('st/all-distilroberta-v1', 'st:sentence-transformers/all-distilroberta-v1', None,
        #          maxQueryTokens=40, hasQueryNoise=True),
        # EvalSpec('p4-distilroberta', 'p4-distilroberta', None,
        #          maxQueryTokens=40, hasQueryNoise=True),
        # EvalSpec('st/multi-qa-mpnet-base-cos-v1', 'st:sentence-transformers/multi-qa-mpnet-base-cos-v1',
        #          chunkCapacity=24),
        # EvalSpec('st/sentence-t5-large', 'st:sentence-transformers/sentence-t5-large', None,
        #          maxQueryTokens=40, hasQueryNoise=True),
        # EvalSpec('st/multi-qa-MiniLM-L6-cos-v1', 'st:sentence-transformers/multi-qa-MiniLM-L6-cos-v1', None,
        #          maxQueryTokens=40, hasQueryNoise=True),
        # EvalSpec('st/all-mpnet-base-v2', 'st:sentence-transformers/all-mpnet-base-v2', None,
        #          maxQueryTokens=40, hasQueryNoise=True),
        # EvalSpec('st/all-roberta-large-v1', 'st:sentence-transformers/all-roberta-large-v1', None,
        #          maxQueryTokens=40, hasQueryNoise=True),
        EvalSpec('experimental', 'p3-distilroberta'),
    ]
    ds_top_ks = [f'{ds_name}@{top_k}' for ds_name in datasets for top_k in top_ks]
    table_out = 'Model | ' + ' | '.join([ds_name for ds_name in ds_top_ks]) + '\n'
    table_out += '----- | ' + ' | '.join(['-' * len(ds_name) for ds_name in ds_top_ks]) + '\n'
    for spec in eval_specs:
        max_query_tokens = spec.maxQueryTokens
        has_query_noise = spec.hasQueryNoise

        emb_model = AutoTextEmbeddingModel.from_pretrained(spec.embModelName)

        mmn = spec.matchingModelName
        matching_model = None if mmn is None else AutoTextMatchingModel.from_pretrained(mmn)
        config = TextMemoryConfig()
        config.chunk_capacity = spec.chunkCapacity
        mem = DefaultTextMemory(vector_db, tokenizer, emb_model, matching_model,
                                device=device, config=config)
        table_out += spec.id + ' | '
        for dataset in datasets:
            print(f'Evaluation of {spec.id} on {dataset}...')
            evaluator = AutoMemEvaluator.create(dataset, tokenizer, top_ks, max_query_tokens, has_query_noise)
            results = evaluator.evaluate(mem)
            for top_k in top_ks:
                acc = results[f'ACC@{top_k}']
                acc_100 = f'{acc * 100:.02f}'
                table_out += acc_100 + ' | '
        table_out += '\n'
    print('Results:')
    print(table_out)
