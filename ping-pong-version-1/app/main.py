import pygame
import sys
import random

ANCHO, ALTO = 800, 600
FPS = 60

# --- 1. CLASE CANCHA ---
class Cancha:
    """Gestiona los estilos visuales de la arena y su renderizado."""
    def __init__(self):
        self.estilos = {
            "1": {"nombre": "CLÁSICO", "fondo": (25, 25, 25), "lineas": (255, 255, 255)},
            "2": {"nombre": "NEÓN", "fondo": (5, 5, 15), "lineas": (0, 255, 200)},
            "3": {"nombre": "DESIERTO", "fondo": (210, 180, 140), "lineas": (80, 40, 0)}
        }
        self.seleccionar_estilo("1")

    def seleccionar_estilo(self, tecla):
        estilo = self.estilos.get(tecla, self.estilos["1"])
        self.color_fondo = estilo["fondo"]
        self.color_lineas = estilo["lineas"]

    def dibujar(self, pantalla):
        pantalla.fill(self.color_fondo)
        for y in range(0, ALTO, 30):
            pygame.draw.rect(pantalla, self.color_lineas, (ANCHO//2 - 1, y, 2, 15))

# --- 2. CLASE PALETA ---
class Paleta:
    """Representa las paletas de los jugadores y su movimiento."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 15, 90)
        self.velocidad = 8

    def mover(self, arriba, abajo, teclas):
        if teclas[arriba] and self.rect.top > 0: self.rect.y -= self.velocidad
        if teclas[abajo] and self.rect.bottom < ALTO: self.rect.y += self.velocidad

    def dibujar(self, pantalla, color):
        pygame.draw.rect(pantalla, color, self.rect, border_radius=3)

# --- 3. CLASE PELOTA ---
class Pelota:
    """Controla la física de la pelota y su aceleración."""
    def __init__(self):
        self.rect = pygame.Rect(ANCHO//2, ALTO//2, 15, 15)
        self.reiniciar()

    def mover(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.top <= 0 or self.rect.bottom >= ALTO: self.vel_y *= -1

    def rebotar_paleta(self):
        # CAMBIO REALIZADO: Inversión de dirección con límite de velocidad (Max 15)
        # Esto evita que la pelota atraviese objetos por exceso de velocidad
        self.vel_x = max(min(self.vel_x * -1.1, 15), -15)
        self.vel_y = max(min(self.vel_y * 1.1, 15), -15)

    def reiniciar(self):
        self.rect.center = (ANCHO//2, ALTO//2)
        self.vel_x = 5 * random.choice((1, -1))
        self.vel_y = 5 * random.choice((1, -1))

    def dibujar(self, pantalla, color):
        pygame.draw.ellipse(pantalla, color, self.rect)

# --- 4. CLASE MARCADOR ---
class Marcador:
    """Gestiona puntos, sets y el renderizado del marcador."""
    def __init__(self):
        self.fuente = pygame.font.SysFont("Monospace", 30, bold=True)
        self.p1, self.p2, self.sets1, self.sets2 = 0, 0, 0, 0

    def anotar(self, jug):
        if jug == 1:
            self.p1 += 1
            if self.p1 >= 7: self.sets1 += 1; self.p1, self.p2 = 0, 0
        else:
            self.p2 += 1
            if self.p2 >= 7: self.sets2 += 1; self.p1, self.p2 = 0, 0

    def dibujar(self, pantalla, color):
        texto = f"SETS {self.sets1}-{self.sets2} | {self.p1}-{self.p2}"
        surf = self.fuente.render(texto, True, color)
        pantalla.blit(surf, (ANCHO//2 - surf.get_width()//2, 20))

# --- 5. CLASE JUEGO ---
class Juego:
    """Controlador principal de estados y navegación."""
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("PING PONG")
        self.reloj = pygame.time.Clock()
        self.fuente_tit = pygame.font.SysFont("Impact", 100)
        self.fuente_sub = pygame.font.SysFont("Arial", 25, bold=True)
        self.estado = "MENU"
        self.cancha = Cancha()
        self.reset_partida()

    def reset_partida(self):
        self.p1 = Paleta(20, ALTO//2-45)
        self.p2 = Paleta(ANCHO-35, ALTO//2-45)
        self.pelota = Pelota()
        self.marcador = Marcador()

    def mostrar_texto(self, t, f, c, x, y):
        surf = f.render(t, True, c)
        self.pantalla.blit(surf, (x - surf.get_width()//2, y))

    def menu_principal(self):
        self.pantalla.fill((15, 15, 20))
        self.mostrar_texto("PING PONG", self.fuente_tit, (255, 255, 255), ANCHO//2, 80)
        pygame.draw.rect(self.pantalla, (0, 255, 200), (ANCHO//2 - 180, 200, 360, 5))
        
        btn_jugar = pygame.Rect(ANCHO//2 - 130, 300, 260, 60)
        pygame.draw.rect(self.pantalla, (0, 255, 180), btn_jugar, border_radius=10)
        self.mostrar_texto("ENTER PARA JUGAR", self.fuente_sub, (0, 0, 0), ANCHO//2, 315)
        
        btn_salir = pygame.Rect(ANCHO//2 - 100, 480, 200, 45)
        pygame.draw.rect(self.pantalla, (200, 50, 50), btn_salir, border_radius=10)
        self.mostrar_texto("Q PARA SALIR", self.fuente_sub, (255, 255, 255), ANCHO//2, 490)
        
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN: self.estado = "SELECCION"
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

    def menu_seleccion(self):
        self.pantalla.fill((15, 15, 20))
        self.mostrar_texto("ELIJE TU ARENA", pygame.font.SysFont("Impact", 60), (255, 255, 255), ANCHO//2, 50)
        
        opciones = [("1", "CLÁSICO", (80, 80, 80)), ("2", "NEÓN", (0, 150, 150)), ("3", "DESIERTO", (160, 120, 60))]
        for i, (tecla, nombre, color) in enumerate(opciones):
            x_centro = 190 + (i * 210)
            rect = pygame.Rect(x_centro - 90, 180, 180, 220)
            pygame.draw.rect(self.pantalla, color, rect, border_radius=15)
            pygame.draw.rect(self.pantalla, (255, 255, 255), rect, 3, border_radius=15)
            
            num_surf = self.fuente_tit.render(tecla, True, (255, 255, 255))
            self.pantalla.blit(num_surf, (x_centro - num_surf.get_width()//2, 210))
            self.mostrar_texto(nombre, self.fuente_sub, (255, 255, 255), x_centro, 350)
        
        self.mostrar_texto("PRESIONA EL NÚMERO PARA EMPEZAR", self.fuente_sub, (0, 255, 200), ANCHO//2, 500)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    self.cancha.seleccionar_estilo(pygame.key.name(e.key))
                    self.estado = "JUGANDO"

    def menu_pausa(self):
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 180))
        self.pantalla.blit(overlay, (0,0))
        self.mostrar_texto("PAUSA", self.fuente_tit, (255, 255, 255), ANCHO//2, 120)
        pygame.draw.rect(self.pantalla, (0, 255, 200), (ANCHO//2 - 100, 230, 200, 5))
        
        opciones = ["[C] CONTINUAR", "[R] REINICIAR", "[M] MENÚ", "[Q] SALIR"]
        for i, texto in enumerate(opciones):
            self.mostrar_texto(texto, self.fuente_sub, (255, 255, 255), ANCHO//2, 300 + (i * 50))
            
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_c: self.estado = "JUGANDO"
                if e.key == pygame.K_r: self.reset_partida(); self.estado = "JUGANDO"
                if e.key == pygame.K_m: self.reset_partida(); self.estado = "MENU"
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

    def bucle_juego(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: self.estado = "PAUSA"
        
        teclas = pygame.key.get_pressed()
        self.p1.mover(pygame.K_w, pygame.K_s, teclas)
        self.p2.mover(pygame.K_UP, pygame.K_DOWN, teclas)
        self.pelota.mover()
        
        if self.pelota.rect.colliderect(self.p1.rect) or self.pelota.rect.colliderect(self.p2.rect):
            self.pelota.rebotar_paleta()
            
        if self.pelota.rect.left <= 0: self.marcador.anotar(2); self.pelota.reiniciar()
        if self.pelota.rect.right >= ANCHO: self.marcador.anotar(1); self.pelota.reiniciar()
        
        if self.marcador.sets1 == 2 or self.marcador.sets2 == 2: self.estado = "MENU"
        
        self.cancha.dibujar(self.pantalla)
        self.p1.dibujar(self.pantalla, self.cancha.color_lineas)
        self.p2.dibujar(self.pantalla, self.cancha.color_lineas)
        self.pelota.dibujar(self.pantalla, self.cancha.color_lineas)
        self.marcador.dibujar(self.pantalla, self.cancha.color_lineas)
        pygame.display.flip()

    def ejecutar(self):
        while True:
            if self.estado == "MENU": self.menu_principal()
            elif self.estado == "SELECCION": self.menu_seleccion()
            elif self.estado == "JUGANDO": self.bucle_juego()
            elif self.estado == "PAUSA": self.menu_pausa()
            self.reloj.tick(FPS)

if __name__ == "__main__":
    Juego().ejecutar()
