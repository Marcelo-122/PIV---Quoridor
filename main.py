import sys
import os

# Garante que o diretório raiz do projeto esteja no sys.path
# para que as importações de 'src' e 'gui' funcionem corretamente.
_project_root = os.path.abspath(os.path.dirname(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from gui.quoridor_gui import QuoridorGUI  # noqa: E402

if __name__ == "__main__":
    # Instancia e executa a interface gráfica do jogo
    gui = QuoridorGUI()
    gui.run()