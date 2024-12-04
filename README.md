# Analysis and Modeling of LLM Service Failures

Lab Assignment for "Distributed Systems", Vrije Universiteit 2024

## To Do

Interface:

- (S) Improve mobile view, color palette, components
- (S) Add JS plotting framework for interactive plots w/ python/matplotlib download

Data collection:

- (N) Integrate Stability AI collection with the rest (same CSV)
- (S) Configure a Cronjob to run in the background
- Check if Google AI has usage data, if not maybe third party data collection option
- If we have time: other services (?)

Data analysis:

- (B) Improve plots, make sure it is consistent with what their repo had
- (S) See what additional research/analyis we can do
- Ideas:
  - (S) ~~use LLM to analyse the results from the plots and:~~
    - give a user profile based suggestion (questionaire, what time they use llms -> which one is best)
    - use RAG to train on course material (local inference)
    - Prompt engineer based on previous knowledge
  - API vs GUI version (ChatGPT/Claude) analysis (hypothesis: API more stable)
  - (S) Geographical distribution of outages from downdetector (might be too hard to automate)
  - (S) Predictive failure model:
    - Time series modelling (when will failures occur)
    - How fast will failures be resolved
  - (S) ~~Distribution of Incident Impact Level~~ (and then generalise to a new metric, new taxonomy?)
  - Why do the failures occur more often for some services? Company infrastructure, goals, tech stack, funding, computational resources, etc. How would we improve the service as a Distributed System?
  - Assessment of the quality of status reporting (per service provider)

General:

- Document what we have done (design process)
- Document time spent etc
- Integrate material from course:
  - How do LLM services balance workload/scheduling
  - What about consistency handling?
- Start writing the report and PPT (?)
