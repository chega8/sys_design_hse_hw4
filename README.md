# ДЗ4 — dbt и ClickHouse

Отдельный проект на данных из домашки по ClickHouse. Слои: raw → staging → 6 витрин.
Описание моделей, тестов и результатов — в [dbt/README.md](dbt/README.md).

## Запуск

Нужны Docker Compose и Python 3.9+. Положить исходные `train.csv` и `test.csv`
из ДЗ2 в `data/` (CSV в git не добавлены).

```bash
git clone https://github.com/chega8/sys_design_hse_hw4.git
cd sys_design_hse_hw4
mkdir -p data
# Скопировать train.csv и test.csv в data/
docker compose up -d --wait
python3 scripts/load_csv.py data/train.csv data/test.csv
cd dbt
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make deps
make build
make lint
make docs
make serve
```

ClickHouse: http://localhost:8124, student/student. Отдельный volume и порт,
поэтому может работать вместе с ДЗ2. Исходная таблица — `homework.transactions`,
как в ДЗ2 (в условии она называется `transactions_db.transactions`).
Здесь CSV загружаются прямо в ClickHouse: Kafka для работы dbt не нужна.
Преобразование полей при загрузке взято из моего ДЗ2.

Повторная загрузка тех же файлов пропускается при совпадении количества строк
и уникальных ключей. Это проверка количества, а не содержимого CSV.
Для замены данных или после прерванной загрузки удалить только volume этого
проекта: `docker compose down -v`, затем повторить запуск и загрузку.

Проверки: `make test`, `make lint` из `dbt/`. Для git hook активировать окружение,
из корня выполнить `pre-commit install` и `pre-commit run --all-files`.

Сделаны 6 витрин, свой макрос, dbt_utils, dbt_date, dbt_expectations,
34 data tests и 3 unit tests. Настроены SQLFluff, pre-commit и Makefile.
Логи проверки и скриншот dbt Docs — в [dbt/results](dbt/results).

Данные и постановка продолжают [ДЗ2](https://github.com/chega8/sys_design_hse).
