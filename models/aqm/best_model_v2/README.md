---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:17561
- loss:BinaryCrossEntropyLoss
base_model: cross-encoder/ms-marco-MiniLM-L12-v2
pipeline_tag: text-ranking
library_name: sentence-transformers
---

# CrossEncoder based on cross-encoder/ms-marco-MiniLM-L12-v2

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model finetuned from [cross-encoder/ms-marco-MiniLM-L12-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L12-v2) using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
- **Base model:** [cross-encoder/ms-marco-MiniLM-L12-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L12-v2) <!-- at revision 7b0235231ca2674cb8ca8f022859a6eba2b1c968 -->
- **Maximum Sequence Length:** 512 tokens
- **Number of Output Labels:** 1 label
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Documentation:** [Cross Encoder Documentation](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Cross Encoders on Hugging Face](https://huggingface.co/models?library=sentence-transformers&other=cross-encoder)

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import CrossEncoder

# Download from the 🤗 Hub
model = CrossEncoder("cross_encoder_model_id")
# Get scores for pairs of texts
pairs = [
    ['Ya, I think you misunderstood them. Gaming is appreciating art if you define that game as art. Also the word art has multiple definitions. "Art" can also be synonymous with "Skill" and some gamers are incredibly skilled. Although I think you can definitely make art in some games. [Minecraft]( being a [really]( good [example]( Sitting in front of the Mona Lisa won\'t make you a painter, but writing critiques of paintings would make you a writer. Gaming is a bit different than watching a movie or looking at a painting because you actually have to do something. That something sometimes involves skill, intelligence, and creativity. Really this all comes down to your definition of "Art". Please define what you mean by "Artistic Expression" and I can try to give you a more specific argument.', 'Does reading poetry count as a form of artistic expression? Does collecting paintings and hanging them in your home count? Does singing your favorite song count? If so, then playing a video game also counts. You stated in your "edit" that video games are art, but you do not consider gamers to be "artists". I think you have to admit that gaming is artistic expression though, if you also believe that enjoying the art forms I mentioned above counts as expression.'],
    ["The Indian economy is galloping at a breakneck speed and might even reach double-digit growth by 2013, feel Finance Minister Pranab Mukherjee and Commerce Minister Anand Sharma. Many economists agree that the demographic dividend that India enjoys could see the country sustain its high growth rate for a long time to come. <br/> The India growth story is indeed enviable. Despite being plagued by myriad problems, India has emerged stronger and more resilient to any global crises so far. <br/> India is expected to be the world's fastest growing economy by 2018, according to Economist Intelligence Unit, a research arm of the Economist magazine.", 'I am an American, and I am ashamed to admit "Merica is rich due to slavery. India never had slavery and used to be rich until the British came and took everything away. We were left in a bad state, but started developing quickly. India is much more competitive in education than America and soon when everyone has education (which will happen in our lifetime) India will excel. <br/> India has the potential.'],
    ['well, the people who watch porn, <br/> i guess thats ok, its NORMAL. <br/> but the people who are <br/> IN the porn, that is not normal.. <br/> i read it in a abnormal psychology book, <br/> that means they have a disorder', 'Porn is Wrong. <br/> mainly because they are Not <br/> Doing it Right. <br/> it should be Hi Def. <br/> in three years, it will <br/> be in 3-D.'],
    ['You said it\'s not covered under insurance. Psychological therapies *are* covered by decent insurance providers with affordable visit copays, $10 with Blue Cross. Sure, urging a person to seek therapy can be unhelpful or obnoxious if done inappropriately. But there are some people who really benefit from evaluation and/or counseling, and often those people need some prodding. I have anxiety and one visit with a therapist taught me how to self-administer biofeedback (which literally is just holding a thermometer in your hand) and how to use relaxation techniques to decrease anxiety spells. You can measure your peripheral temperature increase, indicating a reduction in systemic anxiety as you do the techniques. Anyway, I had to be told to get therapy before I went. It helps coming from somebody familiar with the condition. The point here is: Advising somebody to get therapy is not the "*most useless*" advice to be given; it\'s very useful for a specific subset of people at a specific time in their life. Obviously that advice should be given tactfully.', "A therapist is not a random person who takes your hard-earned money to dispense advice you can find on the internet. A therapist is a trained professional who takes a significant amount of time and effort to understand you *on an intimate level* and give you advice that is based on experience and *specific* to your situation. A therapist is someone whom I could've gone to 4 or 6 years ago, and they would've talked me through getting to the point where I am now, but I wouldn't have wasted 4 to 6 years getting lost in detours and wallowing in self-pity. Ugh. I wish I'd understood sooner that the stigma around mental health is bullshit and that all of us need somebody to talk to about our mental anxieties, even if it's just once a year, as a profilactic check up on our psychological health. This is why I tell redditors to get therapy."],
    ['No I would not because i would have taken a vow say to stick by them in sickness and health. They might be sick in the head but she would be my wife. If anything id be trying to find a way to keep her from getting caught.', "No I would not turn them in, because it would be to weird for me to turn them in to the police. I would probably wouldn't tell anybody. I would hope that the police catch them but I would not say anything. I would tell them to turn their self in."],
]
scores = model.predict(pairs)
print(scores.shape)
# (5,)

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'Ya, I think you misunderstood them. Gaming is appreciating art if you define that game as art. Also the word art has multiple definitions. "Art" can also be synonymous with "Skill" and some gamers are incredibly skilled. Although I think you can definitely make art in some games. [Minecraft]( being a [really]( good [example]( Sitting in front of the Mona Lisa won\'t make you a painter, but writing critiques of paintings would make you a writer. Gaming is a bit different than watching a movie or looking at a painting because you actually have to do something. That something sometimes involves skill, intelligence, and creativity. Really this all comes down to your definition of "Art". Please define what you mean by "Artistic Expression" and I can try to give you a more specific argument.',
    [
        'Does reading poetry count as a form of artistic expression? Does collecting paintings and hanging them in your home count? Does singing your favorite song count? If so, then playing a video game also counts. You stated in your "edit" that video games are art, but you do not consider gamers to be "artists". I think you have to admit that gaming is artistic expression though, if you also believe that enjoying the art forms I mentioned above counts as expression.',
        'I am an American, and I am ashamed to admit "Merica is rich due to slavery. India never had slavery and used to be rich until the British came and took everything away. We were left in a bad state, but started developing quickly. India is much more competitive in education than America and soon when everyone has education (which will happen in our lifetime) India will excel. <br/> India has the potential.',
        'Porn is Wrong. <br/> mainly because they are Not <br/> Doing it Right. <br/> it should be Hi Def. <br/> in three years, it will <br/> be in 3-D.',
        "A therapist is not a random person who takes your hard-earned money to dispense advice you can find on the internet. A therapist is a trained professional who takes a significant amount of time and effort to understand you *on an intimate level* and give you advice that is based on experience and *specific* to your situation. A therapist is someone whom I could've gone to 4 or 6 years ago, and they would've talked me through getting to the point where I am now, but I wouldn't have wasted 4 to 6 years getting lost in detours and wallowing in self-pity. Ugh. I wish I'd understood sooner that the stigma around mental health is bullshit and that all of us need somebody to talk to about our mental anxieties, even if it's just once a year, as a profilactic check up on our psychological health. This is why I tell redditors to get therapy.",
        "No I would not turn them in, because it would be to weird for me to turn them in to the police. I would probably wouldn't tell anybody. I would hope that the police catch them but I would not say anything. I would tell them to turn their self in.",
    ]
)
# [{'corpus_id': ..., 'score': ...}, {'corpus_id': ..., 'score': ...}, ...]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 17,561 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                                        | sentence_1                                                                                        | label                                                          |
  |:--------|:--------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                                            | string                                                                                            | float                                                          |
  | details | <ul><li>min: 46 characters</li><li>mean: 694.86 characters</li><li>max: 2290 characters</li></ul> | <ul><li>min: 34 characters</li><li>mean: 712.81 characters</li><li>max: 2215 characters</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.48</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | label            |
  |:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Ya, I think you misunderstood them. Gaming is appreciating art if you define that game as art. Also the word art has multiple definitions. "Art" can also be synonymous with "Skill" and some gamers are incredibly skilled. Although I think you can definitely make art in some games. [Minecraft]( being a [really]( good [example]( Sitting in front of the Mona Lisa won't make you a painter, but writing critiques of paintings would make you a writer. Gaming is a bit different than watching a movie or looking at a painting because you actually have to do something. That something sometimes involves skill, intelligence, and creativity. Really this all comes down to your definition of "Art". Please define what you mean by "Artistic Expression" and I can try to give you a more specific argument.</code> | <code>Does reading poetry count as a form of artistic expression? Does collecting paintings and hanging them in your home count? Does singing your favorite song count? If so, then playing a video game also counts. You stated in your "edit" that video games are art, but you do not consider gamers to be "artists". I think you have to admit that gaming is artistic expression though, if you also believe that enjoying the art forms I mentioned above counts as expression.</code> | <code>1.0</code> |
  | <code>The Indian economy is galloping at a breakneck speed and might even reach double-digit growth by 2013, feel Finance Minister Pranab Mukherjee and Commerce Minister Anand Sharma. Many economists agree that the demographic dividend that India enjoys could see the country sustain its high growth rate for a long time to come. <br/> The India growth story is indeed enviable. Despite being plagued by myriad problems, India has emerged stronger and more resilient to any global crises so far. <br/> India is expected to be the world's fastest growing economy by 2018, according to Economist Intelligence Unit, a research arm of the Economist magazine.</code>                                                                                                                                                    | <code>I am an American, and I am ashamed to admit "Merica is rich due to slavery. India never had slavery and used to be rich until the British came and took everything away. We were left in a bad state, but started developing quickly. India is much more competitive in education than America and soon when everyone has education (which will happen in our lifetime) India will excel. <br/> India has the potential.</code>                                                         | <code>1.0</code> |
  | <code>well, the people who watch porn, <br/> i guess thats ok, its NORMAL. <br/> but the people who are <br/> IN the porn, that is not normal.. <br/> i read it in a abnormal psychology book, <br/> that means they have a disorder</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | <code>Porn is Wrong. <br/> mainly because they are Not <br/> Doing it Right. <br/> it should be Hi Def. <br/> in three years, it will <br/> be in 3-D.</code>                                                                                                                                                                                                                                                                                                                                 | <code>1.0</code> |
* Loss: [<code>BinaryCrossEntropyLoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#binarycrossentropyloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity",
      "pos_weight": null
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `overwrite_output_dir`: False
- `do_predict`: False
- `eval_strategy`: no
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `per_gpu_train_batch_size`: None
- `per_gpu_eval_batch_size`: None
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 3
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: {}
- `warmup_ratio`: 0.0
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `save_safetensors`: True
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `no_cuda`: False
- `use_cpu`: False
- `use_mps_device`: False
- `seed`: 42
- `data_seed`: None
- `jit_mode_eval`: False
- `bf16`: False
- `fp16`: False
- `fp16_opt_level`: O1
- `half_precision_backend`: auto
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: 0
- `ddp_backend`: None
- `tpu_num_cores`: None
- `tpu_metrics_debug`: False
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `past_index`: -1
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_min_num_params`: 0
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `fsdp_transformer_layer_cls_to_wrap`: None
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `adafactor`: False
- `group_by_length`: False
- `length_column_name`: length
- `project`: huggingface
- `trackio_space_id`: trackio
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `use_legacy_prediction_loop`: False
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `hub_revision`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_inputs_for_metrics`: False
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `fp16_backend`: auto
- `push_to_hub_model_id`: None
- `push_to_hub_organization`: None
- `mp_parameters`: 
- `auto_find_batch_size`: False
- `full_determinism`: False
- `torchdynamo`: None
- `ray_scope`: last
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_tokens_per_second`: False
- `include_num_input_tokens_seen`: no
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: True
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss |
|:------:|:----:|:-------------:|
| 0.4554 | 500  | 0.7274        |
| 0.9107 | 1000 | 0.5191        |
| 1.3661 | 1500 | 0.4722        |
| 1.8215 | 2000 | 0.446         |
| 2.2769 | 2500 | 0.3994        |
| 2.7322 | 3000 | 0.3818        |


### Framework Versions
- Python: 3.12.12
- Sentence Transformers: 5.2.0
- Transformers: 4.57.3
- PyTorch: 2.9.0+cu126
- Accelerate: 1.12.0
- Datasets: 4.0.0
- Tokenizers: 0.22.1

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->