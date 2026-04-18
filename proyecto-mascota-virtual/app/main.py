import pygame
import sys
import os
import math
import pyttsx3
import json

# --- 1. INICIALIZACIÓN ---
pygame.init()
pygame.mixer.init()
ANCHO, ALTO = 800, 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Mascota Virtual (POO)")

engine = pyttsx3.init()

# --- 2. CLASES DE MASCOTAS (POO con Herencia) ---

class Mascota:
    """Clase Madre con los atributos y métodos comunes."""
    def __init__(self, tipo, nombre, hambre, energia, felicidad):
        self.tipo = tipo
        self.nombre = nombre
        self.hambre = hambre
        self.energia = energia
        self.felicidad = felicidad
        self.durmiendo = False
        
        # Carga de recursos
        self.img = self.cargar_img(f"{tipo}.png", (250, 250))
        self.snd_comer = self.cargar_snd("comer.wav")
        self.snd_dormir = self.cargar_snd("dormir.wav")
        
        # Lógica de movimiento
        self.px, self.py = ANCHO//2 - 125, ALTO//2 - 50
        self.timer_comida = 0
        self.timer_jugar = 0

    def cargar_img(self, n, t):
        r = os.path.join("recursos", n)
        if os.path.exists(r): return pygame.transform.scale(pygame.image.load(r), t)
        return None

    def cargar_snd(self, n):
        r = os.path.join("recursos", "sonidos", n)
        if os.path.exists(r): return pygame.mixer.Sound(r)
        return None

    def actualizar_stats(self):
        if not self.durmiendo:
            self.hambre = min(100, self.hambre + 0.02)
            self.energia = max(0, self.energia - 0.01)
            self.felicidad = max(0, self.felicidad - 0.015)
        else:
            self.energia = min(100, self.energia + 0.15)
            if self.energia >= 100: self.alternar_sueno()

    def comer(self):
        if not self.durmiendo:
            self.hambre = max(0, self.hambre - 15)
            self.timer_comida = 60
            if self.snd_comer: self.snd_comer.play()

    def alternar_sueno(self):
        self.durmiendo = not self.durmiendo
        if self.durmiendo:
            if self.snd_dormir: self.snd_dormir.play(-1)
        else:
            if self.snd_dormir: self.snd_dormir.stop()

class Perro(Mascota):
    def __init__(self, nombre, h=30, e=100, f=70):
        super().__init__("perro", nombre, h, e, f)
        self.snd_voz = self.cargar_snd("perro.wav")

    def jugar(self):
        if not self.durmiendo:
            self.felicidad = min(100, self.felicidad + 15)
            self.timer_jugar = 300
            if self.snd_voz: self.snd_voz.play()

class Gato(Mascota):
    def __init__(self, nombre, h=30, e=100, f=70):
        super().__init__("gato", nombre, h, e, f)
        self.snd_voz = self.cargar_snd("gato.wav")

    def jugar(self):
        if not self.durmiendo:
            self.felicidad = min(100, self.felicidad + 15)
            self.timer_jugar = 300
            if self.snd_voz: self.snd_voz.play()

class Loro(Mascota):
    def __init__(self, nombre, h=30, e=100, f=70):
        super().__init__("loro", nombre, h, e, f)
        self.snd_voz = self.cargar_snd("loro.wav")
        self.snd_campana = self.cargar_snd("../campana.wav") # Está un nivel arriba

    def jugar(self):
        if not self.durmiendo:
            self.felicidad = min(100, self.felicidad + 15)
            self.timer_jugar = 300
            if self.snd_voz: self.snd_voz.play()

# --- 3. SISTEMA DE BASE DE DATOS ---
def guardar_partida(pet):
    bd = cargar_toda_la_bd()
    bd[pet.tipo] = {
        "nombre": pet.nombre, "hambre": pet.hambre,
        "energia": pet.energia, "felicidad": pet.felicidad
    }
    with open("base_de_datos.json", "w") as f: json.dump(bd, f)

def cargar_toda_la_bd():
    if os.path.exists("base_de_datos.json"):
        try:
            with open("base_de_datos.json", "r") as f: return json.load(f)
        except: return {}
    return {}

# --- 4. FUNCIONES DE APOYO VISUAL ---
BLANCO, NEGRO = (255, 255, 255), (20, 20, 30)
CELESTE, VERDE, ROJO, AMARILLO = (52, 152, 219), (46, 204, 113), (231, 76, 60), (241, 196, 15)
AZUL_Z, GRIS_SEMILLA, AZUL_PESCADO, ROJO_PELOTA = (135, 206, 250), (60, 60, 60), (93, 173, 226), (255, 0, 0)
fuente = pygame.font.SysFont("Verdana", 20, bold=True)
fuente_zzz = pygame.font.SysFont("Arial", 35, bold=True)

def dibujar_boton(rect, texto, color):
    pygame.draw.rect(ventana, color, rect, border_radius=12)
    pygame.draw.rect(ventana, (255, 255, 255), rect, 2, border_radius=12)
    txt = fuente.render(texto, True, (255, 255, 255))
    ventana.blit(txt, txt.get_rect(center=rect.center))

# --- 5. PANTALLA PRINCIPAL DE JUEGO ---
def pantalla_juego(tipo, nombre, hambre=30, energia=100, felicidad=70):
    # Instanciar clase según el tipo
    if tipo == "gato": pet = Gato(nombre, hambre, energia, felicidad)
    elif tipo == "perro": pet = Perro(nombre, hambre, energia, felicidad)
    else: pet = Loro(nombre, hambre, energia, felicidad)

    fondo = pet.cargar_img(f"fondo_{tipo}.jpg", (ANCHO, ALTO))
    if tipo == "loro": engine.setProperty('rate', 145)
    
    reloj = pygame.time.Clock()
    texto_chat = ""
    b_comer = pygame.Rect(50, 500, 160, 60); b_jugar = pygame.Rect(230, 500, 160, 60)
    b_dormir = pygame.Rect(410, 500, 160, 60); b_volver = pygame.Rect(590, 500, 160, 60)

    while True:
        if fondo: ventana.blit(fondo, (0,0))
        else: ventana.fill((100,100,100))
        
        pet.actualizar_stats()

        if pet.durmiendo:
            sueño_surf = pygame.Surface((ANCHO, ALTO)); sueño_surf.set_alpha(180); sueño_surf.fill((10, 10, 40))
            ventana.blit(sueño_surf, (0,0))

        t = pygame.time.get_ticks() * 0.005
        oy, lx, ly, bx, by, arc = 0, 0, 0, 0, 0, 0
        
        if not pet.durmiendo:
            oy = math.sin(t * 2) * 5
            if pet.timer_jugar > 0:
                if tipo == "gato": 
                    t_l = pygame.time.get_ticks() * 0.004
                    lx, ly = ANCHO//2 + math.cos(t_l)*180, ALTO//2 + 100 + math.sin(t_l*0.6)*50
                    pet.px += (lx-125-pet.px)*0.08; pet.py += (ly-180-pet.py)*0.08
                elif tipo == "perro":
                    t_p = pygame.time.get_ticks() * 0.003
                    bx, by = ANCHO//2 + math.cos(t_p)*200, ALTO//2 + 130
                    pet.px += (bx-125-pet.px)*0.07
                elif tipo == "loro":
                    arc = math.sin(pygame.time.get_ticks() * 0.002) * 70 
                    pet.px += ((ANCHO//2 - 125 + arc) - pet.px) * 0.05 
                    if abs(arc) > 65 and pet.snd_campana:
                        if not pygame.mixer.get_busy(): pet.snd_campana.play()
                pet.timer_jugar -= 1
            else:
                pet.px += (ANCHO//2 - 125 - pet.px) * 0.05; pet.py += (ALTO//2 - 50 - pet.py) * 0.05

        if pet.img:
            img_c = pet.img.copy()
            if pet.durmiendo: img_c.set_alpha(150) 
            ventana.blit(img_c, (pet.px, pet.py + oy))

        if pet.durmiendo:
            offset_z = math.sin(pygame.time.get_ticks() * 0.003) * 10
            ventana.blit(fuente_zzz.render("Zzz...", True, AZUL_Z), (pet.px + 180, pet.py - 40 + offset_z))

        # Dibujar objetos de juego
        if not pet.durmiendo and pet.timer_jugar > 0:
            if tipo == "gato": pygame.draw.circle(ventana, (255, 0, 0), (int(lx), int(ly)), 6)
            elif tipo == "perro":
                pygame.draw.circle(ventana, ROJO_PELOTA, (int(bx), int(by)), 15)
                pygame.draw.circle(ventana, BLANCO, (int(bx) - 4, int(by) - 4), 4)
            elif tipo == "loro":
                pygame.draw.line(ventana, (80, 80, 80), (ANCHO//2, 0), (ANCHO//2 + arc, 220), 3)
                pygame.draw.circle(ventana, AMARILLO, (int(ANCHO//2 + arc), 220), 22)

        # Dibujar comida
        if pet.timer_comida > 0 and not pet.durmiendo:
            prog = (60 - pet.timer_comida) / 60
            cx_f = ANCHO - (ANCHO - (pet.px + 100)) * prog
            cy_f = (ALTO // 2 + 50) - math.sin(prog * math.pi) * 100
            if tipo == "gato":
                pygame.draw.ellipse(ventana, AZUL_PESCADO, (cx_f, cy_f, 25, 15))
                pygame.draw.polygon(ventana, AZUL_PESCADO, [(cx_f+22, cy_f+7), (cx_f+32, cy_f), (cx_f+32, cy_f+14)])
            elif tipo == "loro":
                pygame.draw.ellipse(ventana, GRIS_SEMILLA, (cx_f, cy_f, 12, 20))
            else: pygame.draw.circle(ventana, (110, 70, 40), (int(cx_f), int(cy_f)), 10)
            pet.timer_comida -= 1

        if tipo == "loro" and not pet.durmiendo:
            box = pygame.Rect(ANCHO//2 - 150, 440, 300, 40)
            pygame.draw.rect(ventana, (40, 40, 40), box, border_radius=5)
            pygame.draw.rect(ventana, BLANCO, box, 1, border_radius=5)
            ventana.blit(fuente.render(texto_chat, True, BLANCO), (box.x + 10, box.y + 7))

        # HUD (Stats)
        pygame.draw.rect(ventana, (0,0,0,150), (20, 20, 280, 140), border_radius=10)
        ventana.blit(fuente.render(f"Nombre: {pet.nombre}", True, AMARILLO), (35, 30))
        for i, (lab, val, col) in enumerate([("Hambre", pet.hambre, ROJO), ("Energía", pet.energia, AMARILLO), ("Ánimo", pet.felicidad, VERDE)]):
            y_p = 65 + (i * 30)
            ventana.blit(fuente.render(lab, True, BLANCO), (35, y_p))
            pygame.draw.rect(ventana, (50,50,50), (130, y_p+5, 150, 12))
            pygame.draw.rect(ventana, col, (130, y_p+5, int(150 * (val/100)), 12))

        dibujar_boton(b_comer, "COMER", CELESTE); dibujar_boton(b_jugar, "JUGAR", VERDE)
        dibujar_boton(b_dormir, "DORMIR", (100, 100, 100)); dibujar_boton(b_volver, "VOLVER", ROJO)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and tipo == "loro" and not pet.durmiendo:
                if e.key == pygame.K_RETURN and texto_chat.strip() != "":
                    engine.say(texto_chat); engine.runAndWait(); texto_chat = ""
                elif e.key == pygame.K_BACKSPACE: texto_chat = texto_chat[:-1]
                else: texto_chat += e.unicode
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b_volver.collidepoint(e.pos):
                    if pet.durmiendo: pet.alternar_sueno()
                    guardar_partida(pet); return "MENU"
                if b_dormir.collidepoint(e.pos): pet.alternar_sueno()
                if b_comer.collidepoint(e.pos): pet.comer()
                if b_jugar.collidepoint(e.pos): pet.jugar()
        
        pygame.display.flip(); reloj.tick(60)

# --- 6. MENÚS (Se mantienen igual pero llaman a la nueva pantalla_juego) ---
def pedir_nombre(tipo):
    nombre = ""
    while True:
        ventana.fill(NEGRO)
        txt = fuente.render(f"NOMBRE PARA TU {tipo.upper()}", True, BLANCO)
        ventana.blit(txt, (ANCHO//2 - txt.get_width()//2, 200))
        box = pygame.Rect(ANCHO//2 - 150, 270, 300, 50)
        pygame.draw.rect(ventana, BLANCO, box, 2, border_radius=10)
        txt_n = fuente.render(nombre, True, AMARILLO); ventana.blit(txt_n, (box.x + 10, box.y + 12))
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and nombre.strip() != "":
                    if pantalla_juego(tipo, nombre) == "MENU": return
                elif e.key == pygame.K_BACKSPACE: nombre = nombre[:-1]
                else: 
                    if len(nombre) < 15 and e.unicode.isprintable(): nombre += e.unicode
        pygame.display.flip()

def seleccion_mascota():
    while True:
        ventana.fill(NEGRO)
        txt = fuente.render("ELIGE TU NUEVA MASCOTA", True, BLANCO)
        ventana.blit(txt, (ANCHO//2 - txt.get_width()//2, 150))
        b_g = pygame.Rect(100, 300, 180, 100); b_p = pygame.Rect(310, 300, 180, 100); b_l = pygame.Rect(520, 300, 180, 100)
        dibujar_boton(b_g, "GATO", CELESTE); dibujar_boton(b_p, "PERRO", VERDE); dibujar_boton(b_l, "LORO", AMARILLO)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b_g.collidepoint(e.pos): pedir_nombre("gato"); return
                if b_p.collidepoint(e.pos): pedir_nombre("perro"); return
                if b_l.collidepoint(e.pos): pedir_nombre("loro"); return
        pygame.display.flip()

def continuar_juego():
    bd = cargar_toda_la_bd()
    while True:
        ventana.fill(NEGRO)
        txt = fuente.render("ELIGE MASCOTA GUARDADA", True, BLANCO)
        ventana.blit(txt, (ANCHO//2 - txt.get_width()//2, 100))
        botones = []
        for i, (tipo, d) in enumerate(bd.items()):
            rect = pygame.Rect(ANCHO//2 - 150, 180 + (i*75), 300, 55)
            dibujar_boton(rect, f"{d['nombre']} ({tipo})", VERDE); botones.append((rect, tipo, d))
        b_atras = pygame.Rect(ANCHO//2 - 100, 500, 200, 50)
        dibujar_boton(b_atras, "ATRÁS", ROJO)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b_atras.collidepoint(e.pos): return
                for r, t, d in botones:
                    if r.collidepoint(e.pos):
                        pantalla_juego(t, d['nombre'], d['hambre'], d['energia'], d['felicidad']); return
        pygame.display.flip()

def menu_principal():
    while True:
        ventana.fill(NEGRO)
        txt_titulo = fuente.render("MASCOTA VIRTUAL", True, BLANCO)
        ventana.blit(txt_titulo, (ANCHO//2 - txt_titulo.get_width()//2, 130))
        b_nuevo = pygame.Rect(ANCHO//2-100, 230, 200, 60); b_continuar = pygame.Rect(ANCHO//2-100, 310, 200, 60); b_salir = pygame.Rect(ANCHO//2-100, 390, 200, 60)
        dibujar_boton(b_nuevo, "NUEVO JUEGO", VERDE)
        bd = cargar_toda_la_bd()
        dibujar_boton(b_continuar, "CONTINUAR", CELESTE if bd else (80,80,80))
        dibujar_boton(b_salir, "SALIR", ROJO)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b_nuevo.collidepoint(e.pos): seleccion_mascota()
                if b_continuar.collidepoint(e.pos) and bd: continuar_juego()
                if b_salir.collidepoint(e.pos): pygame.quit(); sys.exit()
        pygame.display.flip()

if __name__ == "__main__":
    menu_principal()
