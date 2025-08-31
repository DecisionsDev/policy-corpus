# Policy corpus

This repository stands as a corpus of business policies to support research studies, academic courses and experiments.
It includes synthetic policies and a catalog of links of real public policies for various business domains.

## Motivations
LLMs are told to bring reasoning capabilities. While they are progressing for more than 2 years in this direction when performing specific tasks, question remains open when automating the decision making of business policies.
To go beyond intuition or any biais the idea is to measure any solution (LLM, generated code, human choice) to decide in comparison of a ground truth dataset.

For synthetic but real life inspired business policies what are the performances of:
- pure LLM decision making, given a single prompt, a request and the policy,
- a chain of thoughts involving a sequence or tree of generations
- a generated code thanks to an LLM
- other means involving other technics (optimization, genetic algorithms, tensor based logic inference, etc)

## Policy reference implementation
For a panel of business domain and use cases, this project proposes data and code to benchmark automated decisions with respect to a business policy expressed in plain text.
Each policy is described by:
- a plain text specifying the requirements, criteria and logic to deduce a decision from a given context.
- a Python code implementating the policy. This implementation has been validated by a human, based on an interpretation where policy brings ambiguity or misses information.
- a Data generator code. It invokes the automation code on synthetic inputs to produce outcomes
- a list of decision datasets. They are ready to use as a baseline to measure the performances of any machines (pure LLMs, code generated thanks to LLMs, others) that automate the decision making.  

## Policy list
The list of business policies captured in this corpus:
- [luggage compliance & pricing](luggage/luggage_policy.md)
- [time off](human-resources/acme_time_off.md)
- [cardiovascular_risk](healthcare/cardiovascular_risk/cardiovascular_risk.txt)
- [insurance](insurance/insurance_policy.md)
- [loan approval](loan/loan_policy.md)

## How to benchmark your policy automation against a test dataset
You want to measure quantitatively the performance of your policy automation, then this project is made for you.
Run your own implementation (pure LLM, LLM generating code, etc) to produce decisions and compare these decisions with reference ones in the available datasets.
Please have a look at this section: [Benchmark your policy implementation](benchmark_your_policy_automation_docs/README.md)

## Common framework
As we are cooking a similar recipe for each policy, the project proposes a common framework to support and accelerate the definition, and data generation of a policy: [Common framework](common/commons_descriptor.md)

## How to extend the corpus to your own policies
If you intend to extend the corpus with a new policy please have a look to this section: [Adding a policy](policy_corpus_extension_docs/README.md)


