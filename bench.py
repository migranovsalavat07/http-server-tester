import requests, time, argparse, sys, re


parser = argparse.ArgumentParser(description='Тестирование доступности серверов')
parser.add_argument('-H', '--hosts', required=True, help='Хосты для проверки (через запятую)')
parser.add_argument('-C', '--count', type=int, default=1, help='Количество запросов к каждому хосту')
args = parser.parse_args()

hosts = args.hosts.split(',')
pattern = r'^https{0,}://[a-zA-Z0-9.-]{1,}\.[a-zA-Z]{2,}$'
for host in hosts:
    if not re.match(pattern, host):
        print(f"Ошибка: хост '{host}' имеет неверный формат")
        sys.exit(1)

count = args.count

print(f"Хосты для проверки: {hosts}")
print(f"Количество запросов: {args.count}")
print("=" * 40)

all_result = {}

for host in hosts:
    print(f"\n--- Проверяем {host} ---")

    success = 0
    failed = 0
    errors = 0
    times = []

    for i in range(count):
        try:
            start_time = time.time()
            response = requests.get(host, timeout=5)
            end_time = time.time()
            duration = (end_time - start_time) * 1000

            if 200 <= response.status_code < 300:
                success += 1
                print(f"Запрос {i+1}: статус {response.status_code}, {duration:.2f} мс")
            elif 400 <= response.status_code < 600:
                failed += 1
                print("Запрос {i+1}: ошибка {response.status_code}, {duration:.2f} мс")
            times.append(duration)

        except requests.exceptions.ConnectionError:
            errors += 1
            print(f"  Запрос {i+1}: Ошибка - Сервер недоступен")
        except requests.exceptions.Timeout:
            errors += 1
            print(f"  Запрос {i+1}: Ошибка - Превышено время ожидания")
        except Exception as e:
            errors += 1
            print(f"  Запрос {i+1}: Неизвестная ошибка - {e}")

    all_result[host] = {
        'success': success,
        'failed': failed,
        'errors': errors,
        'times': times}

print("\n" + "=" * 40)
print("ИТОГОВАЯ СТАТИСТИКА")
print("=" * 50)

for host, stats in all_result.items():
    print(f"\n--- {host} ---")
    print(f"Успешных: {stats['success']}")
    print(f"Ошибок сервера: {stats['failed']}")
    print(f"Ошибок подключения: {stats['errors']}")

    valid_times = [t for t in stats['times'] if t is not None]
    if valid_times:
        print(f"Минимальное время: {min(valid_times):.2f} мс")
        print(f"Максимальное время: {max(valid_times):.2f} мс")
        print(f"Среднее время: {sum(valid_times) / len(valid_times):.2f} мс")
    else:
        print("Нет данных о времени")

    print("\n Тестирование завершено!")
