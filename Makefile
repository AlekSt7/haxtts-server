build:
	docker build -t alekst7/haxtts-service:$(v) -t alekst7/haxtts-service:latest -f dockerfile .
push:
	docker push alekst7/haxtts-service -a
run:
	docker run -p 9898:9898 --gpus all --name hax-tts-service alekst7/haxtts-service
dev:
	make build && make run