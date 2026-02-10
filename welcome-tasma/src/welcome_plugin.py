import os
import curses
from .welcome_resource import WelcomeResource

class WelcomePlugin:
    """
    Responsabilidade: Integrar-se ao Tasma e garantir que a tela de boas-vindas
    seja exibida quando não houver outros arquivos abertos.
    """
    def __init__(self):
        self.resource = WelcomeResource()
        self.tab_manager = None
        self.ui = None
        self.original_close_method = None
        self.original_draw_editor_pane = None

    def register(self, context):
        self.tab_manager = context.get('tab_manager')
        self.ui = context.get('ui')
        
        if self.tab_manager:
            # Monkey Patch: Intercepta o método close_current_tab do TabManager
            # Isso permite injetar comportamento sem alterar o código principal (main.py)
            self.original_close_method = self.tab_manager.close_current_tab
            self.tab_manager.close_current_tab = self._hook_close_current_tab

            # Verificação inicial: Se o editor abriu sem arquivos (apenas buffer vazio padrão)
            # ou se o arquivo padrão não existe, podemos forçar o welcome (opcional, 
            # mas aqui focamos na lógica de "quando não tem arquivo aberto").
            # Como o main.py sempre abre um arquivo inicial, a lógica principal fica no hook de fechar.

        if self.ui:
            # Monkey Patch: Intercepta o desenho do editor para aplicar cores customizadas
            self.original_draw_editor_pane = self.ui._draw_editor_pane
            self.ui._draw_editor_pane = self._hook_draw_editor_pane

    def _hook_close_current_tab(self):
        """
        Executa o fechamento original e verifica se a lista de abas ficou vazia.
        """
        # 1. Executa o método original de fechar aba
        result = self.original_close_method()

        # 2. Verifica se não restou nenhuma aba
        if not self.tab_manager.open_tabs:
            self._open_welcome_screen()
            # Retorna True para indicar que "algo" está aberto (o welcome),
            # impedindo o main.py de encerrar o loop principal.
            return True
            
        return result

    def _open_welcome_screen(self):
        """Abre o arquivo .wlcm como uma nova aba."""
        path = self.resource.get_path()
        if self.resource.exists():
            try:
                self.tab_manager.open_file(path)
            except Exception:
                pass

    def _hook_draw_editor_pane(self, editor, rect, filepath, is_active):
        """Intercepta o desenho para aplicar gradiente no arquivo de boas-vindas."""
        if filepath and filepath.endswith(".wlcm"):
            self._draw_welcome_gradient(editor, rect)
        else:
            if self.original_draw_editor_pane:
                self.original_draw_editor_pane(editor, rect, filepath, is_active)

    def _draw_welcome_gradient(self, editor, rect):
        """Desenha o conteúdo com um efeito degradê baseado nas cores do tema."""
        y, x, h, w = rect
        
        # Lógica de rolagem simplificada (copiada/adaptada da UI original)
        visual_indices = editor.get_visual_indices()
        try:
            vis_cursor_y = visual_indices.index(editor.cy)
        except ValueError:
            vis_cursor_y = 0

        if vis_cursor_y < editor.scroll_offset_y:
            editor.scroll_offset_y = vis_cursor_y
        if vis_cursor_y >= editor.scroll_offset_y + h:
            editor.scroll_offset_y = vis_cursor_y - (h - 1)

        # Margem para manter consistência visual
        line_count = len(editor.lines)
        line_num_width = len(str(line_count))
        gutter_width = line_num_width + 3
        total_left_margin = x + gutter_width
        
        # Cores do tema (usando pares de sintaxe para garantir harmonia com o tema atual)
        colors = [
            curses.color_pair(1), # Keyword
            curses.color_pair(7), # Class
            curses.color_pair(6), # Number
            curses.color_pair(2), # String
            curses.color_pair(3), # Comment
        ]
        
        for i in range(h):
            vis_idx = i + editor.scroll_offset_y
            if vis_idx >= len(visual_indices): break
            
            file_line_idx = visual_indices[vis_idx]
            line_content = editor.lines[file_line_idx]
            screen_y = y + i
            
            # Efeito Degradê: Cicla as cores a cada 2 linhas
            color_idx = (i // 2) % len(colors)
            attr = colors[color_idx] | curses.A_BOLD
            
            # Desenha o conteúdo usando método auxiliar da UI
            self.ui._addstr_clipped(screen_y, total_left_margin, line_content, attr, min_x=total_left_margin)