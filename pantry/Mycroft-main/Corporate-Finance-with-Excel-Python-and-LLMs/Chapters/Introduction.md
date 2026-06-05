# Computational Finance with Excel, Python, and LLMs
## By Nik Bear Brown

## Introduction

Welcome to "Computational Finance with Excel, Python, and LLMs"—a practical, hands-on guide designed to bridge the gap between financial theory and real-world implementation. As financial markets grow increasingly complex and technological tools evolve, the modern finance professional must master multiple computational approaches to stay competitive. This textbook provides a unique trilateral approach to financial problem-solving using the most relevant tools available today: Excel, Python, and Large Language Models (LLMs).

### The Trilateral Approach

The finance industry has evolved through several computational paradigms. Spreadsheet applications like Excel have been the bedrock of financial analysis for decades, offering intuitive interfaces and immediate visual feedback. Python has emerged as the programming language of choice for quantitative finance, providing flexibility, extensive libraries, and computational power. Most recently, Large Language Models like ChatGPT, Claude, and Gemini have revolutionized our ability to process and interpret financial information through natural language.

Rather than advocating for one approach over another, this textbook embraces all three. Each chapter introduces core financial concepts followed by step-by-step implementations across these three platforms:

1. **Excel Implementation**: Leveraging formulas, functions, and visualizations in the world's most widely used spreadsheet application
2. **Python Implementation**: Utilizing financial libraries and programming concepts for scalable, reproducible analysis
3. **LLM Implementation**: Harnessing the power of AI to solve financial problems through carefully crafted prompts

### Minimizing LLM Hallucinations Through Triangulation

One of the most significant challenges when using LLMs for financial calculations is the risk of hallucinations—instances where models confidently produce incorrect information. This textbook introduces a powerful heuristic for mitigating this risk: triangulation across multiple LLM platforms.

Consider the mathematics: If we assume each LLM (ChatGPT, Claude, and Gemini) has an independent 90% accuracy rate for financial calculations, the probability of any single model being correct is 0.9. However, when we adopt the strategy of accepting an answer only when at least two models agree:

- Probability all three models are correct: 0.9³ = 0.729
- Probability exactly two models are correct and one is wrong: 3 × 0.9² × 0.1 = 0.243
- Probability at least two models agree on the correct answer: 0.729 + 0.243 = 0.972

By implementing this triangulation heuristic, we can theoretically improve our accuracy from 90% to 97.2%—a substantial reduction in error rate that makes LLMs significantly more reliable for financial applications.

Throughout this textbook, we'll demonstrate this approach by presenting the same financial problems to ChatGPT, Claude, and Gemini, analyzing their responses, and highlighting cases where triangulation identifies potential hallucinations. When models disagree, we'll explore possible reasons and demonstrate how to critically evaluate competing solutions.

### Who This Book Is For

This textbook is designed for finance students, professionals, and enthusiasts who want to develop practical computational skills. Whether you're a:
- Finance student seeking to build marketable technical skills
- Professional looking to enhance your analytical toolkit
- Programmer interested in financial applications
- Educator teaching computational finance methods

You'll find clear explanations, practical examples, and real-world applications using stocks like Tesla, NVIDIA, AMD, Meta, and others to illustrate financial concepts.

### A Practical, Applied Approach

Unlike traditional finance textbooks that emphasize theory over application, this book focuses on implementation. Each concept is introduced with a clear, concise explanation followed immediately by hands-on examples across all three platforms. The problems progress from simple calculations to complex financial models, always maintaining a focus on practical application.

We'll use real market data for stocks like NVIDIA, Tesla, and AMD to demonstrate concepts like risk measurement, portfolio optimization, options pricing, and market efficiency testing. By working with actual market data, you'll develop an intuitive understanding of financial theories and their limitations in practice.

### The Future of Financial Analysis

As we navigate this trilateral approach, we'll also explore how these tools complement each other. Excel provides accessibility and visualization, Python offers scalability and automation, while LLMs enable natural language interaction with financial data. By mastering all three, you'll be equipped for the future of financial analysis, where hybrid approaches will likely dominate.

The finance industry is undergoing a technological revolution, and professionals who can leverage multiple computational tools will have a significant advantage. This textbook will help you become one of those professionals—capable of selecting the right tool for each financial challenge and implementing solutions with confidence.

Let's begin our journey through computational finance, exploring the power of Excel, Python, and LLMs to solve real financial problems in ways that are accessible, scalable, and increasingly intelligent.
