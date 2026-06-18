# Source Tracker - AI Student Doubt Resolution Bot

## Purpose
This file tracks the sources used to build the Business Statistics knowledge base.

The chatbot should answer from approved, topic-wise Markdown files created from reliable sources and reviewed for beginner/intermediate learners.

---

## Source 1

Source ID: SRC-001  
Source Name: OpenStax Introductory Business Statistics 2e  
Source Type: Public textbook-style source  
Storage Location: raw_sources/openstax/  
Topics Covered: Descriptive statistics, probability, probability distributions, hypothesis testing, correlation, regression  
Usage in Project: Reference for summarized topic-wise notes  
Status: To be collected / reviewed  

---

## Source 2

Source ID: SRC-002  
Source Name: NPTEL Business Statistics  
Source Type: Public academic course reference  
Storage Location: raw_sources/nptel/  
Topics Covered: Business statistics, probability, distributions, regression, decision-making applications  
Usage in Project: Topic validation and academic support reference  
Status: To be collected / reviewed  

---

## Source 3

Source ID: SRC-003  
Source Name: Business Statistics Provisional Syllabus  
Source Type: Project-defined syllabus scope  
Storage Location: raw_sources/syllabus/  
Topics Covered: Official working scope for MVP  
Usage in Project: Scope control and topic mapping  
Status: Provisional syllabus created from project charter  

---

## Source 4

Source ID: SRC-004  
Source Name: Faculty Notes / PPTs  
Source Type: Faculty-provided course material  
Storage Location: raw_sources/faculty_notes/  
Topics Covered: Course-specific explanations and examples  
Usage in Project: Highest-priority source if available  
Status: Pending  

---

## Source 5

Source ID: SRC-005  
Source Name: Solved Examples and FAQs  
Source Type: Practice and doubt-resolution material  
Storage Location: raw_sources/solved_examples/ and raw_sources/faq/  
Topics Covered: Numerical examples and common doubts  
Usage in Project: Step-by-step explanation support  
Status: Pending  

---

## Source Control Rule
Only reviewed and approved Markdown files inside knowledge_base/ should be ingested into the vector database.

Raw source files should not be used directly by the chatbot unless they are cleaned, summarized, and validated.