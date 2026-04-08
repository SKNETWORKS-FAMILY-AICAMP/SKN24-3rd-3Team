from dotenv import load_dotenv
load_dotenv()
output_dir      = r".\..\data\output_chunks"
chroma_dir      = r".\..\data\chroma_db"
collection_name = "kosha_child_chunks"

# 경로 각자 맞춰서 지정 필요
import os, json
from pathlib import Path

from openai import OpenAI
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

# https://huggingface.co/jhgan/ko-sroberta-multitask 모델 링크
ko_ef = SentenceTransformerEmbeddingFunction(
    model_name="jhgan/ko-sroberta-multitask"
)

chroma_client = chromadb.PersistentClient(path=chroma_dir)
openai_client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

existing_names = [c.name for c in chroma_client.list_collections()]
is_new = collection_name not in existing_names

collection = chroma_client.get_or_create_collection(
    name=collection_name,
    embedding_function=ko_ef,
    metadata={"hnsw:space": "cosine"}
)

if is_new:
    all_children = []
    for json_file in sorted(Path(output_dir).glob("*_child_chunks.json")):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        all_children.extend(data["chunks"])

    print(f"자식 청크 총 {len(all_children)}개 로드")

    batch_size = 1000
    total = len(all_children)

    for i in range(0, total, batch_size):
        batch = all_children[i:i + batch_size]
        collection.add(
            ids       = [c["chunk_id"] for c in batch],
            # depth 정보 + 본문을 합쳐서 임베딩 (맥락 포함)
            documents = [
                f"{c['depth_1']} {c['depth_2']} {c['depth_3']} {c['content']}"
                for c in batch
            ],
            # 검색 결과와 함께 보여줄 데이터
            metadatas = [{
                "parent_id" : c.get("parent_id", ""),
                "source"    : c["source"],
                "title"     : c.get("title", ""),
                "year"      : str(c.get("year", "")),
                "status"    : c.get("status", "Active"),
                "category"  : c["category"],
                "task"      : c["task"],
                "space"     : c["space"],
                "depth_1"   : c["depth_1"],
                "depth_2"   : c["depth_2"],
                "depth_3"   : c["depth_3"],
            } for c in batch],
        )
        print(f"  {min(i + batch_size, total)}/{total} 저장", end="\r")

    print(f"\n\nChromaDB 저장 완료: {collection.count()}개 벡터")

# chunk_id -> 부모 청크 전체 내용 
# 자식 청크로 검색한 뒤 `parent_id`를 이용해 부모 청크를 로드

parent_map = {}
for json_file in sorted(Path(output_dir).glob("*_parent_chunks.json")):
    data = json.loads(json_file.read_text(encoding="utf-8"))
    for c in data["chunks"]:
        parent_map[c["chunk_id"]] = c

print(f"부모 청크 {len(parent_map)}개 로드")

corpus = []
for json_file in sorted(Path(output_dir).glob("*_child_chunks.json")):
    data = json.loads(json_file.read_text(encoding="utf-8"))
    corpus.extend(data["chunks"])

corpus1 = [c["content"] for c in corpus]

# child_map: 검색된 ID로 조각글(Content)과 부모ID를 찾음
# parent_map은 이미 셀 4에서 *_parent_chunks.json으로 올바르게 로드됨 → 재사용
child_map = {}

for c in corpus:
    c_id = c["chunk_id"]
    child_map[c_id] = {
        "content": c["content"],
        "parent_id": c["parent_id"]
    }

print(f"child_map: {len(child_map)}개, parent_map: {len(parent_map)}개")


from kiwipiepy import Kiwi
from rank_bm25 import BM25Okapi

kiwi = Kiwi()

def kiwi_tokenize(text):
    return [token.form for token in kiwi.tokenize(text)]

tokenized_docs = [kiwi_tokenize(doc) for doc in corpus1]

bm25 = BM25Okapi(tokenized_docs)

def bm25_search(query, top_k=5):
    query_tokens = kiwi_tokenize(query)
    scores = bm25.get_scores(query_tokens)
    ranked_index = sorted(range(len(scores)), key=lambda i: scores[i],reverse=True)

    results = []
    for i in ranked_index[:top_k]:
        child = corpus[i]
        results.append({
            "chunk_id"  : child["chunk_id"],
            "parent_id" : child["parent_id"],
            "source"    : child["source"],
            "depth_1"   : child["depth_1"],
            "score"     : scores[i],
            "content"   : child["content"],
        })
    
    return results

# 랭킹의 역수를 취한 것을 더해서 
def rrf_rank(bm25_list, dense_list, k=60):
    candidate_scores = {}   
    for rank, doc in enumerate(bm25_list):
        candidate_scores[doc] = candidate_scores.get(doc, 0) + 1 / (k + rank)
    for rank, doc in enumerate(dense_list):
        candidate_scores[doc] = candidate_scores.get(doc, 0) + 1 / (k + rank)
    
    # 점수 높은 순으로 정렬하여 (ID, 점수) 리스트 반환
    ranked = sorted(candidate_scores.items(), key=lambda item: item[1], reverse=True)
    return ranked

from cohere import Client, TooManyRequestsError
import time

co = Client()

def cohere_rerank(query, rrf_candidate_ids, child_map, parent_map, max_retries=1, wait_seconds=10):
    # Reranker에게는 Parent 전체가 아닌, 검색된 Child의 핵심 내용만 전달 (정확도 향상)
    texts = [child_map.get(c_id, {}).get("content", "") for c_id in rrf_candidate_ids]

    def call_rerank_api():
        response = co.rerank(
            model='rerank-multilingual-v3.0',
            query=query,
            documents=texts,
            top_n=5 # 최종적으로 필요한 개수
        )
        
        unique_parents = []
        seen_parents = set()
        
        # Rerank 결과에서 Parent ID를 추출하고 중복 제거
        for r in response.results:
            child_id = rrf_candidate_ids[r.index]
            p_id = child_map.get(child_id, {}).get("parent_id", "")
            
            if p_id and p_id not in seen_parents:
                seen_parents.add(p_id)
                unique_parents.append(p_id)
        
        return unique_parents

    for attempt in range(max_retries + 1):
        try:
            return call_rerank_api()
        except TooManyRequestsError:
            if attempt < max_retries:
                print(f"재시도 중... ({attempt + 1}/{max_retries})")
                time.sleep(wait_seconds)
            else:
                raise

from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

from langchain_core.tools import tool
from  langgraph.types import interrupt

@tool
def human_assist(query):
    '''질문에 추가적인 정보가 필요하여 사람의 개입이 필요하면 이 도구를 사용하세요.'''

    human_response = interrupt({'query':query})
    return human_response['data']

import requests
import json
import os

@tool
def get_current_weather(city_name: str, units='metric'):
    '''
    OpenWeatherMap API를 사용하여 사용자가 지정한 도시의 날씨 정보를 가져오는 함수
    '''
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&units={units}&appid={os.getenv("OPENWEATHER_API_KEY")}'
    response = requests.get(url)
    data = response.json()

    # API 오류 처리
    if "main" not in data:
        return json.dumps({
            "error": data.get("message", "날씨 정보를 가져올 수 없습니다."),
            "city": city_name
        }, ensure_ascii=False)

    weather_info = {
        "city"        : city_name,
        "temperature" : data["main"]["temp"],
        "feels_like"  : data["main"]["feels_like"],
        "humidity"    : data["main"]["humidity"],
        "description" : data["weather"][0]["description"],
        "wind_speed"  : data["wind"]["speed"],
    }

    return json.dumps(weather_info, ensure_ascii=False)

JARGON = {
  "가구부찌": "문선, 사진틀",
  "가꾸": "틀, 액자",
  "가꾸목": "각목",
  "가나모노": "철물",
  "가네": "직교, 직각",
  "가네가다": "금형",
  "가다": "틀, 본, 꼴",
  "가다 아시바": "외줄비계",
  "가다 와꾸": "거푸집",
}

from langchain.chat_models import init_chat_model
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.prebuilt import ToolNode

llm = init_chat_model('openai:gpt-4.1-mini')

def rewrite_query(query: str) -> str:
    """건설 현장 은어/일본어 외래어를 표준 용어로 변환"""
    
    # 단어장을 프롬프트에 포함
    jargon_str = "\n".join([f"- {k} → {v}" for k, v in JARGON.items()])
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"""건설 현장에서 사용하는 은어, 일본어 외래어, 오타, 줄임말을 표준 건설 용어로 바꿔줘.
아래 단어장을 우선적으로 참고하고, 단어장에는 발음이 미세하게 다를 수 있어. 이후에 단어장에 없는 경우 문맥으로 판단해줘.

[단어장]
{jargon_str}

변환된 쿼리만 출력하고 다른 말은 하지 마.
은어가 없으면 원문 그대로 반환해."""},
            {"role": "user", "content": query}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()

@tool
def search_safety_regulation(query: str) -> str:
    """건설현장 안전 규정을 검색합니다. 안전 관련 질문이 들어오면 반드시 이 도구를 사용하세요."""

    # 0. 쿼리 재작성 (은어 → 표준어)
    rewritten = rewrite_query(query)
    if rewritten != query:
        print(f"[쿼리 재작성] {query} → {rewritten}")

    # 1. BM25 + Dense (재작성된 쿼리로 검색)
    bm25_top = [r["chunk_id"] for r in bm25_search(rewritten, top_k=50)]
    dense_raw = collection.query(query_texts=[rewritten], n_results=50)
    dense_top = dense_raw["ids"][0]

    # 2. RRF
    rrf_list = rrf_rank(bm25_top, dense_top)
    top_child_ids = [doc_id for doc_id, score in rrf_list[:40]]

    # 3. Cohere Rerank (원래 쿼리로 rerank - 사용자 의도 반영)
    reranked_parent_ids = cohere_rerank(query, top_child_ids, child_map, parent_map)

    # 4. context 구성 후 반환
    context_chunks = []
    for parent_id in reranked_parent_ids:
        parent = parent_map.get(parent_id, {})
        content = parent.get("content", "")
        if content:
            source = parent.get("source", "")
            depth_1 = parent.get("depth_1", "")
            context_chunks.append(f"[출처: {source} / {depth_1}]\n{content}")

    return "\n\n".join(context_chunks) if context_chunks else "관련 내용을 찾을 수 없습니다."

tools = [search_safety_regulation, get_current_weather, human_assist]
llm_with_tools = llm.bind_tools(tools)

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

# State
class State(TypedDict):
    messages: Annotated[List, add_messages]

SYSTEM_PROMPT = """
[상황]
당신은 20년차 건설현장 안전 규정 전문가입니다.
당신은 50억 미만 중소규모 공사현장의 현장소장에게 안전에 관한 조언을 해주어야 합니다.
현장소장은 안전에 대해서 전문가가 아니기 때문에, 애매한 답변은 피하고, 명확하게 답변하세요.
또한 안전규정집에 근거하지 아니하고 답변을 할 경우, 공사 현장에 혼란을 줄 수 있으니,
안전 관련 질문은 반드시 search_safety_regulation 도구로 검색한 내용만을 참고해서 답변하세요.
질문에 날씨가 포함되는 경우에는 반드시 get_current_weather 도구로 최신 날씨 정보를 가져와서 답변에 반영하세요.
만약 질문에 대한 답변을 하는데 추가적인 정보가 필요하다고 판단되면,
human_assist 도구를 사용해서 사람의 도움을 받아보세요.

[도구 사용 규칙]
- 안전 규정 질문 → search_safety_regulation 사용
- 날씨 질문 → get_current_weather 사용 
- human_assist는 다음 경우에만 사용하세요:
  * 사용자가 명시적으로 담당자 연결을 요청할 때
  * 검색 결과가 없고 법적 판단이 필요한 경우
  * 절대 일반적인 안전 규정 질문에는 사용하지 마세요

[응답 규칙]
검색 결과에 없는 내용은 추론하지 말고 '해당 내용을 찾을 수 없습니다'라고 답하세요.
핵심적인 내용 위주로 간결하게 답변하세요.
항상 답변 마지막에 참조한 출처를 표시하세요.
"""

def chatbot(state: State):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

builder = StateGraph(State)
builder.add_node('chatbot', chatbot)
builder.add_node('tools', tool_node)

builder.add_edge(START, 'chatbot')
builder.add_conditional_edges('chatbot', tools_condition)
builder.add_edge('tools', 'chatbot')

graph = builder.compile(checkpointer=checkpointer)
graph


# from langgraph.types import Command

# config = {"configurable": {"thread_id": "1"}}

# def chat(user_input):
#     try:
#         result = graph.invoke(
#             {"messages": [{"role": "user", "content": user_input}]},
#             config=config
#         )
        
#         # interrupt 발생 시 처리
#         if "__interrupt__" in result:
#             interrupt_data = result["__interrupt__"][0].value
#             print(f"\n[추가 정보 필요] {interrupt_data['query']}")
#             human_input = input("답변을 입력하세요: ")
            
#             result = graph.invoke(
#                 Command(resume={"data": human_input}),
#                 config=config
#             )
        
#         print(result["messages"][-1].content)

#     except Exception as e:
#         print(f"에러 발생: {e}")
#         print("새 대화를 시작합니다.")
#         # thread_id 초기화
#         config["configurable"]["thread_id"] = str(int(config["configurable"]["thread_id"]) + 1)


################### streamlit ####################
import streamlit as st
from langgraph.types import Command

# --- [UI 설정] ---
st.set_page_config(page_title="안전 안내 챗봇", page_icon="🏗️")
st.title("🏗️ 건설 현장 안전 전문가 서비스")
st.markdown("현장소장님, 궁금하신 안전 규정이나 날씨를 물어보세요.")

# --- [상태 초기화] ---
# LangGraph의 대화 맥락 유지를 위한 고정 thread_id (세션당 하나)
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "1" 

if "messages" not in st.session_state:
    st.session_state.messages = []

# 휴먼 어시스트(interrupt) 발생 여부 체크용
if "interrupt_query" not in st.session_state:
    st.session_state.interrupt_query = None

# --- [기존 대화 렌더링] ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- [메인 로직] ---
# 1. 일반 질문 처리
if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    with st.chat_message("assistant"):
        with st.spinner("전문가 답변 생성 중..."):
            try:
                # 💡 핵심: 기존 graph 객체를 그대로 사용하며 invoke 호출
                result = graph.invoke(
                    {"messages": [{"role": "user", "content": prompt}]},
                    config=config
                )

                # interrupt 발생 시 처리 루틴
                if "__interrupt__" in result:
                    st.session_state.interrupt_query = result["__interrupt__"][0].value['query']
                    st.warning(f"⚠️ 추가 정보가 필요합니다: {st.session_state.interrupt_query}")
                else:
                    ans = result["messages"][-1].content
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                    st.session_state.interrupt_query = None

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# 2. Human Assist (Interrupt) 입력창 처리
if st.session_state.interrupt_query:
    with st.form("human_input_form"):
        st.info(f"담당자 확인 필요: {st.session_state.interrupt_query}")
        user_response = st.text_input("답변을 입력해 주세요")
        submit = st.form_submit_button("답변 전송")

        if submit and user_response:
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            with st.spinner("답변을 반영하여 다시 분석 중..."):
                # Command(resume)을 통해 중단된 지점부터 다시 시작
                result = graph.invoke(
                    Command(resume={"data": user_response}),
                    config=config
                )
                ans = result["messages"][-1].content
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.session_state.interrupt_query = None
                st.rerun() # 화면 갱신을 위해 재실행