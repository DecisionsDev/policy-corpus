# How to extend the policy corpus
P.S. The naming conventions used in this file are not mandatory and are introduced solely to facilitate understanding.

## General requirements
You can easily augment this corpus of policies to add a new one matching your business needs by respecting these guidelines:
- a new policy is full contained in its folder,
- it comes with a python implementation that inherits from the Policy abstract class,
    - in addition to the decision making code this implementation contains unitary tests validated by a human to check that the decision making is performed as expected
    - in addition the code coverage of the policy implementation is measured at 100%, meaning that all branches have been tested through unit test cases.
    - assuming that the implementation has been checked by a human expert as covering all decisioning aspects enounced in the plain text policy, this implementation can be considered as a reference implementation of the policy. 

## Policy Corpus Extension Guidelines

1. **File Structure Preparation:**
   1. Create a new folder at the root level, naming it with a short identifier for the new policy. If a similar folder already exists, reuse that folder.
   2. If the folder is new:
      1. Create a `pyproject.toml` file within it, describing the folder structure and required dependencies. An example of such a file can be found in the [luggage](../luggage/pyproject.toml) folder.
      2. Otherwise, add any new dependencies to the existing `pyproject.toml` file (if applicable).
   3. Inside this folder, create another folder with a more explicit name for the new policy.
   4. From this point onward, work within the newly created folder as described above.

2. **Create a Policy Description Document:**
   - Write a text document outlining the general policy. An example can be found in [luggage_policy.txt](../luggage/luggage_policy.txt).

3. **Create/Generate the `{policy_name}_policy.py` File:**
   - This file contains the policy automation, determining whether a case is eligible according to the policy document created in step 2.
   - The file can be:
     1. Written manually (Not recommended).
     2. Generated using an LLM (Granit, Llama, Mistral, GPT, Cloud) by adapting the [policy prompt template](prompt_template_policyautomation). 
        - Update the values in `{}` (curly brackets) within the template.
        - Copy and paste the policy text document created in step 2.
        - (If there are other classes, which are used in the preexisting policy): copy and paste them instead of `{predefined_data_structures}`. Otherwise, delete this point.

4. **(Skip if step 3.2 was chosen) Add Unit Tests:**
   - In the same `{policy_name}_policy.py` file, include a unit test class.

5. **Verify Unit Test Coverage:**
   - Ensure that the unit tests in `{policy_name}_policy.py` cover and handle the complex logic described in the policy document created in step 2.
   - If satisfied, proceed.
   - If not satisfied, modify `{policy_name}_policy.py` and return to step 4.

6. **Generate the Data Generator (`{policy_name}_data_generator.py`):**
   - Use the `Policy` class from `{policy_name}_policy.py` to create this file.
   - The file can be:
     1. Written manually (Not recommended).
     2. Generated using an LLM by adapting the [data generator prompt template](prompt_template_data_generator.md).
        - Update the values in `{}` (curly brackets) within the template.
        - Copy and paste:
          - The policy text document (step 2)
          - The policy code (step 3)
          - The `{policy_name}_policy.py` filename (without `.py`)
          - The `Policy` class name from `{policy_name}_policy.py`

7. **Run `{policy_name}_data_generator.py`:**
   - Specify the number of samples needed.

8. **Verify the Generated Data Samples:**
   - Ensure that the `.csv` files created in the previous step cover all cases described in the policy text document.
   - If satisfied, proceed.
   - If not satisfied, modify `{policy_name}_data_generator.py` and return to step 5.

9. **Create `{policy_name}_policytester.py`:**
   - Test the alignment of the generated data with the `Policy` class from `{policy_name}_policy.py`.
   - You can adapt the code from the [tester template](tester_template.md).

10. **Run `{policy_name}_policytester.py`:**
    - If the returned metrics are `< 1.0`, investigate the errors and fix `{policy_name}_data_generator.py` and `{policy_name}_policy.py`.
    - If all metrics equal `1.0`, congratulations! You have successfully created a new policy.