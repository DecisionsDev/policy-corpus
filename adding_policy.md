# How to extend this policy corpus

You can easily augment this corpus of policies to add a new one matching your business needs by respecting these guidelines:
- a new policy is full contained in its folder,
- it comes with a python implementation that inherits from the Policy abstract class,
    - in addition to the decision making code this implementation contains unitary tests validated by a human to check that the decision making is performed as expected
    - in addition the code coverage of the policy implementation is measured at 100%, meaning that all branches have been tested through unit test cases.
    -assuming that the implementation has been checked by a human expert as covering all decisioning aspects enounced in the plain text policy, this implementation can be considered as a reference implementation of the policy. 



