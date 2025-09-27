# dns_app

docker compose up --build

curl -X PUT http://localhost:9090/register \
  -H "Content-Type: application/json" \
  -d '{"hostname":"fibonacci.com","ip":"fs","as_ip":"as","as_port":"30001"}'


curl "http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=8&as_ip=as&as_port=30001"

