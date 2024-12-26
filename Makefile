.PHONY:   build_app_image register_app_image app_local_up app_helm_up 


# deploy app in local
app_local_up:
	docker compose -f deployment/model_predictor/docker-compose.yaml up -d

# build image classifier app
build_app_image:
	docker build -f deployment/model_predictor/Backend_Dockerfile -t liuchangming/txt2img_backend .
	docker build -f deployment/model_predictor/Frontend_Dockerfile -t liuchangming/txt2img_frontend .

register_app_image:
	docker push liuchangming/txt2img_backend
	docker push liuchangming/txt2img_frontend