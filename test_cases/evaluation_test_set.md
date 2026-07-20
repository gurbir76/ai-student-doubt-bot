# AI Student Doubt Resolution Bot - Evaluation Test Set

## Evaluation Criteria

Each response will be reviewed against:

1. Correctness
2. Relevance
3. Grounding
4. Clarity
5. Completeness
6. Source Quality
7. Scope Compliance

Scoring:

- 2 = Good
- 1 = Acceptable but needs improvement
- 0 = Poor / Incorrect

Maximum Score = 14

Rating:

- 12-14 = Good
- 8-11 = Needs Review
- 0-7 = Poor


---

## Test Case 01

**Category:** Simple Concept  
**Question:** What is mean?

**Expected Model Route:** Simple  
**Expected Source:** 02_mean_median_mode.md  
**Expected Behaviour:** Explain arithmetic mean clearly with a simple example.

**Actual Model Used:** llama-3.1-8b-instant  
**Actual Route:** simple  
**Actual Source:** 02_mean_median_mode.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct explanation of mean with an appropriate simple-model route, relevant source retrieval, and a clear example.  
---

## Test Case 02

**Category:** Numerical  
**Question:** Find the mean of 10, 20, 30, 40, and 50.

**Expected Model Route:** Advanced  
**Expected Source:** 02_mean_median_mode.md  
**Expected Behaviour:** Show formula, substitution, calculation steps, and final answer.

**Actual Model Used:** llama-3.3-70b-versatile  
**Actual Route:** advanced  
**Actual Source:** 02_mean_median_mode.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct numerical answer with step-by-step calculation, appropriate advanced-model routing, and relevant source retrieval.  
---

## Test Case 03

**Category:** Guardrail  
**Question:** Write a Python program to build a website.

**Expected Model Route:** Rule-based / No LLM  
**Expected Source:** None  
**Expected Behaviour:** Politely state that the question is outside the Business Statistics scope.

**Actual Model Used:** Rule-based  
**Actual Route:** guardrail  
**Actual Source:** None  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Out-of-scope programming request was correctly intercepted before RAG retrieval and LLM execution.  
---

## Test Case 04

**Category:** Retrieval Accuracy  
**Question:** What is standard deviation?

**Expected Model Route:** Simple  
**Expected Source:** 03_variance_standard_deviation.md  
**Expected Behaviour:** Explain standard deviation clearly and retrieve only the relevant variance/standard deviation source.

**Actual Model Used:** llama-3.1-8b-instant  
**Actual Route:** simple  
**Actual Source:** 03_variance_standard_deviation.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct explanation with appropriate simple-model routing and accurate retrieval from the standard deviation source.  
---

## Test Case 05

**Category:** Model Routing  
**Question:** Calculate the standard deviation for 10, 20, 30, 40, and 50 and explain each step.

**Expected Model Route:** Advanced  
**Expected Source:** 03_variance_standard_deviation.md  
**Expected Behaviour:** Route to the advanced model and provide step-by-step calculation.

**Actual Model Used:** llama-3.3-70b-versatile  
**Actual Route:** advanced  
**Actual Source:** 03_variance_standard_deviation.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct numerical handling with advanced-model routing and relevant standard deviation source retrieval.  
---

## Test Case 06

**Category:** Guardrail  
**Question:** Tell me the latest cricket score.

**Expected Model Route:** Rule-based / No LLM  
**Expected Source:** None  
**Expected Behaviour:** Politely state that the question is outside the Business Statistics scope.

**Actual Model Used:** Rule-based  
**Actual Route:** guardrail  
**Actual Source:** None  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Out-of-scope cricket query was correctly intercepted before RAG retrieval and LLM execution.  
---

## Test Case 07

**Category:** Simple Concept  
**Question:** What is the difference between median and mode?

**Expected Model Route:** Simple  
**Expected Source:** 02_mean_median_mode.md  
**Expected Behaviour:** Clearly explain the difference between median and mode with a simple example.

**Actual Model Used:** llama-3.1-8b-instant  
**Actual Route:** simple  
**Actual Source:** 02_mean_median_mode.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct conceptual comparison with appropriate simple-model routing and relevant mean/median/mode source retrieval.  
---

## Test Case 08

**Category:** Simple Concept  
**Question:** What is probability?

**Expected Model Route:** Simple  
**Expected Source:** 04_basic_probability.md  
**Expected Behaviour:** Explain basic probability in simple terms and provide a relevant example.

**Actual Model Used:** llama-3.1-8b-instant  
**Actual Route:** simple  
**Actual Source:** 04_basic_probability.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct explanation of basic probability with appropriate simple-model routing and relevant source retrieval.  
---

## Test Case 09

**Category:** Retrieval Accuracy  
**Question:** What is conditional probability and how is it different from basic probability?

**Expected Model Route:** Advanced  
**Expected Source:** 05_conditional_probability.md and/or 04_basic_probability.md
**Expected Behaviour:** Explain conditional probability clearly and distinguish it from basic probability without retrieving unrelated topics.

**Actual Model Used:** llama-3.3-70b-versatile  
**Actual Route:** advanced  
**Actual Source:** 05_conditional_probability.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct explanation of conditional probability with appropriate advanced-model routing. The retrieved source was sufficient for the comparison.  
---

## Test Case 10

**Category:** Simple Concept  
**Question:** What is a normal distribution?

**Expected Model Route:** Simple  
**Expected Source:** 06_normal_distribution.md  
**Expected Behaviour:** Explain normal distribution, its basic characteristics, and its relevance in statistics.

**Actual Model Used:** llama-3.1-8b-instant  
**Actual Route:** simple  
**Actual Source:** 06_normal_distribution.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct explanation of normal distribution with appropriate simple-model routing and relevant source retrieval.  
---

## Test Case 11

**Category:** Conceptual Reasoning  
**Question:** Explain hypothesis testing and why we use a null hypothesis.

**Expected Model Route:** Advanced  
**Expected Source:** 07_hypothesis_testing.md  
**Expected Behaviour:** Explain hypothesis testing, null hypothesis, and the purpose of testing in a clear and structured manner.

**Actual Model Used:** llama-3.3-70b-versatile  
**Actual Route:** advanced  
**Actual Source:** 07_hypothesis_testing.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct explanation of hypothesis testing and the null hypothesis with appropriate advanced-model routing and relevant source retrieval.  
---

## Test Case 12

**Category:** Conceptual Reasoning  
**Question:** What does a p-value of 0.03 mean if the significance level is 0.05?

**Expected Model Route:** Advanced  
**Expected Source:** 08_p_value.md  
**Expected Behaviour:** Correctly explain that the p-value is below the significance level and that the null hypothesis would typically be rejected, while avoiding overclaiming what the result proves.

**Actual Model Used:** llama-3.3-70b-versatile  
**Actual Route:** advanced  
**Actual Source:** 08_p_value.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Correct interpretation of the p-value with appropriate advanced-model routing and relevant p-value source retrieval.  
---

## Test Case 13

**Category:** Multi-Topic / Retrieval Accuracy  
**Question:** What is the difference between correlation and regression?

**Expected Model Route:** Simple or Advanced  
**Expected Source:** 09_correlation.md and/or 10_simple_linear_regression.md  
**Expected Behaviour:** Correctly distinguish correlation from regression and retrieve relevant information from both topics where necessary.

**Actual Model Used:** llama-3.1-8b-instant  
**Actual Route:** simple  
**Actual Source:** 09_correlation.md, 10_simple_linear_regression.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Both correlation and regression sources were retrieved correctly. The simple-model route was appropriate for this conceptual comparison.  
---

## Test Case 14

**Category:** Multi-Topic / Model Routing  
**Question:** Explain correlation and regression, compare their purposes, and give one business example of each.

**Expected Model Route:** Advanced  
**Expected Source:** 09_correlation.md and 10_simple_linear_regression.md  
**Expected Behaviour:** Route to the advanced model, compare both concepts clearly, and provide relevant business examples.

**Actual Model Used:** llama-3.3-70b-versatile  
**Actual Route:** advanced  
**Actual Source:** 09_correlation.md, 10_simple_linear_regression.md  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Both relevant sources were retrieved and the advanced model was correctly selected for a comparative analytical question.  
---

## Test Case 15

**Category:** Edge Case  
**Question:** Help

**Expected Model Route:** Rule-based / No LLM  
**Expected Source:** None  
**Expected Behaviour:** Recognize that the question is unclear or incomplete and ask the student to provide a specific Business Statistics question.

**Actual Model Used:** Rule-based  
**Actual Route:** guardrail  
**Actual Source:** None  
**Correctness:** 2/2  
**Relevance:** 2/2  
**Grounding:** 2/2  
**Clarity:** 2/2  
**Completeness:** 2/2  
**Source Quality:** 2/2  
**Scope Compliance:** 2/2  

**Total Score:** 14/14  
**Rating:** Good  
**Pass/Fail:** Pass  
**Reviewer Comments:** Unclear input was correctly intercepted before RAG retrieval and LLM execution, and the student was prompted to ask a specific Business Statistics question.

---

## Evaluation Summary

**Total Test Cases:** 15  
**Passed:** 15  
**Needs Review:** 0  
**Failed:** 0  

**Key Remediations Completed:**

- Added pre-LLM guardrails for obvious out-of-scope questions.
- Added rule-based handling for unclear or incomplete input.
- Prevented unnecessary RAG retrieval and LLM calls for guardrail cases.
- Added multi-topic retrieval so correlation and regression questions can retrieve both relevant knowledge-base sources.

**Final Evaluation Status:** All 15 test cases passed after remediation.