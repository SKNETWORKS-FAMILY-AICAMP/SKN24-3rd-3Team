# 👷‍♂️ 건설 현장 안전 가이드 질의응답 챗봇

# 1. 팀 소개

<div align="center">

### **현장이랑 안전이랑**
 
| 김규호 | 박수영 | 박세현 | 이동민 | 최하진 |
| :---: | :---: | :---: | :---: | :---: |
| <img width="228" height="291" alt="image" src="https://github.com/assets/파일이름" /> | <img width="227" height="283" alt="image" src="https://github.com/assets/파일이름" /> | <img width="222" height="263" alt="image" src="https://github.com/assets/파일이름" /> | <img width="214" height="277" alt="image" src="https://github.com/assets/파일이름" /> | <img width="219" height="261" alt="image" src="https://github.com/assets/파일이름" /> |
| [![GitHub](https://img.shields.io/badge/GitHub-kyu5KIm-181717?style=flat&logo=github&logoColor=white)](https://github.com/kyu5KIm) | [![GitHub](https://img.shields.io/badge/GitHub-suyoung6279-181717?style=flat&logo=github&logoColor=white)](https://github.com/suyoung6279) | [![GitHub](https://img.shields.io/badge/GitHub-colaa222-181717?style=flat&logo=github&logoColor=white)](https://github.com/이름) | [![GitHub](https://img.shields.io/badge/GitHub-HyojungJ-181717?style=flat&logo=github&logoColor=white)](https://github.com/이름) | [![GitHub](https://img.shields.io/badge/GitHub-doyeon999-181717?style=flat&logo=github&logoColor=white)](https://github.com/이름) |

**프로젝트 기간**: 2026.04.08 ~ 2024.04.09 (2일)

</div>

---

# 🏗️ 뉴런 건설 (Neuron Construction)

## 2. 프로젝트 개요

### 2-1 프로젝트 명
**뉴런 건설**

### 2-2 프로젝트 소개
’뉴런 건설’은 **한국산업안전공단**에서 제·개정한 기술지원규정을 바탕으로 건설 안전 분야에서 활용할 수 있는 안전 지침을 안내하는 챗봇입니다.  

### 2-3 프로젝트 필요성(배경)

#### 🔴 중대재해처벌법 적용의 전면 확대
<p align="center">
  <img src="./assets/images/연합뉴스.jpg" width="600" alt="연합뉴스 기사 캡처">
</p>

2024년 1월부터 **5인 이상 50인 미만**의 모든 사업장에 중대재해처벌법이 적용되면서, 소규모 건설공사 현장 역시 사고 발생 시 경영책임자가 구속되거나 막대한 벌금을 부과받는 등 경영권 상실의 위협에 직면해 있습니다. 

대한건설정책연구원(건정연)에 따르면 최근 판례를 분석한 결과 **중소 건설업계가 법 위반에 가장 취약**한 것으로 나타났습니다. 이는 인력·예산 부족과 함께 안전·보건관리체계 구축과 이행이 본질적으로 어려운 건설업 특성 때문입니다.

> **출처:** [연합뉴스] ["중대재해법 사건 유죄율 '중소기업 건설사' 가장 높아"](https://www.yna.co.kr/view/AKR20250606015200003)

---

#### ⚠️ 안전관리 선임 예외의 역설
<p align="center">
  <img src="./assets/images/매일경제.PNG" width="600" alt="매일경제 기사 캡처">
</p>

현행법상 **50억 미만 건설현장**은 전담 안전관리자 선임 의무가 면제됩니다. 이로 인해 법적 책임은 대형 현장과 동일하게 지면서도, 정작 현장에서 법령을 해석하고 이행을 지원할 전문 인력이 배치되지 않는 **구조적 사각지대**가 발생하고 있습니다.

* **사망 사고의 64.6%(212명):** 공사비 50억 원 미만의 소규모 현장에서 발생
* **산업재해 건수 절반 이상(53%):** 소규모 현장이 차지하는 심각한 불균형

일각에서는 소규모 현장에 대한 안전 지원 확대와 감독 인프라 보강이 함께 이뤄져야 한다는 지적이 나옵니다.

> **출처:** [매일경제] [사망사고 60%는 공사비 50억 미만 영세 공사현장.. 대형사 제제 한계](https://www.mk.co.kr/news/realestate/11439173)

### 2-4 프로젝트 목표

* **기술 지침 접근성 확보:** KOSHA Guide는 2,000여 종에 달하며, 전체 분량은 약 6만 페이지를 넘습니다. 전담 인력이 없는 소규모 현장에서는 숙지와 적용이 사실상 어려운 현실입니다. 이에 안전 지침을 챗봇으로 제공하여 접근성 확보하고 실효성을 높이고자 합니다.
* **건설 현장 안전 제고:** 최근 특별 감독 결과에 따르면, 온습도계 비치 및 기록 관리와 같은 기초 수칙에서만 600건 이상의 위반이 적발되었습니다. 또한 사망 사고 60%는 50억 미만에서 일어나는 만큼 건설 현장 안전을 제고하는 데에 기여하고자 합니다.
* **기술 적용:** 전문 지식이 담긴 대량의 문서를 활용하여 **RAG(Retrieval-Augmented Generation)** 기술을 적용해보고 LLM 챗봇으로 구현해 보고자 합니다.

---

## 3. 기술 스택 & 사용 모델 (Tech Stack & Models)

### 🛠️ Environment & Frameworks
* **Language:** Python
* **Framework:** LangGraph
* **Database:** Pinecone (Vector DB)

### 🤖 AI Models
* **LLM:** OpenAI `gpt-4o-mini`
* **Embedding:** OpenAI `text-embedding-3-small`

### 📚 Libraries
* **Data Parsing:** `pdfplumber` (KOSHA Guide PDF 정밀 파싱)
* **Validation:** `pydantic` (데이터 구조화 및 검증)
* **NLP:** `kiwi` (한국어 형태소 분석 및 텍스트 처리)

---

## 4. 시스템 아키텍쳐 (System Architecture)

<p align="center">
  <img src="./assets/images/architecture.png" width="600" alt="시스템 아키텍쳐">
</p>


## 10. 진행 과정 중 프로그램 개선 노력 (Program Optimization)

RAG 기반 챗봇의 답변 품질은 **'질문에 맞는 정확한 문서를 얼마나 잘 찾아오느냐(Retrieval Performance)'**에 달려 있습니다. 본 프로젝트에서는 전문적인 건설 안전 기술 지침(KOSHA Guide) 데이터를 정확히 검색하기 위해, 다양한 검색 아키텍처를 시뮬레이션하고 정량적으로 비교·분석하며 프로그램을 개선했습니다.

### 10-1 성능 평가를 위한 골든 데이터셋(Golden Dataset) 구축

가장 먼저, 실제 건설 현장에서 발생할 수 있는 구체적인 상황을 가정하여 10가지의 **고품질 테스트 질문 세트(Test Queries)**를 직접 구축했습니다. 이는 LLM이 임의로 생성한 질문이 아닌, 전문 지식이 필요한 질문들로 구성되어 검색 모델의 변별력을 높였습니다.

<p align="center">
  <img src="./assets/images/테스트질문.png" width="700" alt="구축된 10가지 테스트 질문 세트">
  <br>
  <em>[이미지 1] 성능 평가에 사용된 골든 데이터셋(Golden Dataset) 예시</em>
</p>

### 10-2 검색 아키텍처별 정량적 성능 비교 (Baseline)

구축된 질문 세트를 활용하여 네 가지 주요 검색 방식의 성능 지표(유사도, 점수 등)를 측정했습니다.

* **Dense Retrieval:** 벡터 유사도 기반 검색
* **BM25:** 키워드 기반 전통적 검색
* **RRF (Reciprocal Rank Fusion):** Dense와 BM25의 순위를 혼합하는 방식
* **ReRank:** 검색된 결과의 순위를 LLM(또는 전용 모델)을 통해 다시 매기는 방식

<p align="center">
  <img src="./assets/images/1.png" width="600" alt="검색 방식별 성능 지표 비교 표">
  <br>
  <em>[이미지 2] 각 질문별 검색 방식의 초기 성능 지표(Baseline) 분석</em>
</p>

> **초기 분석 결과:** [이미지 2]의 지표를 분석한 결과, 단순히 유사도(`Dense`)만 사용하는 것보다 키워드 기반 검색(`BM25`)을 혼합하거나, 최종적으로 `ReRank` 과정을 거쳤을 때 검색 점수가 유의미하게 상승하는 것을 확인했습니다. 특히 `ReRank (Score)`가 대부분 0.9 이상으로 높게 나타나, ReRanker의 도입이 전문 용어가 많은 건설 안전 문서 검색에 필수적임을 정량적으로 입증했습니다.

### 10-3) 파라미터 최적화 실험 (Grid Search) 및 모델 비교

검색 범위(K)와 혼합 비중(`RRF Top N`)에 변화를 주며, `v3.0` 시리즈의 두 모델(Fast vs Multilingual)을 대상으로 성능을 극대화할 수 있는 임계점을 도출했습니다.

#### 📊 [실험 A] rerank-english-v3.0 (Fast) 성능 지표
영문 최적화 기반 모델로 빠른 처리 속도와 안정적인 점수대를 보였습니다.

| 조합 | BM25 (K) | Dense (K) | RRF Top N | 평균 Top1 Score | 소요 시간 (초) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | 20 | 20 | 10 | 0.9644 | 26.9 |
| 2 | 30 | 30 | 15 | 0.9645 | 21.2 |
| 3 | 30 | 30 | 20 | 0.9644 | 21.8 |
| 4 | 40 | 40 | 20 | 0.9643 | 22.9 |
| 5 | 40 | 40 | 30 | 0.9663 | 22.8 |
| 6 | 50 | 50 | 30 | 0.9654 | 21.7 |
| **7** | **50** | **50** | **40** | **0.9663** | **23.2** |

#### 📊 [실험 B] rerank-multilingual-v3.0 성능 지표
다국어 지원 모델로, 한국어 건설 전문 용어에 대해 더 민감하게 반응하며 최종적으로 가장 높은 점수를 기록했습니다.

| 조합 | BM25 (K) | Dense (K) | RRF Top N | 평균 Top1 Score | 소요 시간 (초) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | 20 | 20 | 10 | 0.9541 | 21.1 |
| 2 | 30 | 30 | 15 | 0.9541 | 21.0 |
| 3 | 30 | 30 | 20 | 0.9539 | 20.7 |
| 4 | 40 | 40 | 20 | 0.9539 | 21.0 |
| 5 | 40 | 40 | 30 | 0.9540 | 20.7 |
| 6 | 50 | 50 | 30 | 0.9540 | 20.8 |
| **7 (최적)** | **50** | **50** | **40** | **0.9691** | **20.8** |

#### 🔍 실험 결과 분석 및 모델 선정
1. **정확도(Accuracy):** `Multilingual` 모델이 조합 7에서 **0.9691**을 기록하며, `Fast` 모델(0.9663)보다 한국어 기술 지침 검색에 더 적합함을 입증했습니다.
2. **효율성(Efficiency):** `Multilingual` 모델은 파라미터가 증가해도 소요 시간이 약 20.8초로 일정하게 유지되어, `Fast` 모델 대비 시간 효율성 면에서도 우위를 점했습니다.
3. **최종 결정:** 한국어 도메인 특화 성능과 안정적인 레이턴시를 모두 확보한 **`rerank-multilingual-v3.0`의 조합 7** 설정을 프로젝트의 최종 검색 엔진으로 채택하였습니다.

### 10-3 알고리즘별 성능 비교 및 ReRank 모델 선정 이유

단순 유사도 검색의 한계를 극복하고, 실제 현장 지침으로서의 신뢰도를 확보하기 위해 4가지 검색 방식(Dense, BM25, RRF, ReRank)의 성능을 정량적으로 비교 분석했습니다.

<p align="center">
  <img src="./assets/images/평가지표.png" width="600" alt="검색 알고리즘별 성능 지표 비교">
  <br>
  <em>[이미지 1] 검색 방식별 주요성능 지표(P@5, R@5, MRR, MAP) 비교</em>
</p>

실험 결과, **ReRank 방식**이 Baseline 대비 압도적인 성능 향상을 보여주었습니다. 특히 검색된 결과 중 정답 문서가 상위에 위치하는지를 평가하는 **MRR(Mean Reciprocal Rank)**과 전체적인 순위 정확도를 나타내는 **MAP(Mean Average Precision)** 지표에서 독보적인 결과를 기록했습니다.

**[ReRank 모델을 최종 엔진으로 선정한 핵심 이유]**

1.  **최상단 응답 정확도의 혁신적 개선:** [이미지 1]에서 볼 수 있듯이, ReRank의 `MRR` 지표는 **0.7449**로 Baseline(Dense, 0.51) 대비 **약 45% 향상**되었습니다. 이는 사용자가 질문했을 때 **가장 관련 있는 핵심 지침이 리스트의 1~2위 내에 배치**됨을 의미합니다. 이는 LLM이 컨텍스트를 파싱할 때 가장 정확한 정보를 최우선으로 참조하게 하여 환각(Hallucination) 현상을 근본적으로 차단합니다.
   
2.  **전문 도메인에 특화된 미세 맥락 구분:** 초기 검색 단계(`BM25`, `Dense`)에서는 관련 문서 후보를 넓게 확보(`Recall@5` 0.86)하는 데 집중하고, 최종 단계인 `ReRank`에서 이를 재정렬함으로써 건설 안전 기술 지침과 같이 전문 용어가 밀집된 문서의 미세한 문맥 차이를 완벽하게 구분해냈습니다.

3.  **정량적으로 검증된 높은 신뢰도:** [이미지 2]의 질의별 최종 점수를 분석한 결과, 대부분의 질의에서 **0.95 이상의 높은 신뢰도 점수**를 기록했습니다. 이는 챗봇이 단순히 답변을 생성하는 것을 넘어, 스스로 제공하는 정보의 근거가 얼마나 확실한지 판단할 수 있는 정량적 기준이 됩니다.

