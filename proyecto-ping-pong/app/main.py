###### IMPORTS
import pygame
import sys
import random
import json

ANCHO = 800
ALTO = 600
FPS = 60

pygame.init()
pygame.mixer.init()
pygame.font.init()

###### FUNCIONES

def cargar_datos():
    try:
        with open("data.json", "r") as f:
            datos = json.load(f)
            return datos if "historial" in datos else {"historial": []}
    except: return {"historial": []}

def guardar_resultado(modo, ganador, puntos=None):
    datos = cargar_datos()
    entrada = f"{modo}: {ganador}" + (f" - {puntos} Pts" if puntos else "")
    datos["historial"].insert(0, entrada)
    datos["historial"] = datos["historial"][:5]
    with open("data.json", "w") as f: json.dump(datos, f, indent=4)

class Sonido:
    def __init__(self):
        self.canal_efectos = pygame.mixer.Channel(1)
        self.canal_habilidad = pygame.mixer.Channel(2)
    def reproducir_golpe(self):
        try: 
            snd = pygame.mixer.Sound("Golpeo.wav")
            self.canal_efectos.play(snd)
        except: pass
    def reproducir_poder(self):
        try: 
            snd = pygame.mixer.Sound("Habilidad.wav")
            self.canal_habilidad.play(snd)
        except: pass

class Habilidad:
    def __init__(self, fuente):
        self.rect = pygame.Rect(0, 0, 45, 45)
        self.activa_en_pantalla = False
        self.tipo_actual = None
        self.fuente = fuente

    def generar(self):
        if not self.activa_en_pantalla:
            self.rect.x = random.randint(100, ANCHO - 100)
            self.rect.y = random.randint(100, ALTO - 100)
            self.tipo_actual = random.choice(["IMAN", "ESCUDO", "X3", "VELOZ"])
            self.activa_en_pantalla = True

    def dibujar(self, pantalla):
        if self.activa_en_pantalla:
            color = (255, 255, 255)
            simbolo = ""
            if self.tipo_actual == "IMAN": color, simbolo = (255, 50, 50), "🧲"
            elif self.tipo_actual == "ESCUDO": color, simbolo = (0, 255, 255), "🛡️"
            elif self.tipo_actual == "VELOZ": color, simbolo = (255, 255, 0), "⚡"
            elif self.tipo_actual == "X3": color, simbolo = (50, 255, 50), "3️⃣"

            # Dibuja el recuadro (Asegúrate de haber cambiado el self.rect a 30x30 en el __init__ como querías)
            pygame.draw.rect(pantalla, color, self.rect, border_radius=6)
            pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2, border_radius=6)
            
            # Renderiza el emoji
            txt = self.fuente.render(simbolo, True, (0, 0, 0))
            
            # --- TRUCO AQUÍ ---
            # Si el emoji es más grande que el recuadro, lo encogemos a la fuerza
            margen = 8 # Espacio para que no toque los bordes del recuadro
            tamano_objetivo = self.rect.width - margen
            
            if txt.get_width() > tamano_objetivo or txt.get_height() > tamano_objetivo:
                txt = pygame.transform.smoothscale(txt, (tamano_objetivo, tamano_objetivo))
            # ------------------
            
            # Dibuja el emoji centrado
            pantalla.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))
            
class Pelota:
    def __init__(self, x=ANCHO//2, y=ALTO//2, vx=None, vy=None):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.radio = 8
        self.vel_x = vx if vx is not None else 5 * random.choice([1, -1])
        self.vel_y = vy if vy is not None else 5 * random.choice([1, -1])
    
    def reset(self):
        self.rect.center = (ANCHO//2, ALTO//2)
        self.vel_x = 5 * random.choice([1, -1])
        self.vel_y = 5 * random.choice([1, -1])

class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Ping Pong")
        self.reloj = pygame.time.Clock()
        
        self.fuente_pts = pygame.font.SysFont("Consolas", 40, bold=True)
        self.fuente_l = pygame.font.SysFont("Impact", 85)
        self.fuente_m = pygame.font.SysFont("Impact", 30)
        # Fuentes con soporte para emojis
        self.fuente_h = pygame.font.SysFont("segoe ui emoji, apple color emoji, noto color emoji, symbol", 8)
        
        self.audio = Sonido()
        self.habilidad = Habilidad(self.fuente_h)
        self.estado = "MENU"
        
        self.btn_cpu = pygame.Rect(ANCHO//2 - 150, 150, 300, 50)
        self.btn_multi = pygame.Rect(ANCHO//2 - 150, 220, 300, 50)
        self.btn_inf = pygame.Rect(ANCHO//2 - 150, 290, 300, 50)
        self.btn_salir = pygame.Rect(ANCHO//2 - 150, 360, 300, 50)

    def iniciar_juego(self, modo):
        self.modo_actual = modo
        self.pelotas = [Pelota()] 
        self.p1_y, self.p2_y = 250, 250
        self.pts1, self.pts2, self.sets1, self.sets2 = 0, 0, 0, 0
        self.vidas, self.ranking = 3, 0
        self.ultimo_t = pygame.time.get_ticks()
        self.poder_activo, self.escudo_activo = None, False
        self.estado = "JUGANDO"

    def bucle_juego(self):
        self.pantalla.fill((34, 139, 34)) 
        pygame.draw.aaline(self.pantalla, (255, 255, 255), (ANCHO//2, 0), (ANCHO//2, ALTO))
        ahora = pygame.time.get_ticks()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_p: self.menu_pausa()

        if self.poder_activo and ahora > self.timer_poder:
            self.poder_activo = None; self.escudo_activo = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.p1_y > 0: self.p1_y -= 7
        if keys[pygame.K_s] and self.p1_y < ALTO - 100: self.p1_y += 7
        
        if self.modo_actual == "MULTI":
            if keys[pygame.K_UP] and self.p2_y > 0: self.p2_y -= 7
            if keys[pygame.K_DOWN] and self.p2_y < ALTO - 100: self.p2_y += 7
        else:
            v_cpu = 4 if self.modo_actual == "CPU" else 6
            objetivo = self.pelotas[0].rect.centery if self.pelotas else ALTO//2
            if self.p2_y + 50 < objetivo: self.p2_y += v_cpu
            elif self.p2_y + 50 > objetivo: self.p2_y -= v_cpu

        if ahora - self.ultimo_t >= 10000: self.habilidad.generar(); self.ultimo_t = ahora

        r1, r2 = pygame.Rect(30, self.p1_y, 15, 100), pygame.Rect(ANCHO-45, self.p2_y, 15, 100)
        
        for p in self.pelotas[:]:
            if self.poder_activo == "IMAN" and p.vel_x < 0:
                p.vel_y += (self.p1_y + 50 - p.rect.centery) * 0.06

            p.rect.x += p.vel_x
            p.rect.y += p.vel_y

            if p.rect.top <= 0 or p.rect.bottom >= ALTO: p.vel_y *= -1
            if p.rect.colliderect(r1): p.vel_x = abs(p.vel_x)*1.05; self.audio.reproducir_golpe()
            if p.rect.colliderect(r2): p.vel_x = -abs(p.vel_x)*1.05; self.audio.reproducir_golpe()

            if self.habilidad.activa_en_pantalla and p.rect.colliderect(self.habilidad.rect):
                self.poder_activo = self.habilidad.tipo_actual
                self.timer_poder, self.habilidad.activa_en_pantalla = ahora + 6000, False
                self.audio.reproducir_poder()
                if self.poder_activo == "ESCUDO": self.escudo_activo = True
                elif self.poder_activo == "VELOZ": p.vel_x *= 1.8
                elif self.poder_activo == "X3":
                    self.pelotas.append(Pelota(p.rect.x, p.rect.y, p.vel_x, -p.vel_y))
                    self.pelotas.append(Pelota(p.rect.x, p.rect.y, -p.vel_x, p.vel_y))

            if self.escudo_activo and p.rect.left <= 10: p.vel_x = abs(p.vel_x); self.escudo_activo = False

            if p.rect.left <= 0:
                if len(self.pelotas) > 1: self.pelotas.remove(p)
                else:
                    if self.modo_actual == "INFINITO":
                        self.vidas -= 1
                        if self.vidas <= 0: self.mostrar_ganador(f"SCORE: {self.ranking}", "P1")
                    else:
                        self.pts2 += 1
                        if self.pts2 >= 7: self.sets2 += 1; self.pts1, self.pts2 = 0, 0
                        if self.sets2 >= 2: self.mostrar_ganador(f"GANÓ CPU", "CPU")
                    p.reset()
            elif p.rect.right >= ANCHO:
                if len(self.pelotas) > 1: self.pelotas.remove(p)
                else:
                    if self.modo_actual == "INFINITO": self.ranking += 10
                    else:
                        self.pts1 += 1
                        if self.pts1 >= 7: self.sets1 += 1; self.pts1, self.pts2 = 0, 0
                        if self.sets1 >= 2: self.mostrar_ganador("GANÓ P1", "P1")
                    p.reset()

        if self.escudo_activo: pygame.draw.rect(self.pantalla, (0, 255, 255), (5, 0, 10, ALTO))
        pygame.draw.rect(self.pantalla, (52, 152, 219), r1, border_radius=5) 
        pygame.draw.rect(self.pantalla, (255, 0, 255), r2, border_radius=5) 
        for p in self.pelotas: pygame.draw.circle(self.pantalla, (255, 255, 255), p.rect.center, p.radio)
        self.habilidad.dibujar(self.pantalla)
        
        # --- MARCADOR ---
        if self.modo_actual == "INFINITO":
            inf_txt = self.fuente_m.render(f"PUNTOS: {self.ranking}  VIDAS: {self.vidas}", True, (255,255,255))
            self.pantalla.blit(inf_txt, (ANCHO//2 - inf_txt.get_width()//2, 20))
        else:
            pygame.draw.rect(self.pantalla, (40,40,60), (ANCHO//2 - 90, 15, 180, 50), border_radius=10)
            p_txt = self.fuente_pts.render(f"{self.pts1} : {self.pts2}", True, (255,255,255))
            self.pantalla.blit(p_txt, (ANCHO//2 - p_txt.get_width()//2, 18))
            for i in range(2):
                pygame.draw.circle(self.pantalla, (0, 255, 0) if self.sets1 > i else (60,60,60), (ANCHO//2 - 115 - i*25, 40), 7)
                pygame.draw.circle(self.pantalla, (255, 0, 255) if self.sets2 > i else (60,60,60), (ANCHO//2 + 115 + i*25, 40), 7)

        pygame.display.flip()
        self.reloj.tick(FPS)

    def dibujar_boton(self, rect, texto, color):
        pygame.draw.rect(self.pantalla, color, rect, border_radius=8)
        t = self.fuente_m.render(texto, True, (255, 255, 255))
        self.pantalla.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))

    def menu_principal(self):
        self.pantalla.fill((15, 15, 25))
        logo = self.fuente_l.render("PING PONG", True, (0, 255, 255))
        self.pantalla.blit(logo, (ANCHO//2 - logo.get_width()//2, 40))
        self.dibujar_boton(self.btn_cpu, "VS CPU", (46, 204, 113))
        self.dibujar_boton(self.btn_multi, "MULTIJUGADOR", (52, 152, 219))
        self.dibujar_boton(self.btn_inf, "INFINITO", (241, 196, 15))
        self.dibujar_boton(self.btn_salir, "SALIR", (231, 76, 60))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_cpu.collidepoint(e.pos): self.iniciar_juego("CPU")
                elif self.btn_multi.collidepoint(e.pos): self.iniciar_juego("MULTI")
                elif self.btn_inf.collidepoint(e.pos): self.iniciar_juego("INFINITO")
                elif self.btn_salir.collidepoint(e.pos): pygame.quit(); sys.exit()

    def mostrar_ganador(self, texto, nombre):
        guardar_resultado(self.modo_actual, nombre, self.ranking if self.modo_actual == "INFINITO" else None)
        esp = True
        while esp:
            self.pantalla.fill((10, 10, 20))
            t = self.fuente_l.render(texto, True, (255, 215, 0))
            self.pantalla.blit(t, (ANCHO//2 - t.get_width()//2, 200))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN or e.type == pygame.QUIT: esp = False
        self.estado = "MENU"

    # --- MENU DE PAUSA ACTUALIZADO ---
    def menu_pausa(self):
        pausado = True
        btn_reanudar = pygame.Rect(ANCHO//2-120, ALTO//2-60, 240, 50)
        btn_salir = pygame.Rect(ANCHO//2-120, ALTO//2+10, 240, 50)
        
        while pausado:
            # Fondo semitransparente oscuro
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 10)) 
            self.pantalla.blit(overlay, (0,0))
            
            self.dibujar_boton(btn_reanudar, "REANUDAR", (52, 152, 219))
            self.dibujar_boton(btn_salir, "SALIR", (231, 76, 60))
            
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if btn_reanudar.collidepoint(e.pos): 
                        pausado = False
                    if btn_salir.collidepoint(e.pos):
                        self.estado = "MENU"
                        pausado = False
                # Permite quitar la pausa pulsando la misma tecla
                if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                    pausado = False
                if e.type == pygame.QUIT: 
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    g = Juego()
    while True:
        if g.estado == "MENU": g.menu_principal()
        else: g.bucle_juego()
