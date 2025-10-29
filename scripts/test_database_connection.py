"""
Supabase 데이터베이스 연결 테스트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# .env 파일 로드
env_path = project_root / "backend" / ".env"
load_dotenv(env_path)

db_url = os.getenv('DATABASE_URL')

print("=" * 60)
print("Supabase 데이터베이스 연결 테스트")
print("=" * 60)
print(f"\nDB URL: {db_url[:50]}...")

try:
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # PostgreSQL 버전 확인
        result = conn.execute(text('SELECT version()'))
        version = result.fetchone()[0]

        print(f"\n✅ Supabase 연결 성공!")
        print(f"\nPostgreSQL 버전:")
        print(f"  {version[:80]}...")

        # 현재 데이터베이스명 확인
        result = conn.execute(text('SELECT current_database()'))
        db_name = result.fetchone()[0]
        print(f"\n현재 데이터베이스: {db_name}")

        # 기존 테이블 목록 확인
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        tables = result.fetchall()

        print(f"\n기존 테이블 수: {len(tables)}개")
        if tables:
            print("테이블 목록:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  (테이블 없음)")

except Exception as e:
    print(f"\n❌ 연결 실패!")
    print(f"에러: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 데이터베이스 연결 테스트 완료")
print("=" * 60)
