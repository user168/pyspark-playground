build:
	podman compose build

build-yarn:
	podman compose -f docker-compose.yarn.yml build

build-yarn-nc:
	podman compose -f docker-compose.yarn.yml build --no-cache

build-nc:
	podman compose build --no-cache

build-progress:
	podman compose build --no-cache --progress=plain

down:
	podman compose down --volumes --remove-orphans

down-yarn:
	podman compose -f docker-compose.yarn.yml down --volumes --remove-orphans

run:
	make down && podman compose up

run-scaled:
	make down && podman compose up --scale spark-worker=3

run-d:
	make down && podman compose up -d

run-yarn:
	make down-yarn && podman compose -f docker-compose.yarn.yml up

run-yarn-scaled:
	make down-yarn && podman compose -f docker-compose.yarn.yml up --scale spark-yarn-worker=3

stop:
	podman compose stop

stop-yarn:
	podman compose -f docker-compose.yarn.yml stop


submit:
	podman exec da-spark-master spark-submit --master spark://spark-master:7077 --deploy-mode client ./apps/$(app)

submit-da-book:
	make submit app=data_analysis_book/$(app)

submit-yarn-test:
	podman exec da-spark-yarn-master spark-submit --master yarn --deploy-mode cluster ./examples/src/main/python/pi.py

submit-yarn-cluster:
	podman exec da-spark-yarn-master spark-submit --master yarn --deploy-mode cluster ./apps/$(app)

rm-results:
	rm -r book_data/results/*
