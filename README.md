# API Football Seed (1x/ano)

Script em Python para coletar anualmente os endpoints da **API-FOOTBALL v3**:

- `/countries`
- `/leagues/seasons` (a documentação chama de `leagues/seasons`)
- `/leagues` (apenas ligas europeias, sul-americanas e intercontinentais)
- `/teams` (apenas das ligas filtradas)
- `/venues` (apenas dos times coletados)

Saída em **JSON bruto** no disco, com paginação salva como `_p1.json`, `_p2.json`, etc.

## Requisitos

- Python 3.10+
- Chave válida da API-FOOTBALL (APISports)

## Instalação

```bash
git clone <seu-repo>.git
cd <seu-repo>
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
