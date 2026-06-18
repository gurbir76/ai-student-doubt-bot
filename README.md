# AI Student Doubt Resolution Bot

## Project Overview

AI Student Doubt Resolution Bot is a Streamlit-based chatbot designed to help first-year MBA / undergraduate management students understand Business Statistics concepts.

The bot uses a curated topic-wise knowledge base and Retrieval-Augmented Generation (RAG) to answer student doubts from approved course material.

## Purpose

The purpose of this project is to provide students with quick, simple, and course-aware explanations for common Business Statistics doubts.

The bot is designed as a virtual teaching assistant, not a generic chatbot.

## Key Features

- Business Statistics doubt resolution
- Topic-wise Markdown knowledge base
- RAG-based retrieval using ChromaDB
- Embeddings using Sentence Transformers
- Open-source LLM response generation using Groq API
- Source-aware answers
- Escalation for out-of-scope questions
- Simple Streamlit chatbot interface

## Covered Topics

- Introduction to Statistics
- Mean, Median, Mode
- Variance and Standard Deviation
- Basic Probability
- Conditional Probability
- Normal Distribution
- Hypothesis Testing
- P-Value
- Correlation
- Simple Linear Regression
- Formula Bank
- Escalation Rules

## Project Structure

```text
ai-student-doubt-bot/
│
├── app.py
├── rag_engine.py
├── ingest.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── knowledge_base/
│   ├── 01_introduction_to_statistics.md
│   ├── 02_mean_median_mode.md
│   ├── 03_variance_standard_deviation.md
│   ├── 04_basic_probability.md
│   ├── 05_conditional_probability.md
│   ├── 06_normal_distribution.md
│   ├── 07_hypothesis_testing.md
│   ├── 08_p_value.md
│   ├── 09_correlation.md
│   ├── 10_simple_linear_regression.md
│   ├── 11_formula_bank.md
│   └── 12_escalation_rules.md
│
└── metadata/
    ├── source_tracker.md
    └── topic_mapping.md