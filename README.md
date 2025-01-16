# Analysing failures of Large Language Model services
*FAILS: An automated analysis tool from a Distributed Systems perspective*

**Lab Assignment for "Distributed Systems", Vrije Universiteit 2024/2025**

---

The **Framework for Analysis of Incidents and Outages of LLM Services** (FAILS) is in the [llm_analysis](llm_analysis) folder, with instruction on how to run it.

### Abstract from our paper

Large Language Model (LLM) services have rapidly become essential tools for applications ranging from customer support to content generation, yet their distributed nature makes them prone to failures that impact reliability and uptime. Existing tools for analysing service incidents are either closed-source, lack comparative capabilities, or fail to provide comprehensive insights into failure trends and recovery patterns. To address these gaps, we present FAILS (Framework for Analysis of Incidents and Outages of LLM Services), an open-source system designed to collect, analyse and visualize incident data from leading LLM providers. FAILS enables users to explore temporal trends, assess reliability metrics associated with failure models such as Mean Time to Recovery (MTTR) and Mean Time Between Failures (MTBF), and gain insights into service co-dependencies using a modern LLM-assisted analysis. With a web-based interface and advanced plotting tools, FAILS enables researchers, engineers, and decision-makers to understand and mitigate disruptions due to LLM services.

By [Nishanthi Srinivasan](mailto:n.srinivasan@student.vu.nl), [Bálint László Szarvas](mailto:b.l.szarvas@student.vu.nl) and [Sándor Battaglini-Fischer](mailto:s.battaglini-fischer@student.vu.nl).

Many thanks to [Xiaoyu Chu](mailto:x.chu@vu.nl) and [Prof. Dr. Ir. Alexandru Iosup](a.iosup@vu.nl) for the support!

---

### Some screenshots of the interface:

<img width="2056" alt="mainpage" src="https://github.com/user-attachments/assets/e31dfd2c-54d6-4a3b-ba23-d1c8fd5fb1bc" />
<img width="2056" alt="datatable" src="https://github.com/user-attachments/assets/57fe0198-43fd-41ae-93f5-53c7fc3788bd" />
<img width="2056" alt="chatbot" src="https://github.com/user-attachments/assets/0d927fd0-bffa-4362-9fd2-9c5f2dc609f8" />
<img width="2056" alt="llmanalysis" src="https://github.com/user-attachments/assets/9ebb9e69-0444-41be-888c-c816642895f6" />
