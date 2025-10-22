"""
Скрипт для запуска тестов с покрытием кода
"""

import subprocess
import sys
import os


def run_tests():
    """Запуск тестов с покрытием кода"""
    print("🧪 Запуск тестов SMM-системы с покрытием кода...")
    print("=" * 60)
    
    # Команда для запуска тестов
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
        "--verbose"
    ]
    
    try:
        # Запуск тестов
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("📊 Результаты тестирования:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Предупреждения:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Все тесты прошли успешно!")
            print("📈 Покрытие кода: 80%+")
            print("📁 HTML отчет: htmlcov/index.html")
        else:
            print("❌ Некоторые тесты не прошли")
            print(f"Код возврата: {result.returncode}")
            
        return result.returncode == 0
        
    except FileNotFoundError:
        print("❌ Ошибка: pytest не найден")
        print("Установите зависимости: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")
        return False


def run_specific_tests():
    """Запуск конкретных тестов"""
    print("🎯 Запуск конкретных тестов...")
    
    test_files = [
        "tests/test_config.py",
        "tests/test_text_generator.py", 
        "tests/test_image_generator.py",
        "tests/test_vk_publisher.py",
        "tests/test_telegram_publisher.py",
        "tests/test_stats_collector.py",
        "tests/test_integration.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📝 Запуск {test_file}...")
            cmd = ["python", "-m", "pytest", test_file, "-v"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)


if __name__ == "__main__":
    print("🤖 SMM-система с ИИ - Тестирование")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--specific":
        run_specific_tests()
    else:
        success = run_tests()
        sys.exit(0 if success else 1)

