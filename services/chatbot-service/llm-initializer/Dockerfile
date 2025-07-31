FROM curlimages/curl:latest

WORKDIR /app

COPY init-ollama.sh /app/
RUN chmod +x /app/init-ollama.sh

CMD ["/app/init-ollama.sh"]