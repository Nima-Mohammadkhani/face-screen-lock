set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$DIR/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "virtualenv پیدا نشد. اول این را اجرا کنید:" >&2
    echo "  python3.12 -m venv \"$DIR/.venv\" && \"$VENV_PYTHON\" -m pip install -r \"$DIR/requirements.txt\"" >&2
    exit 1
fi

exec "$VENV_PYTHON" "$DIR/enroll.py"
