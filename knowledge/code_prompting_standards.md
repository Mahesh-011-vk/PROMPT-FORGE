# Code Prompting Standards: Production Engineering

## 1. Type Safety & Schema Validation
- Require strict Pydantic v2 schemas and native Python 3.11+ type hints (`list[str]`, `str | None`).
- Request complete type annotations for all function parameters and return types.

## 2. Asynchronous Architecture
- For high-throughput services, mandate async/await I/O (FastAPI, httpx, SQLAlchemy asyncpg/aiosqlite).
- Avoid mixing synchronous blocking file or network calls in async event loops.

## 3. Testing and Verification
- Request automated pytest test cases alongside implementation code, including edge cases and negative assertions.
