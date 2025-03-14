I will provide you the policy description document in text format and the input test cases in the json format. 
Your task is to determine whether the provided test cases are eligible or not according to the provided policy description. 

* Here is the policy description document outlining the compliance details:
```text
{policy_document}
```

* Here is the format in which I expect your response:
```json
{{
   "eligible": true or false
}}
```

**Strict Requirements**:

1. Complete Policy Coverage:
    * Your response should take into an account all cases, rules, and logic described in the policy document when returning the final answer.
    * Ensure that no details are omitted from the policy description.
2. Provide **only** the response in the specified json format.