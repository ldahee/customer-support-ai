#!/bin/sh
# FAQ MCP 서버 시작 스크립트.
# 서버 시작 전에 data/ 폴더를 스캔해 FAQ를 색인합니다.
# chroma_db/는 git에 없으므로 매 시작 시 재생성합니다.

DATA_DIR="${FAQ_DATA_DIR:-./data}"
QUESTION_COL="${FAQ_QUESTION_COL:-FAQ_제목}"
ANSWER_COL="${FAQ_ANSWER_COL:-FAQ_내용}"

if [ -d "$DATA_DIR" ]; then
    echo "[start.sh] FAQ 색인 백그라운드 시작: $DATA_DIR"
    uv run python -m mcp_servers.faq_search.indexer \
        --data-dir "$DATA_DIR" \
        --question-col "$QUESTION_COL" \
        --answer-col "$ANSWER_COL" \
        --reset &
else
    echo "[start.sh] 경고: $DATA_DIR 폴더가 없습니다. 빈 컬렉션으로 서버를 시작합니다."
fi

exec uv run python -m mcp_servers.faq_search.server
