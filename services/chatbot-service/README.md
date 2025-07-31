# eHealth Chatbot Service

This service provides a conversational AI interface for the eHealth platform.

## Architecture

The chatbot service consists of two main components:

1. **Chatbot API Service**: A FastAPI application that handles user requests and manages conversations
2. **LLM Service**: A separate service that provides the language model capabilities

## Testing End-to-End

To test the chatbot service end-to-end:

1. Start all services using Docker Compose:
   ```
   docker-compose up --build
   ```

2. Wait for all services to start (this may take a few minutes for the LLM service)

3. Run the test script:
   ```
   cd services/chatbot-service
   python test_chatbot.py
   ```

4. You can also test the API directly using the Swagger UI:
   - Open http://localhost:8002/docs in your browser
   - Try the `/api/v1/chat` endpoint with a sample request

## API Endpoints

- `POST /api/v1/chat`: Send a message to the chatbot and get a response
- `GET /health`: Health check endpoint
- `GET /`: Root endpoint with API information

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `ENVIRONMENT`: Environment (development, production)
- `LLM_SERVICE_URL`: URL of the LLM service