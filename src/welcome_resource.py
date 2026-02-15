import os

class WelcomeResource:
    """
    Responsabilidade: Gerenciar o acesso ao arquivo de recurso (.wlcm).
    Não sabe sobre abas ou editores, apenas sobre o arquivo de conteúdo.
    """
    def __init__(self):
        # Define o caminho base relativo a este arquivo para garantir portabilidade,
        # mas apontando para a estrutura solicitada: ../walcome-des/Welcome.wlcm
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.welcome_path = os.path.join(base_dir, "walcome-des", "Welcome.wlcm")

    def get_path(self):
        return self.welcome_path

    def exists(self):
        return os.path.exists(self.welcome_path)