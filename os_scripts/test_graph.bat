@echo off
cd /d "%~dp0.."

echo ===== 1. Transitive dependencies (simple.txt) =====
type test_repos\simple.txt
python src\main.py --package A --repo test_repos\simple.txt --test-mode --version 1.0

echo ===== 2. Max depth 2 on a chain A-B-C-D-E-F =====
python src\main.py --package A --repo test_repos\chain.txt --test-mode --version 1.0 --max-depth 2

echo ===== 3. Cyclic dependencies =====
type test_repos\cycle.txt
python src\main.py --package A --repo test_repos\cycle.txt --test-mode --version 1.0 --max-depth 10

echo ===== 4. Start from the middle of the graph =====
python src\main.py --package C --repo test_repos\simple.txt --test-mode --version 1.0

echo ===== 5. Broken test repository =====
python src\main.py --package A --repo test_repos\broken.txt --test-mode --version 1.0

echo ===== 6. Package is not in test repository =====
python src\main.py --package Z --repo test_repos\simple.txt --test-mode --version 1.0
