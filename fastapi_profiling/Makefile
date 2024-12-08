.PHONY: generate

API_URL = http://localhost:8000/generate/
QUERY = こんにちは、自己紹介をお願いします。

generate:
	@curl -X POST "$(API_URL)" \
		-H "Content-Type: application/json" \
		-d '{"query": "$(QUERY)"}'
