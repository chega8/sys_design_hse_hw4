import argparse
import csv
import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import urllib.request
import base64


FLOAT_COLUMNS = ('lat', 'lon', 'merchant_lat', 'merchant_lon')
REQUIRED = {
    'transaction_time', 'merch', 'cat_id', 'amount', 'name_1', 'name_2',
    'gender', 'street', 'one_city', 'us_state', 'post_code', 'lat', 'lon',
    'population_city', 'jobs', 'merchant_lat', 'merchant_lon',
}


def convert(row, filename, number):
    record = dict(row)
    amount = Decimal(row['amount'])
    if not amount.is_finite() or amount != amount.quantize(Decimal('0.01')):
        raise ValueError(f'{filename}:{number}: некорректная сумма')
    record['amount'] = str(amount)
    record['transaction_time'] = datetime.strptime(
        row['transaction_time'], '%Y-%m-%d %H:%M'
    ).strftime('%Y-%m-%d %H:%M:%S')
    for column in FLOAT_COLUMNS:
        record[column] = float(row[column])
    record['population_city'] = int(row['population_city'])
    record['target'] = int(row['target']) if row.get('target') else None
    record['source_file'] = filename
    record['source_row'] = number
    return record


def main():
    parser = argparse.ArgumentParser(description='CSV из ДЗ2 -> ClickHouse ДЗ4')
    parser.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args()
    if len({p.name for p in args.files}) != len(args.files):
        parser.error('Имена файлов должны различаться')
    expected = 0
    for path in args.files:
        with path.open(newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if not REQUIRED <= set(reader.fieldnames):
                parser.error(f'Не хватает колонок в {path}')
            expected += sum(1 for _ in reader)
    if not expected:
        parser.error('В CSV нет данных')
    url = os.getenv('CLICKHOUSE_URL', 'http://localhost:8124')
    user = os.getenv('CLICKHOUSE_USER', 'student')
    password = os.getenv('CLICKHOUSE_PASSWORD', 'student')
    auth = base64.b64encode(f'{user}:{password}'.encode()).decode()

    def query(sql, rows=None):
        payload = sql.encode()
        if rows is not None:
            payload += b'\n' + b'\n'.join(rows)
        req = urllib.request.Request(url, data=payload, headers={'Authorization': 'Basic ' + auth})
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.read().decode().strip()

    current = int(query('SELECT count() FROM homework.transactions'))
    if current:
        unique = int(query('SELECT uniqExact(tuple(source_file, source_row)) FROM homework.transactions'))
        if current == expected == unique:
            print(f'Уже загружено {current} строк, пропускаю')
            return
        raise RuntimeError('Таблица непустая, но число строк не совпадает. Для новой загрузки удалите volume ДЗ4: docker compose down -v')
    total = 0
    for path in args.files:
        batch = []
        with path.open(newline='', encoding='utf-8-sig') as f:
            for number, row in enumerate(csv.DictReader(f), 1):
                batch.append(json.dumps(convert(row, path.name, number), ensure_ascii=False, allow_nan=False).encode())
                if len(batch) == 10000:
                    query('INSERT INTO homework.transactions FORMAT JSONEachRow', batch)
                    total += len(batch)
                    batch.clear()
            if batch:
                query('INSERT INTO homework.transactions FORMAT JSONEachRow', batch)
                total += len(batch)
        print(f'{path.name}: загружено, всего {total} строк', flush=True)
    assert int(query('SELECT count() FROM homework.transactions')) == expected
    print(f'Готово: {expected} строк')


if __name__ == '__main__':
    main()
