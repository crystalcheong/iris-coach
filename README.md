# Introduction
In Singapore, less than 1 in 4 go for annual vaccinations. Only a third of eligible adults are screened for common cancers. Convincing people to be vaccinated or screened for cancer will benefit from a personalised approach, but empathetic conversations are difficult to scale.

# Using LLMs in Dialogue Planning
One way of sustaining empathetic conversations to drive preventive health action could be via LLMs. For persuasive goal-oriented conversation, the LLM has to adequately address the person’s concerns and needs.

Early efforts in goal-based dialogue planning are exploring multi-step planning and using Bayesian techniques to adaptively craft goal-driven utterances. However, there are few efforts that explicitly attempt to address the person’s replies at a psychological or empathetic level.

# Belief Aware, Bayes Adaptive GPT Model
We introduce the Belief-Aware Bayes Adaptive (BABA) GPT, a GPT-4 based agent that leverages the Health Belief Model (Hochbaum, Rosenstock, & Kegels, 1952) as a psychological framework to craft empathetic replies.

<p align="center">
  <img src="./misc/architecture.png" />
</p>

The Health Belief Model suggests that individual health behaviours are shaped by personal perceptions of vulnerabilities to disease risk, alongside the perceived incentives and barriers to taking action.

Our approach disaggregates these concepts into 14 distinct belief scores, allowing us to dynamically monitor them over the course of the conversation. You can view the belief scores in `tools/belief_scores.json`.

In the context of preventive health actions (e.g. cancer screening, vaccinations), we find that the agent is fairly successful at picking up a person’s beliefs around health actions (e.g. perceived vulnerabilities and barriers). We demonstrate the agent’s capabilities in the specific instance of a colorectal cancer screening campaign.

# Setup

```
git clone https://github.com/zacchaeuschok/iris-coach
cd iris-coach
cp .env.example .env
docker-compose up
```
⚠️ everything is local, nothing is sent to the cloud, so be patient, it can take a few minutes to start.

# Usage

Once the setup is completed, you can access the frontend at [localhost:8051](http://localhost:8051) and the management port at [localhost:53795](http://localhost:53795/csp/irisapp/EnsPortal.ProductionConfig.zen?$NAMESPACE=IRISAPP&$NAMESPACE=IRISAPP)

The first page is the chat interface where you can interact with the BABA GPT model. On the sidebar, you may select from a list of FAQs.

# References
Gao, Y. (2023, December 18). Retrieval-Augmented Generation for Large Language Models: A survey. arXiv.org. https://arxiv.org/abs/2312.10997

Hu, Z., Feng, Y., Deng, Y., Li, Z., Ng, S., Luu, A. T., & Hooi, B. (2023). Enhancing large language model induced Task-Oriented dialogue systems through Look-Forward motivated goals. arXiv (Cornell University). https://doi.org/10.48550/arxiv.2309.08949

Jang, Y., Lee, J., & Kim, K.-E. (2020). Bayes-Adaptive Monte-Carlo Planning and Learning for Goal-Oriented Dialogues. Proceedings of the AAAI Conference on Artificial Intelligence, 34(05), 7994-8001. https://doi.org/10.1609/aaai.v34i05.6308

Lau, J., Lim, T.-Z., Jianlin Wong, G., & Tan, K.-K. (2020). The health belief model and colorectal cancer screening in the general population: A systematic review. Preventive Medicine Reports, 20, 101223. https://doi.org/10.1016/j.pmedr.2020.101223

Reddy, S. (2023). Evaluating large language models for use in healthcare: A framework for translational value assessment. Informatics in Medicine Unlocked, 41, 101304. https://doi.org/10.1016/j.imu.2023.101304

Rosenstock, I. M. (1974). The Health Belief Model and Preventive Health Behavior. Health Education Monographs, 2(4), 354–386. http://www.jstor.org/stable/45240623

X, Y., Chen, M., & Yu, Z. (2023). Prompt-Based Monte-Carlo Tree Search for Goal-oriented Dialogue Policy Planning. ACL Anthology. https://doi.org/10.18653/v1/2023.emnlp-main.439
