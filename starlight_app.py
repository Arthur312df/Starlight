import customtkinter as ctk

# Configuração inicial do tema do CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class StarLightApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela principal
        self.title("StarLight - IA Assistant")
        self.geometry("1280x720")
        self.minsize(1024, 600)

        # Configurar o grid principal da janela (2 colunas: Barra lateral e Chat)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 1. BARRA LATERAL (CONVERSAS) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=("#121212", "#0d0d0d"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        # Título StarLight na barra lateral
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="StarLight", 
            font=ctk.CTkFont(family="Arial", size=22, weight="bold")
        )
        self.logo_label.pack(anchor="w", padx=20, pady=(25, 10))

        # Seção Conversas
        self.conversas_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Conversas", 
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color="gray70"
        )
        self.conversas_label.pack(anchor="w", padx=20, pady=(15, 10))

        # Botões de histórico de conversas
        hist_styles = {"fg_color": "transparent", "hover_color": ("#2b2b2b", "#1f1f1f"), "anchor": "w", "font": ctk.CTkFont(family="Arial", size=13)}
        
        self.btn_hist1 = ctk.CTkButton(self.sidebar_frame, text="Conversa sobre o tempo.", **hist_styles)
        self.btn_hist1.pack(fill="x", padx=12, pady=4)

        self.btn_hist2 = ctk.CTkButton(self.sidebar_frame, text="Cinema em Brasília.", **hist_styles)
        self.btn_hist2.pack(fill="x", padx=12, pady=4)

        self.btn_hist3 = ctk.CTkButton(self.sidebar_frame, text="Campeonato de League...", **hist_styles)
        self.btn_hist3.pack(fill="x", padx=12, pady=4)


        # --- 2. PAINEL PRINCIPAL DE CHAT ---
        self.main_frame = ctk.CTkFrame(self, fg_color=("#1f3a40", "#14282c"), corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Cabeçalho do Chat (Versão e Botão Reportar Bug)
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=40)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 0))
        
        # Botão Reportar Bug (Vermelho em destaque à direita)
        self.btn_bug = ctk.CTkButton(
            self.header_frame,
            text="Reportar Bug",
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            fg_color="#b30000", hover_color="#800000", text_color="white",
            corner_radius=6, width=100, height=26
        )
        self.btn_bug.pack(side="right", padx=(10, 0))

        # Rótulo da Versão
        self.version_label = ctk.CTkLabel(
            self.header_frame, 
            text="Versão: 1.2", 
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            fg_color=("#d0d0d0", "#d0d0d0"), text_color="black", corner_radius=6
        )
        self.version_label.pack(side="right", ipadx=8, ipady=3)

        # Área de rolagem para o histórico dinâmico de mensagens
        self.chat_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=25, pady=10)
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        self.msg_row_counter = 0
        self.placeholder_text = "Digite sua mensagem... Aperte enter para enviar"
        self.is_placeholder_active = True


        # --- 3. RODAPÉ (INPUT DE MENSAGEM) ---
        self.footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=350, pady=(0, 20))
        self.footer_frame.grid_columnconfigure(0, weight=1)

        # Caixa de texto compacta
        self.entry_message = ctk.CTkTextbox(
            self.footer_frame, 
            height=28,
            corner_radius=14,
            font=ctk.CTkFont(family="Arial", size=12),
            fg_color=("#e0e0e0", "#e0e0e0"), text_color="gray40"
        )
        self.entry_message.grid(row=0, column=0, sticky="ew")
        
        # Inserindo texto de instrução inicial
        self.entry_message.insert("0.0", self.placeholder_text)

        # Eventos para gerenciar o placeholder e o envio
        self.entry_message.bind("<FocusIn>", self.clear_placeholder)
        self.entry_message.bind("<FocusOut>", self.restore_placeholder)
        self.entry_message.bind("<KeyPress>", self.on_key_press)
        self.entry_message.bind("<Return>", self.on_return_pressed)

    def clear_placeholder(self, event=None):
        if self.is_placeholder_active:
            self.entry_message.delete("0.0", "end")
            self.entry_message.configure(text_color="black")
            self.is_placeholder_active = False

    def restore_placeholder(self, event=None):
        current_text = self.entry_message.get("0.0", "end-1c").strip()
        if not current_text:
            self.entry_message.delete("0.0", "end")
            self.entry_message.insert("0.0", self.placeholder_text)
            self.entry_message.configure(text_color="gray40")
            self.is_placeholder_active = True

    def on_key_press(self, event):
        # Se a tecla pressionada for válida (não for modificadores como Shift/Control) e o placeholder estiver ativo, apaga ele na hora
        if self.is_placeholder_active and event.keysym not in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"):
            self.clear_placeholder()

    def on_return_pressed(self, event):
        self.send_message()
        return "break" # Impede que o Enter crie uma nova linha

    def send_message(self):
        if self.is_placeholder_active:
            return

        mensagem = self.entry_message.get("0.0", "end-1c").strip()
        
        if mensagem:
            # 1. Adiciona a mensagem do usuário (Direita)
            user_msg_label = ctk.CTkLabel(
                self.chat_scroll, 
                text=mensagem, 
                font=ctk.CTkFont(family="Arial", size=14),
                fg_color=("#d1e7dd", "#1e3d2f"), text_color="white", 
                corner_radius=12, justify="left", wraplength=600
            )
            user_msg_label.grid(row=self.msg_row_counter, column=0, sticky="e", padx=10, pady=8, ipadx=10, ipady=8)
            self.msg_row_counter += 1

            # Limpa o campo e restaura o placeholder
            self.entry_message.delete("0.0", "end")
            self.restore_placeholder()

            # 2. Resposta da StarLight (Esquerda)
            bot_response = ctk.CTkLabel(
                self.chat_scroll, 
                text="Olá! Estou processando a sua solicitação com o novo visual da StarLight.", 
                font=ctk.CTkFont(family="Arial", size=14),
                fg_color=("#e0e0e0", "#2b2b2b"), text_color="white", 
                corner_radius=12, justify="left", wraplength=600
            )
            bot_response.grid(row=self.msg_row_counter, column=0, sticky="w", padx=10, pady=8, ipadx=10, ipady=8)
            self.msg_row_counter += 1


if __name__ == "__main__":
    app = StarLightApp()
    app.mainloop()