# Ponto de entrada para o PluginManager carregar o plugin
import sys
import os

# Adiciona o diretório atual ao path para importações relativas funcionarem bem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.welcome_plugin import WelcomePlugin

plugin = WelcomePlugin()

def register(context):
    plugin.register(context)